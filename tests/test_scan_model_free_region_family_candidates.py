import numpy as np

from scripts.scan_model_free_region_family_candidates import (
    aggregate_features,
    present_family_definitions,
)


def test_present_family_definitions_filters_missing_regions() -> None:
    families = present_family_definitions(["CA", "DG", "VISp", "void"])

    assert families["hippocampal_formation"] == ("CA", "DG")
    assert families["cortical_visual"] == ("VISp",)
    assert "fiber_tracts" not in families


def test_aggregate_features_sums_family_members() -> None:
    regions = ["CA", "DG", "VISp"]
    families = {
        "hipp": ("CA", "DG"),
        "visual": ("VISp",),
    }
    features = np.asarray([
        [1.0, 2.0, 3.0],
        [0.0, 4.0, 5.0],
    ], dtype=np.float32)

    out = aggregate_features(features, regions, families)

    np.testing.assert_allclose(out, np.asarray([
        [3.0, 3.0],
        [4.0, 5.0],
    ], dtype=np.float32))
