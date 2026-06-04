from pathlib import Path

from scripts.audit_csh_zad_019_signal import (
    ResultRow,
    result_to_json,
    combine_rows,
    parse_lso_rows,
    parse_manual_delta_rows,
    parse_split_diagnostic_from_audit,
    parse_split_diagnostics,
)


def test_parse_lso_rows_reads_standard_summary_table(tmp_path: Path) -> None:
    path = tmp_path / "results.md"
    path.write_text(
        "\n".join([
            "| holdout | arm | n_seeds | mean_AUC | mean_delta_vs_shared | seed_deltas |",
            "|---|---|---|---|---|---|",
            "| CSH_ZAD_019 | region_only | 3 | 0.544 | +0.038 | +0.014,+0.045,+0.056 |",
        ])
    )

    assert parse_lso_rows(path, "source") == [
        ResultRow("source", "CSH_ZAD_019", "region_only", 3, 0.544, 0.038, (0.014, 0.045, 0.056)),
    ]


def test_parse_manual_delta_rows_reads_recovered_table(tmp_path: Path) -> None:
    path = tmp_path / "manual.md"
    path.write_text(
        "\n".join([
            "| holdout | arm | n_pairs | mean_delta | seed_deltas |",
            "|---|---|---|---|---|",
            "| CSH_ZAD_019 | region_only | 1 | +0.029 | +0.029 |",
        ])
    )

    assert parse_manual_delta_rows(path, "seed0") == [
        ResultRow("seed0", "CSH_ZAD_019", "region_only", 1, None, 0.029, (0.029,)),
    ]


def test_combine_rows_averages_seed_deltas() -> None:
    rows = [
        ResultRow("a", "CSH_ZAD_019", "region_only", 1, None, 0.029, (0.029,)),
        ResultRow("b", "CSH_ZAD_019", "region_only", 2, 0.537, 0.049, (0.054, 0.044)),
    ]

    combined = combine_rows(rows, source="combined", holdout="CSH_ZAD_019", arm="region_only")

    assert combined == ResultRow(
        "combined",
        "CSH_ZAD_019",
        "region_only",
        3,
        0.537,
        (0.029 + 0.054 + 0.044) / 3,
        (0.029, 0.054, 0.044),
    )


def test_result_to_json_counts_positive_seeds() -> None:
    row = ResultRow("control", "CSH_ZAD_019", "region_shuffle", 3, 0.494, -0.012, (-0.008, -0.030, 0.003))

    assert result_to_json(row) == {
        "source": "control",
        "holdout": "CSH_ZAD_019",
        "arm": "region_shuffle",
        "n_seeds": 3,
        "mean_auc": 0.494,
        "mean_delta_vs_shared": -0.012,
        "seed_deltas": [-0.008, -0.030, 0.003],
        "positive_seeds": 1,
    }


def test_parse_split_diagnostics_filters_holdout(tmp_path: Path) -> None:
    path = tmp_path / "log.txt"
    path.write_text(
        '{"event":"split","holdout_subjects":["CSH_ZAD_019"],'
        '"train_subjects":["S1"],"eval_subjects":["CSH_ZAD_019"],'
        '"region_filter":"shared_regions","region_granularity":"parent",'
        '"n_allowed_regions":2,"allowed_regions":["A","B"],'
        '"n_train_trials":10,"n_eval_trials":4,'
        '"train_class_balance":{"L":5,"R":5},'
        '"eval_class_balance":{"L":3,"R":1}}\n'
    )

    diagnostics = parse_split_diagnostics(path, "CSH_ZAD_019")

    assert len(diagnostics) == 1
    assert diagnostics[0].n_allowed_regions == 2
    assert diagnostics[0].allowed_regions == ("A", "B")
    assert diagnostics[0].eval_class_balance == {"L": 3, "R": 1}


def test_parse_split_diagnostic_from_audit_doc(tmp_path: Path) -> None:
    path = tmp_path / "audit.md"
    path.write_text(
        "\n".join([
            "## Shared-Parent Split Diagnostic",
            "",
            "| train_subjects | eval_subjects | train_trials | eval_trials | train_balance | eval_balance |",
            "|---|---|---:|---:|---|---|",
            "| S1, S2 | CSH_ZAD_019 | 10 | 4 | {'L': 5, 'R': 5} | {'L': 3, 'R': 1} |",
            "",
            "Allowed parent regions:",
            "",
            "`A`, `B`",
            "",
            "## Evidence Ladder",
        ])
    )

    diagnostic = parse_split_diagnostic_from_audit(path, "CSH_ZAD_019")

    assert diagnostic is not None
    assert diagnostic.n_allowed_regions == 2
    assert diagnostic.allowed_regions == ("A", "B")
    assert diagnostic.train_subjects == ("S1", "S2")
