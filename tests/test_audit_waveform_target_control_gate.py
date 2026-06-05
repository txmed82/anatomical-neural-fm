from types import SimpleNamespace

import numpy as np

from scripts.audit_waveform_target_control_gate import (
    make_waveform_feature_matrix,
    recording_waveform_features,
    summarize,
    transform_waveform_features,
)


class FakeDataset:
    def __init__(self, sample):
        self.sample = sample

    def __getitem__(self, _index):
        return self.sample


def fake_recording() -> SimpleNamespace:
    return SimpleNamespace(
        units=SimpleNamespace(
            amps=np.asarray([1.0, 2.0, 3.0], dtype=np.float32),
            depths=np.asarray([10.0, 20.0, 30.0], dtype=np.float32),
            peak_to_trough=np.asarray([0.1, 0.2, 0.3], dtype=np.float32),
        )
    )


def test_recording_waveform_features_zscores_within_recording() -> None:
    z = recording_waveform_features(fake_recording(), control="none", recording_id="r1", seed=0)

    np.testing.assert_allclose(z.mean(axis=0), [0.0, 0.0, 0.0], atol=1e-6)
    np.testing.assert_allclose(z.std(axis=0), [1.0, 1.0, 1.0], atol=1e-6)


def test_recording_waveform_shuffle_preserves_column_distribution() -> None:
    true = recording_waveform_features(fake_recording(), control="none", recording_id="r1", seed=0)
    shuffled = recording_waveform_features(fake_recording(), control="within_recording_shuffle", recording_id="r1", seed=0)

    for col in range(true.shape[1]):
        np.testing.assert_allclose(np.sort(shuffled[:, col]), np.sort(true[:, col]))


def test_make_waveform_feature_matrix_sums_spike_unit_features() -> None:
    sample = SimpleNamespace(
        spikes=SimpleNamespace(unit_index=np.asarray([0, 2, 2], dtype=np.int64)),
    )
    recs = {"r1": fake_recording()}

    features, targets, recordings = make_waveform_feature_matrix(
        FakeDataset(sample),
        recs,
        [("r1", 0.0, 1.0)],
        control="none",
        seed=0,
        window_len=1.0,
    )

    unit_features = recording_waveform_features(recs["r1"], control="none", recording_id="r1", seed=0)
    np.testing.assert_allclose(features[0], unit_features[[0, 2, 2]].sum(axis=0))
    assert targets.tolist() == [1]
    assert recordings == ["r1"]


def test_transform_waveform_recording_centered_removes_recording_mean() -> None:
    features = np.asarray([[1.0, 2.0], [3.0, 4.0], [10.0, 20.0]], dtype=np.float32)
    out = transform_waveform_features(features, "recording_centered", recording_ids=["a", "a", "b"])

    np.testing.assert_allclose(out[:2].mean(axis=0), [0.0, 0.0])
    np.testing.assert_allclose(out[2], [0.0, 0.0])


def test_summarize_marks_waveform_candidate_decision() -> None:
    rows = [{
        "target_mode": "choice",
        "family": "amp",
        "holdout": "S1",
        "decision": "candidate",
        "centered_delta_vs_shuffle": 0.1,
        "target0_improved_vs_shuffle": 0.6,
        "target1_improved_vs_shuffle": 0.6,
        "n_bidirectional_recordings": 3,
        "bidirectional_recording_fraction": 0.75,
    }]

    summary = summarize(rows)

    assert summary["decision"] == "waveform_target_control_candidate"
