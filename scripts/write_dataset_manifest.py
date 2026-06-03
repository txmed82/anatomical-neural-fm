"""Write a committed-safe manifest for ignored local IBL HDF5 recordings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping


REPO_ROOT = Path(__file__).resolve().parent.parent


def _as_list(values) -> list:
    return values.tolist() if hasattr(values, "tolist") else list(values)


def _choice_counts(choices) -> dict[str, int]:
    values = _as_list(choices)
    return {
        "left": sum(1 for c in values if int(c) == -1),
        "right": sum(1 for c in values if int(c) == 1),
        "nogo": sum(1 for c in values if int(c) == 0),
    }


def summarize_recordings(recs: Mapping[str, object]) -> dict:
    recordings = []
    subjects = set()
    total_units = 0
    total_trials = 0
    for rid in sorted(recs):
        rec = recs[rid]
        regions = _as_list(rec.units.region_acronym)
        choices = _as_list(rec.trials.choice) if hasattr(rec, "trials") else []
        subject_id = str(rec.subject.id)
        n_units = len(regions)
        n_trials = len(choices)
        subjects.add(subject_id)
        total_units += n_units
        total_trials += n_trials
        recordings.append({
            "recording_id": rid,
            "session_id": str(rec.session.id),
            "subject_id": subject_id,
            "n_units": n_units,
            "n_regions": len(set(str(r) for r in regions)),
            "n_trials": n_trials,
            "choice_counts": _choice_counts(choices),
        })
    return {
        "dataset": "ibl_bwm",
        "n_recordings": len(recordings),
        "n_subjects": len(subjects),
        "n_units": total_units,
        "n_trials": total_trials,
        "recordings": recordings,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data/brainsets/ibl_bwm")
    p.add_argument("--out", type=Path, default=REPO_ROOT / "manifests/ibl_bwm.local.json")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    from torch_brain.dataset import Dataset

    ds = Dataset(dataset_dir=args.data_dir, keep_files_open=True)
    recs = {rid: ds.get_recording(rid) for rid in ds.recording_ids}
    manifest = summarize_recordings(recs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {args.out}")
    print(
        f"recordings={manifest['n_recordings']} subjects={manifest['n_subjects']} "
        f"units={manifest['n_units']} trials={manifest['n_trials']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
