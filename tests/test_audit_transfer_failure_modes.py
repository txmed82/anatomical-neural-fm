from collections import Counter
from pathlib import Path

import pytest

from scripts.audit_shared_parent_broadening import RegionSignal
from scripts.audit_transfer_failure_modes import (
    baseline_auc,
    controlled_result_lookup,
    shared_parent_panel,
    weighted_signal_alignment,
)
from scripts.audit_csh_zad_019_signal import ResultRow


def test_controlled_result_lookup_reads_multiple_result_docs(tmp_path: Path) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text(
        "\n".join([
            "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
            "|---|---|---|---|---|---|",
            "| CSH_ZAD_019 | region_only | 3 | 0.544 | +0.038 | +0.014,+0.045,+0.056 |",
        ])
    )
    second.write_text(
        "\n".join([
            "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
            "|---|---|---|---|---|---|",
            "| NR_0019 | region_shuffle | 3 | 0.509 | +0.003 | +0.007,+0.013,-0.010 |",
        ])
    )

    rows = controlled_result_lookup([first, second])

    assert rows[("CSH_ZAD_019", "region_only")].mean_delta == 0.038
    assert rows[("NR_0019", "region_shuffle")].seed_deltas == (0.007, 0.013, -0.010)


def test_shared_parent_panel_compares_holdout_to_training_subjects() -> None:
    counts = {
        "heldout": Counter({"A": 3, "B": 2, "C": 1}),
        "train1": Counter({"A": 5}),
        "train2": Counter({"C": 4, "D": 2}),
    }

    assert shared_parent_panel("heldout", counts) == {"A", "C"}


def test_weighted_signal_alignment_uses_min_unit_weights() -> None:
    counts = {
        "ref": Counter({"A": 10, "B": 2}),
        "candidate": Counter({"A": 5, "B": 20}),
    }
    signals = {
        "ref": {
            "A": RegionSignal(units=10, left_trials=1, right_trials=1, left_rate=0.0, right_rate=1.0),
            "B": RegionSignal(units=2, left_trials=1, right_trials=1, left_rate=1.0, right_rate=0.0),
        },
        "candidate": {
            "A": RegionSignal(units=5, left_trials=1, right_trials=1, left_rate=0.0, right_rate=2.0),
            "B": RegionSignal(units=20, left_trials=1, right_trials=1, left_rate=2.0, right_rate=0.0),
        },
    }

    alignment = weighted_signal_alignment("ref", "candidate", counts, signals)

    assert alignment.weighted_corr == pytest.approx(1.0)
    assert alignment.same_sign_mass_frac == 1.0


def test_baseline_auc_recovers_shared_null_auc() -> None:
    row = ResultRow("source", "NR_0019", "region_only", 3, 0.498, -0.008, (-0.004, 0.014, -0.033))

    assert baseline_auc(row) == 0.506
    assert baseline_auc(None) is None
