from __future__ import annotations

import numpy as np
import torch

from scripts.train import (
    apply_region_label_control,
    best_metric_initial_value,
    build_inputs_for_window,
    build_trial_samples,
    is_better_metric,
    manifest_recording_ids,
    metrics_from_prediction_rows,
    parse_region_include,
    region_acronym_at_granularity,
    region_index_lookup,
    select_recording_ids,
    shared_split_regions,
    write_region_embeddings,
)


class Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_manifest_recording_ids_use_session_probe_stems(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        """
        {
          "recordings": [
            {"session_id": "eid-a", "probe_name": "probe00"},
            {"eid": "eid-b", "probe": "probe01"}
          ]
        }
        """
    )

    assert manifest_recording_ids(manifest) == ["eid-a_probe00", "eid-b_probe01"]


def test_select_recording_ids_filters_to_manifest_order(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        """
        {"recordings": [
          {"session_id": "eid-b", "probe_name": "probe01"},
          {"session_id": "eid-a", "probe_name": "probe00"}
        ]}
        """
    )
    ds = Obj(recording_ids=["extra", "eid-a_probe00", "eid-b_probe01"])

    assert select_recording_ids(ds, manifest, tmp_path) == ["eid-b_probe01", "eid-a_probe00"]


def test_region_label_shuffle_preserves_distribution_but_changes_assignments() -> None:
    vocab = {
        "region_idx_per_unit": np.arange(20, dtype=np.int64),
        "region_acronyms": np.array([f"R{i}" for i in range(20)]),
        "cell_type_region_acronyms": np.array([f"F{i}" for i in range(20)]),
        "other": object(),
    }

    shuffled = apply_region_label_control(vocab, "shuffle", seed=3)

    assert shuffled["other"] is vocab["other"]
    assert sorted(shuffled["region_idx_per_unit"].tolist()) == list(range(20))
    assert sorted(shuffled["region_acronyms"].tolist()) == sorted(f"R{i}" for i in range(20))
    assert sorted(shuffled["cell_type_region_acronyms"].tolist()) == sorted(f"F{i}" for i in range(20))
    assert shuffled["region_idx_per_unit"].tolist() != vocab["region_idx_per_unit"].tolist()


def test_build_trial_samples_choice_skips_nogo_and_nan_stim() -> None:
    rec = Obj(
        trials=Obj(
            choice=np.array([-1, 1, 0, 1]),
            stim_on_times=np.array([0.1, 0.2, 0.3, np.nan]),
        ),
        domain=Obj(end=np.array([2.0])),
    )

    samples = build_trial_samples({"rec": rec}, ["rec"], window_len=1.0, target_mode="choice")

    assert samples == [("rec", 0.1, 0.0), ("rec", 0.2, 1.0)]


def test_build_trial_samples_stimulus_side_uses_contrast_not_choice() -> None:
    rec = Obj(
        trials=Obj(
            choice=np.array([1, -1, 1, -1]),
            contrast_left=np.array([1.0, 0.0, 0.25, np.nan]),
            contrast_right=np.array([0.0, 1.0, 0.25, 0.5]),
            stim_on_times=np.array([0.1, 0.2, 0.3, 0.4]),
        ),
        domain=Obj(end=np.array([2.0])),
    )

    samples = build_trial_samples(
        {"rec": rec},
        ["rec"],
        window_len=1.0,
        target_mode="stimulus_side",
    )

    assert samples == [("rec", 0.1, 0.0), ("rec", 0.2, 1.0), ("rec", 0.4, 1.0)]


def test_shared_split_regions_uses_train_eval_intersection() -> None:
    recs = {
        "train": Obj(units=Obj(region_acronym=np.array(["VISp", "CA1", "CA1"]))),
        "eval": Obj(units=Obj(region_acronym=np.array(["CA1", "LP"]))),
    }

    assert shared_split_regions(recs, ["train"], ["eval"]) == {"CA1"}


def test_region_acronym_at_granularity_uses_allen_parent() -> None:
    assert region_acronym_at_granularity("SSp-bfd6a", "parent") == "SSp-bfd"
    assert region_acronym_at_granularity("PO", "parent") == "LAT"
    assert region_acronym_at_granularity("PO", "fine") == "PO"


def test_shared_split_regions_can_use_parent_granularity() -> None:
    recs = {
        "train": Obj(units=Obj(region_acronym=np.array(["PO"]))),
        "eval": Obj(units=Obj(region_acronym=np.array(["LP"]))),
    }

    assert shared_split_regions(recs, ["train"], ["eval"], region_granularity="fine") == set()
    assert shared_split_regions(recs, ["train"], ["eval"], region_granularity="parent") == {"LAT"}


def test_parse_region_include_splits_comma_separated_acronyms() -> None:
    assert parse_region_include("PRT, CA,VP,,") == {"PRT", "CA", "VP"}
    assert parse_region_include("") == set()


def test_build_inputs_for_window_filters_spikes_to_allowed_regions() -> None:
    class Tokenizer:
        def __call__(self, unit_ids):
            return list(range(len(unit_ids)))

    model = Obj(unit_emb=Obj(tokenizer=Tokenizer()), session_emb=Obj(tokenizer=Tokenizer()))
    sample = Obj(
        units=Obj(
            id=np.array(["u0", "u1", "u2"]),
            region_acronym=np.array(["CA1", "LP", "CA1"]),
        ),
        spikes=Obj(
            unit_index=np.array([0, 1, 2, 1]),
            timestamps=np.array([1.0, 1.1, 1.2, 1.3], dtype=np.float32),
        ),
    )
    args = Obj(
        window_len=1.0,
        latent_step=0.5,
        num_latents=1,
        output_query_mode="shared",
        region_granularity="fine",
    )

    out = build_inputs_for_window(
        model,
        sample,
        rid="rec",
        t0=1.0,
        args=args,
        allowed_region_acronyms={"CA1"},
    )

    assert out is not None
    assert out["input_unit_index"].tolist() == [0, 2]
    assert out["input_timestamps"].tolist() == [0.0, 0.20000004768371582]


def test_region_index_lookup_recovers_first_acronym_for_each_index() -> None:
    vocab = {
        "region_idx_per_unit": np.array([2, 0, 2, 1]),
        "region_acronyms": np.array(["DG", "CA", "DG-duplicate", "MOp"]),
    }

    assert region_index_lookup(vocab) == {0: "CA", 1: "MOp", 2: "DG"}


def test_write_region_embeddings_exports_labeled_vectors(tmp_path) -> None:
    model = Obj(region_emb=torch.nn.Embedding(3, 2))
    with torch.no_grad():
        model.region_emb.weight.copy_(torch.tensor([[1.0, 0.0], [0.0, 2.0], [3.0, 4.0]]))
    vocab = {
        "region_idx_per_unit": np.array([2, 0]),
        "region_acronyms": np.array(["DG", "CA"]),
    }
    out = tmp_path / "region_embeddings.jsonl"

    rows = write_region_embeddings(model, vocab, out)

    lines = out.read_text().splitlines()
    assert rows == 2
    assert '"region": "CA"' in lines[0]
    assert '"embedding": [1.0, 0.0]' in lines[0]
    assert '"region": "DG"' in lines[1]
    assert '"norm": 5.0' in lines[1]


def test_metrics_from_prediction_rows_computes_full_eval_fields() -> None:
    rows = [
        {"target": 0, "prob": 0.1},
        {"target": 0, "prob": 0.2},
        {"target": 1, "prob": 0.8},
        {"target": 1, "prob": 0.9},
    ]

    metrics = metrics_from_prediction_rows(rows)

    assert metrics["full_eval_n"] == 4
    assert metrics["full_eval_n_pos"] == 2
    assert metrics["full_eval_n_neg"] == 2
    assert metrics["full_eval_acc"] == 1.0
    assert metrics["full_eval_auc"] == 1.0


def test_best_metric_helpers_support_loss_and_auc() -> None:
    assert best_metric_initial_value("eval_loss") == float("inf")
    assert best_metric_initial_value("eval_auc") == -float("inf")
    assert is_better_metric("eval_loss", 0.4, 0.5)
    assert not is_better_metric("eval_loss", 0.6, 0.5)
    assert is_better_metric("eval_auc", 0.6, 0.5)
    assert not is_better_metric("eval_auc", 0.4, 0.5)
    assert not is_better_metric("eval_auc", float("nan"), 0.5)
