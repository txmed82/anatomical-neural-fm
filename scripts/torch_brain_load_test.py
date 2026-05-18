"""Verify our IBL HDF5 file is consumable by torch_brain's Dataset end-to-end.

Adds vendored torch_brain to sys.path (avoids einops version conflict in install).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))

import numpy as np  # noqa: E402

from torch_brain.dataset import Dataset, DatasetIndex  # noqa: E402


DATASET_DIR = REPO_ROOT / "data" / "brainsets" / "ibl_bwm"


def main() -> int:
    print(f"Loading torch_brain.dataset.Dataset from {DATASET_DIR}")
    ds = Dataset(dataset_dir=DATASET_DIR, keep_files_open=True)
    print(f"  recordings: {len(ds.recording_ids)}")
    print(f"  recording_ids: {ds.recording_ids[:3]}{'...' if len(ds.recording_ids) > 3 else ''}")

    rid = ds.recording_ids[0]
    full = ds.get_recording(rid)
    print(f"\nFull recording {rid[:8]}...:")
    print(f"  domain = [{full.domain.start[0]:.2f}, {full.domain.end[-1]:.2f}]s")
    print(f"  brainset.id = {full.brainset.id!r}")
    print(f"  session.id  = {full.session.id!r}")
    print(f"  subject.id  = {full.subject.id!r}")
    print(f"  units.id    [{len(full.units.id)}]  first 3 = {full.units.id[:3].tolist()}")
    print(f"  units.region_acronym [{len(full.units.region_acronym)}]  first 5 = {full.units.region_acronym[:5].tolist()}")
    print(f"  units.mlapdv.shape = {full.units.mlapdv.shape}")
    print(f"  spikes.timestamps   [{len(full.spikes.timestamps):,}]")

    # Slice a 1-second sample (which is what the sampler would yield to the model)
    t0 = 100.0
    t1 = 101.0
    print(f"\nSlicing 1-second window [{t0}, {t1}] via DatasetIndex...")
    sample = ds[DatasetIndex(recording_id=rid, start=t0, end=t1)]
    print(f"  sample.spikes.timestamps  [{len(sample.spikes.timestamps)}]")
    print(f"  sample.spikes.unit_index  [{len(sample.spikes.unit_index)}]")
    if len(sample.spikes.timestamps):
        print(f"    first 5 spike times: {sample.spikes.timestamps[:5]}")
        print(f"    first 5 unit_index: {sample.spikes.unit_index[:5].tolist()}")
        active_units = np.unique(sample.spikes.unit_index)
        print(f"    {len(active_units)}/{len(full.units.id)} units spiked in this window")

    # Sampling intervals — what samplers use to decide where to slice
    intervals = ds.get_sampling_intervals()
    iv = intervals[rid]
    print(f"\nSampling intervals for this recording:")
    print(f"  {len(iv.start)} interval(s); total duration = {(iv.end - iv.start).sum():.1f}s")

    print("\nAll checks passed — HDF5 schema is consumable by torch_brain.dataset.Dataset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
