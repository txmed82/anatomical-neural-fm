from __future__ import annotations

import h5py
import numpy as np
from temporaldata import ArrayDict, Data, Interval, IrregularTimeSeries
from torch_brain.dataset import Dataset, DatasetIndex


def test_training_cache_without_wheel_loads_through_torch_brain(tmp_path) -> None:
    domain = Interval(start=np.array([0.0]), end=np.array([3.0]))
    data = Data(
        brainset=Data(id="ibl_bwm"),
        session=Data(id="eid-a"),
        subject=Data(id="subject-a"),
        units=ArrayDict(
            id=np.array(["u0000", "u0001"], dtype="<U16"),
            region_id=np.array([1, 2], dtype=np.int64),
            region_acronym=np.array(["VISp", "CA1"], dtype="<U64"),
            mlapdv=np.array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]], dtype=np.float32),
            amps=np.array([0.1, 0.2], dtype=np.float32),
            depths=np.array([100.0, 200.0], dtype=np.float32),
            peak_to_trough=np.array([0.3, 0.4], dtype=np.float32),
        ),
        spikes=IrregularTimeSeries(
            timestamps=np.array([1.0, 1.2, 1.9], dtype=np.float64),
            unit_index=np.array([0, 1, 0], dtype=np.int64),
            domain=domain,
        ),
        trials=Interval(
            start=np.array([0.8], dtype=np.float64),
            end=np.array([2.0], dtype=np.float64),
            stim_on_times=np.array([1.0], dtype=np.float64),
            choice=np.array([1], dtype=np.int64),
            contrast_left=np.array([0.0], dtype=np.float64),
            contrast_right=np.array([1.0], dtype=np.float64),
        ),
        domain=domain,
    )
    with h5py.File(tmp_path / "eid-a_probe00.h5", "w") as f:
        data.to_hdf5(f)

    ds = Dataset(dataset_dir=tmp_path, keep_files_open=True)
    rec = ds.get_recording("eid-a_probe00")
    assert not hasattr(rec, "wheel")
    assert rec.subject.id == "subject-a"

    sample = ds[DatasetIndex(recording_id="eid-a_probe00", start=1.0, end=2.0)]
    np.testing.assert_allclose(sample.spikes.timestamps, [0.0, 0.2, 0.9])
    assert sample.trials.choice.tolist() == [1]
