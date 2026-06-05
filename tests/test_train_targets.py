from __future__ import annotations

import numpy as np
import torch

from scripts.train import (
    apply_region_label_control,
    best_metric_initial_value,
    best_metric_requires_full_eval,
    build_inputs_for_window,
    build_trial_samples,
    center_logits_by_group,
    choose_recording_for_balanced_pair,
    choose_trial_index,
    is_better_metric,
    manifest_recording_ids,
    metrics_from_prediction_rows,
    parse_region_include,
    region_acronym_at_granularity,
    region_index_lookup,
    recording_pairwise_rank_loss,
    recording_centered_auc_from_prediction_rows,
    select_recording_ids,
    shared_split_regions,
    training_loss,
    trial_indices_by_recording_target,
    trial_indices_by_target,
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
        "unit_recording_ids": np.array(["a"] * 10 + ["b"] * 10),
        "other": object(),
    }

    shuffled = apply_region_label_control(vocab, "shuffle", seed=3)

    assert shuffled["other"] is vocab["other"]
    assert sorted(shuffled["region_idx_per_unit"].tolist()) == list(range(20))
    assert sorted(shuffled["region_acronyms"].tolist()) == sorted(f"R{i}" for i in range(20))
    assert sorted(shuffled["cell_type_region_acronyms"].tolist()) == sorted(f"F{i}" for i in range(20))
    assert shuffled["region_idx_per_unit"].tolist() != vocab["region_idx_per_unit"].tolist()


def test_within_recording_region_label_shuffle_preserves_recording_distribution() -> None:
    vocab = {
        "region_idx_per_unit": np.array([0, 1, 2, 3, 10, 11, 12, 13], dtype=np.int64),
        "region_acronyms": np.array(["A0", "A1", "A2", "A3", "B0", "B1", "B2", "B3"]),
        "cell_type_region_acronyms": np.array(["FA0", "FA1", "FA2", "FA3", "FB0", "FB1", "FB2", "FB3"]),
        "unit_recording_ids": np.array(["a", "a", "a", "a", "b", "b", "b", "b"]),
    }

    shuffled = apply_region_label_control(vocab, "within_recording_shuffle", seed=1)

    for recording_id in ("a", "b"):
        mask = vocab["unit_recording_ids"] == recording_id
        assert sorted(shuffled["region_idx_per_unit"][mask].tolist()) == sorted(
            vocab["region_idx_per_unit"][mask].tolist()
        )
        assert sorted(shuffled["region_acronyms"][mask].tolist()) == sorted(
            vocab["region_acronyms"][mask].tolist()
        )
    assert sorted(shuffled["region_idx_per_unit"][:4].tolist()) == [0, 1, 2, 3]
    assert sorted(shuffled["region_idx_per_unit"][4:].tolist()) == [10, 11, 12, 13]
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


def test_trial_indices_by_target_groups_binary_targets() -> None:
    trials = [
        ("a", 0.1, 0.0),
        ("a", 0.2, 1.0),
        ("b", 0.3, 1.0),
        ("b", 0.4, 0.0),
    ]

    assert trial_indices_by_target(trials) == {0: [0, 3], 1: [1, 2]}


def test_trial_indices_by_recording_target_groups_within_recording() -> None:
    trials = [
        ("a", 0.1, 0.0),
        ("a", 0.2, 1.0),
        ("b", 0.3, 1.0),
        ("b", 0.4, 0.0),
        ("b", 0.5, 1.0),
    ]

    assert trial_indices_by_recording_target(trials) == {
        "a": {0: [0], 1: [1]},
        "b": {0: [3], 1: [2, 4]},
    }


def test_target_balanced_trial_choice_alternates_requested_target() -> None:
    trials = [
        ("a", 0.1, 0.0),
        ("a", 0.2, 1.0),
        ("b", 0.3, 1.0),
        ("b", 0.4, 0.0),
    ]
    rng = np.random.default_rng(0)

    first = choose_trial_index(trials, rng, "target_balanced", accepted_count=0, target_offset=0)
    second = choose_trial_index(trials, rng, "target_balanced", accepted_count=1, target_offset=0)

    assert trials[first][2] == 0.0
    assert trials[second][2] == 1.0


def test_recording_target_balanced_choice_uses_requested_recording() -> None:
    trials = [
        ("a", 0.1, 0.0),
        ("a", 0.2, 1.0),
        ("b", 0.3, 1.0),
        ("b", 0.4, 0.0),
    ]
    rng = np.random.default_rng(0)

    first = choose_trial_index(
        trials,
        rng,
        "recording_target_balanced",
        accepted_count=0,
        target_offset=0,
        recording_id="b",
    )
    second = choose_trial_index(
        trials,
        rng,
        "recording_target_balanced",
        accepted_count=1,
        target_offset=0,
        recording_id="b",
    )

    assert trials[first][0] == "b"
    assert trials[first][2] == 0.0
    assert trials[second][0] == "b"
    assert trials[second][2] == 1.0


def test_choose_recording_for_balanced_pair_requires_both_targets() -> None:
    trials = [
        ("a", 0.1, 0.0),
        ("a", 0.2, 1.0),
        ("b", 0.3, 1.0),
    ]
    rng = np.random.default_rng(0)

    assert choose_recording_for_balanced_pair(trials, rng) == "a"


def test_target_balanced_trial_choice_falls_back_when_one_class_missing() -> None:
    trials = [("a", 0.1, 1.0), ("a", 0.2, 1.0)]
    rng = np.random.default_rng(0)

    idx = choose_trial_index(trials, rng, "target_balanced", accepted_count=0, target_offset=0)

    assert idx in {0, 1}


def test_center_logits_by_group_removes_group_offsets() -> None:
    logits = torch.tensor([[2.0], [4.0], [10.0], [14.0]])

    centered = center_logits_by_group(logits, ["a", "a", "b", "b"])

    assert torch.allclose(centered, torch.tensor([[-1.0], [1.0], [-2.0], [2.0]]))


def test_recording_centered_training_loss_ignores_recording_offsets() -> None:
    logits = torch.tensor([[2.0], [4.0], [10.0], [12.0]])
    shifted_logits = torch.tensor([[102.0], [104.0], [-30.0], [-28.0]])
    target = torch.tensor([[0.0], [1.0], [0.0], [1.0]])
    meta = {"recording_ids": ["a", "a", "b", "b"]}

    loss = training_loss(logits, target, "recording_centered_bce", meta)
    shifted_loss = training_loss(shifted_logits, target, "recording_centered_bce", meta)

    assert torch.allclose(loss, shifted_loss)


def test_recording_pairwise_rank_loss_ignores_recording_offsets() -> None:
    logits = torch.tensor([[1.0], [3.0], [10.0], [13.0]])
    shifted_logits = torch.tensor([[101.0], [103.0], [-30.0], [-27.0]])
    target = torch.tensor([[0.0], [1.0], [0.0], [1.0]])
    recording_ids = ["a", "a", "b", "b"]

    loss = recording_pairwise_rank_loss(logits, target, recording_ids)
    shifted_loss = recording_pairwise_rank_loss(shifted_logits, target, recording_ids)

    assert torch.allclose(loss, shifted_loss)


def test_recording_pairwise_rank_loss_prefers_positive_above_negative() -> None:
    good = torch.tensor([[0.0], [2.0]])
    bad = torch.tensor([[2.0], [0.0]])
    target = torch.tensor([[0.0], [1.0]])

    good_loss = recording_pairwise_rank_loss(good, target, ["a", "a"])
    bad_loss = recording_pairwise_rank_loss(bad, target, ["a", "a"])

    assert good_loss < bad_loss


def test_training_loss_supports_recording_pairwise_rank_mode() -> None:
    logits = torch.tensor([[0.0], [2.0]])
    target = torch.tensor([[0.0], [1.0]])
    meta = {"recording_ids": ["a", "a"]}

    loss = training_loss(logits, target, "recording_pairwise_rank", meta)

    assert torch.isfinite(loss)


def test_recording_local_auc_surrogate_alias_matches_pairwise_rank() -> None:
    logits = torch.tensor([[0.0], [2.0], [10.0], [13.0]])
    target = torch.tensor([[0.0], [1.0], [0.0], [1.0]])
    meta = {"recording_ids": ["a", "a", "b", "b"]}

    pairwise = training_loss(logits, target, "recording_pairwise_rank", meta)
    local_auc = training_loss(logits, target, "recording_local_auc_surrogate", meta)

    assert torch.allclose(pairwise, local_auc)


def test_pairwise_rank_centered_bce_loss_ignores_recording_offsets() -> None:
    logits = torch.tensor([[0.0], [2.0], [10.0], [13.0]])
    shifted_logits = torch.tensor([[100.0], [102.0], [-40.0], [-37.0]])
    target = torch.tensor([[0.0], [1.0], [0.0], [1.0]])
    meta = {"recording_ids": ["a", "a", "b", "b"]}

    loss = training_loss(logits, target, "recording_pairwise_rank_centered_bce", meta)
    shifted_loss = training_loss(shifted_logits, target, "recording_pairwise_rank_centered_bce", meta)

    assert torch.allclose(loss, shifted_loss)


def test_pairwise_rank_centered_bce_loss_prefers_good_ordering() -> None:
    good = torch.tensor([[0.0], [2.0]])
    bad = torch.tensor([[2.0], [0.0]])
    target = torch.tensor([[0.0], [1.0]])
    meta = {"recording_ids": ["a", "a"]}

    good_loss = training_loss(good, target, "recording_pairwise_rank_centered_bce", meta)
    bad_loss = training_loss(bad, target, "recording_pairwise_rank_centered_bce", meta)

    assert good_loss < bad_loss


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
    assert metrics["full_eval_centered_auc"] == 1.0


def test_best_metric_helpers_support_loss_and_auc() -> None:
    assert best_metric_initial_value("eval_loss") == float("inf")
    assert best_metric_initial_value("eval_auc") == -float("inf")
    assert best_metric_initial_value("full_eval_auc") == -float("inf")
    assert best_metric_initial_value("full_eval_centered_auc") == -float("inf")
    assert is_better_metric("eval_loss", 0.4, 0.5)
    assert not is_better_metric("eval_loss", 0.6, 0.5)
    assert is_better_metric("eval_auc", 0.6, 0.5)
    assert not is_better_metric("eval_auc", 0.4, 0.5)
    assert is_better_metric("full_eval_auc", 0.6, 0.5)
    assert is_better_metric("full_eval_centered_auc", 0.6, 0.5)
    assert not is_better_metric("eval_auc", float("nan"), 0.5)
    assert not best_metric_requires_full_eval("eval_auc")
    assert best_metric_requires_full_eval("full_eval_auc")
    assert best_metric_requires_full_eval("full_eval_centered_auc")


def test_recording_centered_auc_from_prediction_rows_removes_recording_offsets() -> None:
    rows = [
        {"recording_id": "a", "target": 0, "prob": 0.89},
        {"recording_id": "a", "target": 1, "prob": 0.91},
        {"recording_id": "b", "target": 0, "prob": 0.09},
        {"recording_id": "b", "target": 1, "prob": 0.11},
    ]

    assert recording_centered_auc_from_prediction_rows(rows) == 1.0
