from __future__ import annotations

import numpy as np

from scripts.train import (
    build_inputs_for_window,
    build_trial_samples,
    manifest_recording_ids,
    region_acronym_at_granularity,
    select_recording_ids,
    shared_split_regions,
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
