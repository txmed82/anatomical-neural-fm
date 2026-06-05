import numpy as np
import pandas as pd

from scripts.audit_cell_type_prior_target_control_gate import (
    CELL_CLASS_GROUPS,
    load_region_group_priors,
    prior_matrix_for_regions,
    project_cell_type_features,
    subclass_group,
    summarize,
)


def test_subclass_group_maps_abc_suffixes_to_broad_classes() -> None:
    assert subclass_group("001 CLA-EPd-CTX Car3 Glut") == "glutamatergic"
    assert subclass_group("046 Vip Gaba") == "gabaergic"
    assert subclass_group("327 Oligo NN") == "non_neuronal"
    assert subclass_group("072 Dopa") == "modulatory"


def test_load_region_group_priors_sums_subclasses(tmp_path) -> None:
    path = tmp_path / "priors.parquet"
    pd.DataFrame({
        "region_acronym": ["A", "A", "A", "B"],
        "subclass": ["001 X Glut", "002 Y Glut", "003 Z Gaba", "004 Astro NN"],
        "count": [1, 1, 1, 1],
        "proportion": [0.2, 0.3, 0.5, 1.0],
    }).to_parquet(path, index=False)

    priors = load_region_group_priors(path)

    row = priors[(priors["region_acronym"] == "A") & (priors["group"] == "glutamatergic")].iloc[0]
    assert row["proportion"] == 0.5


def test_prior_matrix_for_regions_reports_missing_regions() -> None:
    priors = pd.DataFrame({
        "region_acronym": ["A", "A", "B"],
        "group": ["glutamatergic", "gabaergic", "non_neuronal"],
        "proportion": [0.25, 0.75, 1.0],
    })

    matrix, coverage = prior_matrix_for_regions(["A", "B", "C"], priors, CELL_CLASS_GROUPS)

    assert matrix.shape == (3, 4)
    assert matrix[0, CELL_CLASS_GROUPS.index("glutamatergic")] == 0.25
    assert matrix[0, CELL_CLASS_GROUPS.index("gabaergic")] == 0.75
    assert matrix[1, CELL_CLASS_GROUPS.index("non_neuronal")] == 1.0
    assert coverage["n_regions_with_priors"] == 2
    assert coverage["regions_without_priors"] == ["C"]


def test_project_cell_type_features_multiplies_region_counts_by_priors() -> None:
    region_features = np.asarray([[2.0, 1.0], [0.0, 3.0]], dtype=np.float32)
    prior_matrix = np.asarray([[0.25, 0.75], [1.0, 0.0]], dtype=np.float32)

    out = project_cell_type_features(region_features, prior_matrix)

    np.testing.assert_allclose(out, [[1.5, 1.5], [3.0, 0.0]])


def test_summarize_marks_cell_type_candidate_decision() -> None:
    rows = [{
        "target_mode": "choice",
        "family": "gabaergic",
        "holdout": "S1",
        "decision": "candidate",
        "centered_delta_vs_shuffle": 0.1,
        "target0_improved_vs_shuffle": 0.6,
        "target1_improved_vs_shuffle": 0.6,
        "n_bidirectional_recordings": 3,
        "bidirectional_recording_fraction": 0.75,
    }]

    summary = summarize(rows, [{"n_regions_with_priors": 2, "n_regions_without_priors": 1, "regions_without_priors": ["X"]}])

    assert summary["decision"] == "cell_type_prior_target_candidate"
    assert summary["prior_coverage"]["max_regions_without_priors"] == 1
