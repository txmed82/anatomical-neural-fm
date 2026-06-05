import numpy as np

from scripts.audit_model_free_family_bidirectional_gate import aggregate_unit_fraction_map


def test_aggregate_unit_fraction_map_sums_parent_members() -> None:
    unit_fractions = {
        "rec-a": np.asarray([0.2, 0.3, 0.5], dtype=np.float32),
        "rec-b": np.asarray([0.5, 0.0, 0.5], dtype=np.float32),
    }
    families = {
        "first_two": ("A", "B"),
        "last": ("C",),
    }

    out = aggregate_unit_fraction_map(
        unit_fractions,
        regions=["A", "B", "C"],
        families=families,
    )

    assert np.allclose(out["rec-a"], [0.5, 0.5])
    assert np.allclose(out["rec-b"], [0.5, 0.5])
