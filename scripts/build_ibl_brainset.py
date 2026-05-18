"""Convert one IBL Brain-Wide Map session into a torch_brain-compatible HDF5 file.

Output schema (temporaldata.Data):
- brainset.id        str   "ibl_bwm"
- session.id         str   <eid>
- subject.id         str   <subject nickname>
- units              ArrayDict (id, region_id, region_acronym, mlapdv)
- spikes             IrregularTimeSeries (timestamps, unit_index)
- domain             Interval covering [first_spike, last_spike]

Usage:
    uv run python scripts/build_ibl_brainset.py [EID] [PROBE_NAME]

Defaults to the session validated in the smoke test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import h5py
import numpy as np
from iblatlas.regions import BrainRegions
from one.api import ONE
from temporaldata import ArrayDict, Data, Interval, IrregularTimeSeries

# IBL trial fields we copy through. start/end come from the `intervals` field separately.
TRIAL_FIELDS = (
    "stimOn_times",
    "response_times",
    "feedback_times",
    "feedbackType",
    "choice",
    "contrastLeft",
    "contrastRight",
    "probabilityLeft",
)

OPEN_ALYX = "https://openalyx.internationalbrainlab.org"
PUBLIC_USER = "intbrainlab"
PUBLIC_PASS = "international"
BRAINSET_ID = "ibl_bwm"


def _ensure_str_array(values, max_len: int = 64) -> np.ndarray:
    arr = np.asarray(values).astype(f"<U{max_len}")
    return arr


def _camel_to_snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def build_recording(eid: str, probe_name: str, out_dir: Path) -> Path:
    ONE.setup(base_url=OPEN_ALYX, silent=True)
    one = ONE(base_url=OPEN_ALYX, username=PUBLIC_USER, password=PUBLIC_PASS)

    # Subject from session details
    details = one.get_details(eid)
    subject = details.get("subject") if isinstance(details, dict) else getattr(details, "subject", "unknown")

    # Find pykilosort collection for the probe
    collections = one.list_collections(eid)
    probe_collections = [c for c in collections if probe_name in c]
    coll = next((c for c in probe_collections if "pykilosort" in c), None)
    if coll is None:
        raise ValueError(f"No pykilosort collection for probe {probe_name} in {eid}; got {probe_collections}")

    print(f"Loading {coll}...")
    clusters = one.load_object(eid, "clusters", collection=coll)
    channels = one.load_object(eid, "channels", collection=coll)
    spikes_obj = one.load_object(eid, "spikes", collection=coll)

    cluster_channels = np.asarray(clusters["channels"], dtype=np.int64)
    n_clusters = len(cluster_channels)

    # Region join: cluster → channel → CCF region
    region_ids = np.asarray(channels["brainLocationIds_ccf_2017"][cluster_channels], dtype=np.int64)
    br = BrainRegions()
    region_acronyms = _ensure_str_array(br.id2acronym(region_ids))

    # Stereotaxic coords per cluster (μm)
    mlapdv = np.asarray(channels["mlapdv"][cluster_channels], dtype=np.float32)

    # Per-unit waveform / spike features (real biological signatures, not animal-specific)
    amps = np.asarray(clusters["amps"], dtype=np.float32)
    depths = np.asarray(clusters["depths"], dtype=np.float32)
    peak_to_trough = np.asarray(clusters["peakToTrough"], dtype=np.float32)
    # Replace any NaNs with population medians (a few units can have missing values)
    for arr in (amps, depths, peak_to_trough):
        m = np.isnan(arr)
        if m.any():
            arr[m] = np.nanmedian(arr)

    # Per-recording-unique unit IDs (Dataset prepends brainset/session prefix at access time)
    unit_ids = _ensure_str_array([f"u{i:04d}" for i in range(n_clusters)], max_len=16)

    units = ArrayDict(
        id=unit_ids,
        region_id=region_ids,
        region_acronym=region_acronyms,
        mlapdv=mlapdv,
        amps=amps,
        depths=depths,
        peak_to_trough=peak_to_trough,
    )

    # Spikes — filter out-of-range/NaN clusters, sort by time
    spike_times = np.asarray(spikes_obj["times"], dtype=np.float64)
    spike_clusters = np.asarray(spikes_obj["clusters"], dtype=np.int64)
    valid = (
        np.isfinite(spike_times)
        & (spike_clusters >= 0)
        & (spike_clusters < n_clusters)
    )
    spike_times = spike_times[valid]
    spike_clusters = spike_clusters[valid]
    order = np.argsort(spike_times, kind="stable")
    spike_times = spike_times[order]
    spike_clusters = spike_clusters[order]

    if len(spike_times) == 0:
        raise ValueError(f"No valid spikes for {eid} probe {probe_name}")

    spike_t_start = float(spike_times[0])
    spike_t_end = float(spike_times[-1])

    # --- Behavior: trials and wheel (session-level, "alf" collection) ---
    print("Loading trials + wheel...")
    trials_raw = one.load_object(eid, "trials", collection="alf")
    intervals = np.asarray(trials_raw["intervals"], dtype=np.float64)
    trial_start = intervals[:, 0]
    trial_end = intervals[:, 1]
    trial_kwargs = {}
    for f in TRIAL_FIELDS:
        if f not in trials_raw:
            continue
        arr = np.asarray(trials_raw[f])
        # Coerce ints (choice, feedbackType) to int64; everything else stays float
        if np.issubdtype(arr.dtype, np.integer):
            arr = arr.astype(np.int64)
        else:
            arr = arr.astype(np.float64)
        trial_kwargs[_camel_to_snake(f)] = arr
    trials = Interval(start=trial_start, end=trial_end, **trial_kwargs)
    print(f"  trials: {len(trial_start)} (fields: {list(trial_kwargs)})")

    wheel_raw = one.load_object(eid, "wheel", collection="alf")
    wheel_times = np.asarray(wheel_raw["timestamps"], dtype=np.float64)
    wheel_position = np.asarray(wheel_raw["position"], dtype=np.float32)
    order = np.argsort(wheel_times, kind="stable")
    wheel_times = wheel_times[order]
    wheel_position = wheel_position[order]
    print(f"  wheel: {len(wheel_times):,} samples")

    # Union domain: cover spikes, trials, and wheel
    domain_start = float(min(spike_t_start, trial_start.min(), wheel_times.min()))
    domain_end = float(max(spike_t_end, trial_end.max(), wheel_times.max()))
    domain = Interval(start=np.array([domain_start]), end=np.array([domain_end]))

    spikes_ts = IrregularTimeSeries(
        timestamps=spike_times,
        unit_index=spike_clusters,
        domain=domain,
    )
    wheel_ts = IrregularTimeSeries(
        timestamps=wheel_times,
        position=wheel_position,
        domain=domain,
    )

    data = Data(
        brainset=Data(id=BRAINSET_ID),
        session=Data(id=eid),
        subject=Data(id=str(subject)),
        units=units,
        spikes=spikes_ts,
        trials=trials,
        wheel=wheel_ts,
        domain=domain,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{eid}_{probe_name}.h5"
    with h5py.File(out_path, "w") as f:
        data.to_hdf5(f)

    print(f"Wrote {out_path}")
    print(f"  subject={subject}  eid={eid}  probe={probe_name}")
    print(f"  units={n_clusters}  spikes={len(spike_times):,}")
    print(f"  duration={spike_t_end - spike_t_start:.1f}s  spike_rate={len(spike_times) / (spike_t_end - spike_t_start):.1f} Hz")
    print(f"  unique regions={len(set(region_acronyms.tolist()))}")
    print(f"  trials={len(trial_start)}  wheel_samples={len(wheel_times):,}")
    return out_path


def verify(out_path: Path) -> None:
    print(f"\nVerifying round-trip read of {out_path}...")
    with h5py.File(out_path, "r") as f:
        data = Data.from_hdf5(f, lazy=False)
        print(f"  brainset.id = {data.brainset.id!r}")
        print(f"  session.id  = {data.session.id!r}")
        print(f"  subject.id  = {data.subject.id!r}")
        print(f"  units.id    [{len(data.units.id)}] e.g. {data.units.id[:3].tolist()}")
        print(f"  units.region_acronym unique = {len(set(data.units.region_acronym.tolist()))}")
        print(f"  spikes.timestamps     [{len(data.spikes.timestamps):,}]  first 3 = {data.spikes.timestamps[:3]}")
        print(f"  trials                [{len(data.trials.start)}]  fields = {[k for k in data.trials.keys()]}")
        if hasattr(data.trials, "choice"):
            n_left = int((data.trials.choice == -1).sum())
            n_right = int((data.trials.choice == 1).sum())
            n_nogo = int((data.trials.choice == 0).sum())
            print(f"    choice counts: left={n_left}  right={n_right}  nogo={n_nogo}")
        print(f"  wheel.timestamps      [{len(data.wheel.timestamps):,}]")
        print(f"  wheel.position range  [{data.wheel.position.min():.2f}, {data.wheel.position.max():.2f}] rad")
        print(f"  domain = [{data.domain.start[0]:.2f}, {data.domain.end[-1]:.2f}]s")


def main() -> int:
    eid = sys.argv[1] if len(sys.argv) > 1 else "ebce500b-c530-47de-8cb1-963c552703ea"
    probe = sys.argv[2] if len(sys.argv) > 2 else "probe00"
    out_dir = Path("data/brainsets/ibl_bwm")
    out_path = build_recording(eid, probe, out_dir)
    verify(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
