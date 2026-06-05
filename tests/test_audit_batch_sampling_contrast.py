from scripts.audit_batch_sampling_contrast import batch_contrast_summary


def test_recording_target_balanced_produces_rankable_pairs() -> None:
    trials = [
        ("rec_a", 0.0, 0.0),
        ("rec_a", 1.0, 1.0),
        ("rec_b", 0.0, 0.0),
        ("rec_b", 1.0, 1.0),
    ]

    summary = batch_contrast_summary(
        trials,
        batch_sampling="recording_target_balanced",
        batch_size=2,
        n_batches=20,
        seed=0,
    )

    assert summary["n_eligible_recordings"] == 2
    assert summary["rankable_batch_fraction"] == 1.0
    assert summary["same_recording_adjacent_pair_fraction"] == 1.0
    assert summary["mean_rankable_pairs_per_batch"] == 1.0


def test_uniform_sampling_reports_partial_recording_contrast() -> None:
    trials = [
        ("rec_a", 0.0, 0.0),
        ("rec_a", 1.0, 1.0),
        ("rec_b", 0.0, 0.0),
        ("rec_b", 1.0, 1.0),
    ]

    summary = batch_contrast_summary(
        trials,
        batch_sampling="uniform",
        batch_size=2,
        n_batches=100,
        seed=0,
    )

    assert 0.0 < summary["rankable_batch_fraction"] < 1.0
    assert 0.0 < summary["same_recording_adjacent_pair_fraction"] < 1.0
