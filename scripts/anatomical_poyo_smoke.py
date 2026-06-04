"""Prototype `AnatomicalPOYO` and verify the five architecture-level ablation arms.

Arms (per-unit input embedding):
  (a) baseline           token = unit_emb
  (b) +region            token = unit_emb + region_emb(region(unit))
  (c) +cell-type         token = unit_emb + (props(unit) @ cell_type_proj)
  (e) +region +cell-type  token = unit_emb + region_emb + cell_type_proj
  (d) pure-anatomy       token = region_emb + cell_type_proj       (no unit_emb)

The +token_type_emb is always added. Cell-type priors come from the ABC Atlas
table at `data/cell_type_priors/region_subclass_priors.parquet`; a few IBL
regions may not match (zero vector for them, logged at registration time).

This script asserts all five arms produce DISTINCT outputs on the same fixture —
confirming each conditioning channel is genuinely in the gradient path.
"""
from __future__ import annotations

import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from torch_brain.dataset import Dataset, DatasetIndex  # noqa: E402
from torch_brain.models.poyo import POYO  # noqa: E402
from torch_brain.registry import DataType, ModalitySpec  # noqa: E402
from torch_brain.utils import create_linspace_latent_tokens  # noqa: E402

PRIORS_PATH = REPO_ROOT / "data" / "cell_type_priors" / "region_subclass_priors.parquet"
TAXONOMY_PATH = REPO_ROOT / "data" / "cell_type_priors" / "subclass_taxonomy.parquet"


def _resolve_acronyms_with_fallback(acronyms, available):
    """For each IBL acronym, return it if it's in `available`; otherwise walk up
    the Allen ontology to find the closest ancestor that is. None if unresolvable.
    """
    from iblatlas.regions import BrainRegions
    br = BrainRegions()
    resolution: dict[str, str | None] = {}
    for acr in acronyms:
        if acr in available:
            resolution[acr] = acr
            continue
        try:
            ids = br.acronym2id(acr)
        except Exception:
            resolution[acr] = None
            continue
        ids = np.atleast_1d(ids)
        if len(ids) == 0:
            resolution[acr] = None
            continue
        region_id = int(ids[0])
        # `ancestors` returns a Bunch with arrays of (id, acronym, name, ...);
        # in iblatlas it's ordered root → leaf, so reverse for closest-first.
        try:
            anc = br.ancestors(np.array([region_id]))
        except Exception:
            resolution[acr] = None
            continue
        if hasattr(anc, "acronym"):
            anc_list = list(anc.acronym)
        elif isinstance(anc, dict) and "acronym" in anc:
            anc_list = list(anc["acronym"])
        else:
            resolution[acr] = None
            continue
        match = None
        for a in reversed(anc_list):
            if a != acr and a in available:
                match = a
                break
        resolution[acr] = match
    return resolution


class AnatomicalPOYO(POYO):
    """POYO with optional anatomical conditioning.

    Conditioning is keyed off the per-unit anatomy lookup, registered after
    `unit_emb.initialize_vocab(...)` via `register_unit_anatomy(unit_ids, region_idx)`.

    Args:
        use_unit_emb: include the standard per-unit-id embedding (False = pure anatomy).
        use_region_emb: add a region embedding keyed by per-unit CCF region.
        n_regions: vocab size for region_emb (will be set to len(unique_region_ids)).
    """

    def __init__(
        self,
        *,
        use_unit_emb: bool = True,
        use_region_emb: bool = False,
        use_cell_type_emb: bool = False,
        use_waveform_emb: bool = False,
        n_regions: int = 2000,
        n_cell_types: int = 0,
        n_waveform_features: int = 3,
        emb_init_scale: float = 0.02,
        **poyo_kwargs,
    ):
        super().__init__(emb_init_scale=emb_init_scale, **poyo_kwargs)
        self.use_unit_emb = use_unit_emb
        self.use_region_emb = use_region_emb
        self.use_cell_type_emb = use_cell_type_emb
        self.use_waveform_emb = use_waveform_emb

        if use_region_emb:
            self.region_emb = nn.Embedding(n_regions + 1, self.dim)
            nn.init.normal_(self.region_emb.weight, std=emb_init_scale)
            self._unknown_region_idx = n_regions
        else:
            self.region_emb = None
            self._unknown_region_idx = 0

        if use_cell_type_emb:
            assert n_cell_types > 0, "n_cell_types required when use_cell_type_emb=True"
            self.cell_type_proj = nn.Linear(n_cell_types, self.dim, bias=False)
            nn.init.normal_(self.cell_type_proj.weight, std=emb_init_scale)
        else:
            self.cell_type_proj = None

        if use_waveform_emb:
            # 2-layer MLP: K_features → hidden → dim. Slightly more capacity than
            # a single Linear so the model can learn nonlinear waveform→type mappings.
            self.waveform_proj = nn.Sequential(
                nn.Linear(n_waveform_features, self.dim),
                nn.GELU(),
                nn.Linear(self.dim, self.dim),
            )
            for m in self.waveform_proj.modules():
                if isinstance(m, nn.Linear):
                    nn.init.normal_(m.weight, std=emb_init_scale)
                    nn.init.zeros_(m.bias)
        else:
            self.waveform_proj = None

        # vocab_idx -> region_idx
        self.register_buffer(
            "unit_to_region",
            torch.full((1,), self._unknown_region_idx, dtype=torch.long),
            persistent=False,
        )
        # vocab_idx -> cell_type_proportions (K-dim distribution, may be all-zero for unknown)
        self.register_buffer(
            "unit_to_cell_type_proportions",
            torch.zeros((1, max(n_cell_types, 1)), dtype=torch.float32),
            persistent=False,
        )
        # vocab_idx -> z-scored waveform feature vector
        self.register_buffer(
            "unit_to_waveform_features",
            torch.zeros((1, n_waveform_features), dtype=torch.float32),
            persistent=False,
        )

    def register_unit_waveform_features(self, unit_ids, features: np.ndarray) -> None:
        """Build the vocab_idx → (F,) waveform feature buffer.

        features should be a (n_units, F) array of raw per-unit features. Z-scored
        internally across the whole population so the model sees zero-mean unit-variance
        inputs.
        """
        vocab_idx = np.asarray(self.unit_emb.tokenizer(list(unit_ids)), dtype=np.int64)
        features = np.asarray(features, dtype=np.float32)
        assert features.shape[0] == len(unit_ids), (features.shape, len(unit_ids))
        # z-score per feature
        mean = features.mean(axis=0, keepdims=True)
        std = features.std(axis=0, keepdims=True) + 1e-6
        z = (features - mean) / std
        size = int(vocab_idx.max()) + 1
        F = z.shape[1]
        table = torch.zeros((size, F), dtype=torch.float32)
        table[torch.from_numpy(vocab_idx)] = torch.from_numpy(z)
        self.unit_to_waveform_features = table

    def register_unit_anatomy(self, unit_ids, region_idx) -> None:
        """Build the vocab_idx → region_idx buffer. Call after unit_emb.initialize_vocab()."""
        vocab_idx = np.asarray(self.unit_emb.tokenizer(list(unit_ids)), dtype=np.int64)
        region_idx = np.asarray(region_idx, dtype=np.int64)
        assert vocab_idx.shape == region_idx.shape, (vocab_idx.shape, region_idx.shape)
        size = int(vocab_idx.max()) + 1
        table = torch.full((size,), self._unknown_region_idx, dtype=torch.long)
        table[torch.from_numpy(vocab_idx)] = torch.from_numpy(region_idx)
        self.unit_to_region = table

    def register_unit_cell_types(self, unit_ids, region_acronyms,
                                 priors_df: pd.DataFrame, taxonomy: list[str]) -> None:
        """Build the vocab_idx → (K,) cell-type-proportion buffer.

        Args:
            unit_ids: vocab-order unit id strings
            region_acronyms: parallel array of CCFv2020-style acronyms for each unit
            priors_df: long-form table with columns (region_acronym, subclass, proportion)
            taxonomy: ordered list of subclass names → defines the K dim
        """
        sc_to_idx = {sc: i for i, sc in enumerate(taxonomy)}
        K = len(taxonomy)
        region_to_vec: dict[str, np.ndarray] = {}
        for region, group in priors_df.groupby("region_acronym", observed=True):
            vec = np.zeros(K, dtype=np.float32)
            for row in group.itertuples(index=False):
                idx = sc_to_idx.get(row.subclass)
                if idx is not None:
                    vec[idx] = row.proportion
            region_to_vec[region] = vec

        # --- Hierarchical fallback: walk up Allen ontology for missing acronyms ---
        available = set(region_to_vec)
        unique_iberegions = sorted({str(r) for r in region_acronyms})
        resolution = _resolve_acronyms_with_fallback(unique_iberegions, available)

        n_direct = sum(1 for a in unique_iberegions if a in available)
        n_fallback = sum(1 for a in unique_iberegions if resolution.get(a) and resolution[a] != a)
        n_unmapped = sum(1 for a in unique_iberegions if resolution.get(a) is None)
        if n_fallback or n_unmapped:
            fb_lines = []
            for a in unique_iberegions:
                r = resolution.get(a)
                if r is None:
                    fb_lines.append(f"      {a} → UNKNOWN")
                elif r != a:
                    fb_lines.append(f"      {a} → {r} (ancestor)")
            print(f"    region resolution: {n_direct} direct, {n_fallback} via ancestor, {n_unmapped} unknown")
            for line in fb_lines:
                print(line)

        vocab_idx = np.asarray(self.unit_emb.tokenizer(list(unit_ids)), dtype=np.int64)
        size = int(vocab_idx.max()) + 1
        table = torch.zeros((size, K), dtype=torch.float32)
        n_missing = 0
        for vidx, region in zip(vocab_idx, region_acronyms):
            resolved = resolution.get(str(region))
            if resolved is None:
                n_missing += 1
                continue
            table[vidx] = torch.from_numpy(region_to_vec[resolved])
        coverage = 1 - n_missing / len(unit_ids)
        print(f"    final per-unit coverage: {coverage:.1%} ({len(unit_ids) - n_missing}/{len(unit_ids)})")
        self.unit_to_cell_type_proportions = table

    def forward(
        self,
        *,
        input_unit_index,
        input_timestamps,
        input_token_type,
        latent_index,
        latent_timestamps,
        output_session_index,
        output_timestamps,
        input_mask=None,
        output_mask=None,
        unpack_output: bool = False,
    ):
        # Vocab init checks (lifted from POYO.forward)
        if self.use_unit_emb and self.unit_emb.is_lazy():
            raise ValueError("unit_emb vocab not initialized")
        if self.session_emb.is_lazy():
            raise ValueError("session_emb vocab not initialized")

        # --- THE ONLY ARCHITECTURAL DIFFERENCE FROM POYO ---
        inputs = self.token_type_emb(input_token_type)
        if self.use_unit_emb:
            inputs = inputs + self.unit_emb(input_unit_index)
        if self.use_region_emb:
            region_idx = self.unit_to_region[input_unit_index]
            inputs = inputs + self.region_emb(region_idx)
        if self.use_cell_type_emb:
            props = self.unit_to_cell_type_proportions[input_unit_index]  # (B, T, K)
            inputs = inputs + self.cell_type_proj(props)
        if self.use_waveform_emb:
            wf = self.unit_to_waveform_features[input_unit_index]  # (B, T, F)
            inputs = inputs + self.waveform_proj(wf)
        # --- end diff ---

        input_timestamp_emb = self.rotary_emb(input_timestamps)
        latents = self.latent_emb(latent_index)
        latent_timestamp_emb = self.rotary_emb(latent_timestamps)
        output_queries = self.session_emb(output_session_index)
        output_timestamp_emb = self.rotary_emb(output_timestamps)

        latents = latents + self.enc_atn(
            latents, inputs, latent_timestamp_emb, input_timestamp_emb, input_mask,
        )
        latents = latents + self.enc_ffn(latents)

        for self_attn, self_ff in self.proc_layers:
            latents = latents + self.dropout(self_attn(latents, latent_timestamp_emb))
            latents = latents + self.dropout(self_ff(latents))

        output_queries = output_queries + self.dec_atn(
            output_queries, latents, output_timestamp_emb, latent_timestamp_emb,
        )
        output_latents = output_queries + self.dec_ffn(output_queries)
        output = self.readout(output_latents)

        if unpack_output:
            output = [output[b][output_mask[b]] for b in range(output.size(0))]
        return output


# --- Fixture: build inputs once, reuse across arms ---

def build_fixture():
    ds_dir = REPO_ROOT / "data" / "brainsets" / "ibl_bwm"
    ds = Dataset(dataset_dir=ds_dir, keep_files_open=True)
    rid = ds.recording_ids[0]
    rec = ds.get_recording(rid)
    unit_ids = rec.units.id.astype(str).tolist()
    session_id = str(rec.session.id)

    # Region info: contiguous region_idx (for region_emb) + acronyms (for cell-type lookup)
    region_ids_per_unit = np.asarray(rec.units.region_id, dtype=np.int64)
    region_acronyms_per_unit = np.asarray(rec.units.region_acronym).astype(str)
    unique_region_ids = np.unique(region_ids_per_unit)
    region_id_to_idx = {int(rid): i for i, rid in enumerate(unique_region_ids)}
    region_idx_per_unit = np.array([region_id_to_idx[int(r)] for r in region_ids_per_unit], dtype=np.int64)
    n_regions = len(unique_region_ids)
    print(f"  {len(unit_ids)} units across {n_regions} unique CCF regions")

    # Cell-type priors + taxonomy
    priors_df = pd.read_parquet(PRIORS_PATH)
    taxonomy = pd.read_parquet(TAXONOMY_PATH)["subclass"].tolist()
    n_cell_types = len(taxonomy)
    print(f"  cell-type taxonomy: {n_cell_types} subclasses; "
          f"prior table covers {priors_df['region_acronym'].nunique()} regions")

    # 1-second sample
    t0, t1 = 100.0, 101.0
    sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t1)]
    sample_unit_ids = sample.units.id.astype(str).tolist()

    return {
        "unit_ids": unit_ids,
        "session_id": session_id,
        "region_idx_per_unit": region_idx_per_unit,
        "region_acronyms_per_unit": region_acronyms_per_unit,
        "n_regions": n_regions,
        "priors_df": priors_df,
        "taxonomy": taxonomy,
        "n_cell_types": n_cell_types,
        "sample": sample,
        "sample_unit_ids": sample_unit_ids,
        "t0": t0,
        "t1": t1,
    }


def model_inputs_from(fixture, model):
    sample = fixture["sample"]
    t0 = fixture["t0"]
    local_to_global = np.array(
        model.unit_emb.tokenizer(fixture["sample_unit_ids"]), dtype=np.int64,
    )
    input_unit_index = local_to_global[sample.spikes.unit_index]
    input_timestamps = sample.spikes.timestamps.astype(np.float32) - t0
    input_token_type = np.zeros(len(input_timestamps), dtype=np.int64)
    latent_index, latent_timestamps = create_linspace_latent_tokens(
        start=0.0, end=1.0, step=0.125, num_latents_per_step=8,
    )
    n_query = 4
    output_session_index = np.full(
        n_query, model.session_emb.tokenizer([fixture["session_id"]])[0], dtype=np.int64,
    )
    output_timestamps = np.linspace(0.1, 0.9, n_query, dtype=np.float32)

    def t(x, dtype):
        return torch.as_tensor(x, dtype=dtype).unsqueeze(0)

    return {
        "input_unit_index": t(input_unit_index, torch.long),
        "input_timestamps": t(input_timestamps, torch.float32),
        "input_token_type": t(input_token_type, torch.long),
        "latent_index": t(latent_index, torch.long),
        "latent_timestamps": t(latent_timestamps, torch.float32),
        "output_session_index": t(output_session_index, torch.long),
        "output_timestamps": t(output_timestamps, torch.float32),
    }


def run_arm(name: str, fixture, *, use_unit_emb: bool, use_region_emb: bool,
            use_cell_type_emb: bool, seed: int):
    torch.manual_seed(seed)
    spec = ModalitySpec(
        id=1, dim=2, type=DataType.CONTINUOUS,
        timestamp_key="dummy.t", value_key="dummy.v",
        loss_fn=torch.nn.functional.mse_loss,
    )
    model = AnatomicalPOYO(
        use_unit_emb=use_unit_emb,
        use_region_emb=use_region_emb,
        use_cell_type_emb=use_cell_type_emb,
        n_regions=fixture["n_regions"],
        n_cell_types=fixture["n_cell_types"],
        sequence_length=1.0, latent_step=0.125,
        dim=32, depth=1, dim_head=16,
        num_latents_per_step=8, cross_heads=2, self_heads=4,
        ffn_dropout=0.0, lin_dropout=0.0, atn_dropout=0.0,
        readout_spec=spec,
    )
    model.unit_emb.initialize_vocab(fixture["unit_ids"])
    model.session_emb.initialize_vocab([fixture["session_id"]])
    model.register_unit_anatomy(fixture["unit_ids"], fixture["region_idx_per_unit"])
    if use_cell_type_emb:
        model.register_unit_cell_types(
            fixture["unit_ids"],
            fixture["region_acronyms_per_unit"],
            fixture["priors_df"],
            fixture["taxonomy"],
        )
    n_params = sum(p.numel() for p in model.parameters())

    inputs = model_inputs_from(fixture, model)
    model.eval()
    with torch.no_grad():
        out = model(**inputs)

    model.train()
    out2 = model(**inputs)
    loss = torch.nn.functional.mse_loss(out2, torch.zeros_like(out2))
    loss.backward()
    grad_norm = sum(p.grad.norm().item() for p in model.parameters() if p.grad is not None)

    print(
        f"  {name:<14s}  params={n_params:>7,}  "
        f"out.mean={out.mean().item():+.4f}  out.std={out.std().item():.4f}  "
        f"loss={loss.item():.4f}  grad_norm={grad_norm:.2f}"
    )
    return out.detach().clone()


def main() -> int:
    print("Loading data + fixture...")
    fixture = build_fixture()

    print("\nRunning five architecture-level ablation arms (same seed, same inputs):")
    outs = {}
    outs["(a) baseline"] = run_arm(
        "(a) baseline", fixture,
        use_unit_emb=True, use_region_emb=False, use_cell_type_emb=False, seed=0,
    )
    outs["(b) +region"] = run_arm(
        "(b) +region", fixture,
        use_unit_emb=True, use_region_emb=True, use_cell_type_emb=False, seed=0,
    )
    outs["(c) +cell-type"] = run_arm(
        "(c) +cell-type", fixture,
        use_unit_emb=True, use_region_emb=False, use_cell_type_emb=True, seed=0,
    )
    outs["(e) +region+ctype"] = run_arm(
        "(e) +region+ctype", fixture,
        use_unit_emb=True, use_region_emb=True, use_cell_type_emb=True, seed=0,
    )
    outs["(d) pure-anatomy"] = run_arm(
        "(d) pure-anatomy", fixture,
        use_unit_emb=False, use_region_emb=True, use_cell_type_emb=True, seed=0,
    )

    # Pairwise mean-abs-diff — every pair must differ; otherwise some channel is silent.
    names = list(outs)
    print("\nPairwise mean abs diffs (all must be > 1e-6):")
    diffs = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = (outs[a] - outs[b]).abs().mean().item()
            diffs[(a, b)] = d
            print(f"  {a:<22s} vs {b:<22s} = {d:.4f}")

    bad = [pair for pair, d in diffs.items() if d <= 1e-6]
    if bad:
        for a, b in bad:
            print(f"FAIL: {a} and {b} produce identical outputs", file=sys.stderr)
        return 1

    print("\nAll five ablation arms produce distinct outputs — both region and cell-type "
          "conditioning are wired correctly into the gradient path.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
