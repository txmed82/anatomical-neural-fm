from types import SimpleNamespace

import numpy as np

from scripts.audit_lateralized_family_target_gate import (
    recording_unit_lateralized_cols,
    summarize,
    unit_hemisphere,
)
from tests.test_audit_shared_family_target_control_gate import base_row


def test_unit_hemisphere_splits_mlapdv_ml_coordinate() -> None:
    mlapdv = np.asarray([
        [-1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [np.nan, 0.0, 0.0],
    ])

    assert unit_hemisphere(mlapdv).tolist() == [0, 0, 1, -1]


def test_recording_unit_lateralized_cols_assigns_family_side_columns() -> None:
    rec = SimpleNamespace(
        units=SimpleNamespace(
            region_acronym=np.asarray(["VISp", "CA", "VISp", "CA"]),
            mlapdv=np.asarray([
                [-1.0, 0.0, 0.0],
                [-1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
            ]),
        )
    )

    cols = recording_unit_lateralized_cols(
        rec,
        families={"visual": ("VISp",), "hippocampal": ("CA",)},
        family_names=["visual", "hippocampal"],
        region_granularity="fine",
        region_control="none",
        recording_id="r1",
        seed=0,
    )

    assert cols == [[0], [2], [1], [3]]


def test_summarize_lateralized_candidates_keep_gpu_trigger_false() -> None:
    summary = summarize([base_row(decision="candidate", n_recordings=4)])

    assert summary["n_candidates"] == 1
    assert summary["decision"] == "lateralized_family_target_candidate"
    assert not summary["gpu_training_ready"]
