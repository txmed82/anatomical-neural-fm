import numpy as np

from scripts.audit_shared_family_near_miss import (
    recording_interpretation,
    target_feature_contrast,
)


def test_target_feature_contrast_reports_target1_minus_target0() -> None:
    features = np.asarray([1.0, 3.0, 10.0, 14.0])
    labels = np.asarray([0, 0, 1, 1])

    contrast = target_feature_contrast(features, labels)

    assert contrast["target0_mean"] == 2.0
    assert contrast["target1_mean"] == 12.0
    assert contrast["target1_minus_target0"] == 10.0


def test_recording_interpretation_separates_one_sided_effects() -> None:
    assert recording_interpretation(
        {"target0_improved": 0.60, "target1_improved": 0.61},
        min_target_improvement=0.55,
    ) == "bidirectional"
    assert recording_interpretation(
        {"target0_improved": 0.40, "target1_improved": 0.61},
        min_target_improvement=0.55,
    ) == "target1_only"
