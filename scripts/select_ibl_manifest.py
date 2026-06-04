"""Select a fixed IBL BWM recording manifest from Alyx insertion metadata.

This avoids using "first N insertions" as an implicit experimental design.
The selector is metadata-only: it balances subjects/labs from PASS insertions
and writes session/probe pairs for the slower HDF5 builder.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from scripts.build_ibl_brainset import OPEN_ALYX, PUBLIC_PASS, PUBLIC_USER
    from scripts.build_ibl_brainset_batch import BWM_PROJECT
except ModuleNotFoundError:
    from build_ibl_brainset import OPEN_ALYX, PUBLIC_PASS, PUBLIC_USER
    from build_ibl_brainset_batch import BWM_PROJECT
from one.api import ONE


def compact_insertion(ins: dict[str, Any]) -> dict[str, Any] | None:
    info = ins.get("session_info") or {}
    meta = ins.get("json") or {}
    if meta.get("qc") != "PASS":
        return None
    n_units = int(meta.get("n_units") or meta.get("n_units_qc_pass") or 0)
    if n_units <= 0:
        return None
    return {
        "session_id": ins["session"],
        "probe_name": ins["name"],
        "subject_id": info.get("subject", "unknown"),
        "lab": info.get("lab", "unknown"),
        "start_time": info.get("start_time"),
        "task_protocol": info.get("task_protocol"),
        "insertion_id": ins.get("id"),
        "n_units_meta": n_units,
        "qc": meta.get("qc"),
        "alignment_qc": (meta.get("extended_qc") or {}).get("alignment_qc"),
    }


def select_balanced(
    candidates: list[dict[str, Any]],
    target: int,
    max_per_subject: int,
    min_units: int,
) -> list[dict[str, Any]]:
    candidates = [r for r in candidates if r["n_units_meta"] >= min_units]
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sorted(candidates, key=lambda r: (-r["n_units_meta"], r["session_id"], r["probe_name"])):
        by_subject[row["subject_id"]].append(row)

    ranked_subjects = sorted(
        by_subject,
        key=lambda s: (-min(len(by_subject[s]), max_per_subject), by_subject[s][0]["lab"], s),
    )
    desired_subjects = max(1, target // max_per_subject)
    subjects_by_lab: dict[str, list[str]] = defaultdict(list)
    for subject in ranked_subjects:
        subjects_by_lab[by_subject[subject][0]["lab"]].append(subject)
    labs = sorted(subjects_by_lab)
    subject_order = []
    while len(subject_order) < desired_subjects:
        progressed = False
        for lab in labs:
            if len(subject_order) >= desired_subjects:
                break
            if subjects_by_lab[lab]:
                subject_order.append(subjects_by_lab[lab].pop(0))
                progressed = True
        if not progressed:
            break
    remaining_subjects = [s for s in ranked_subjects if s not in set(subject_order)]
    selected: list[dict[str, Any]] = []
    subject_counts: Counter[str] = Counter()
    while len(selected) < target:
        progressed = False
        for subject in subject_order:
            if len(selected) >= target:
                break
            if subject_counts[subject] >= max_per_subject:
                continue
            rows = by_subject[subject]
            while rows and any(
                r["session_id"] == rows[0]["session_id"] and r["probe_name"] == rows[0]["probe_name"]
                for r in selected
            ):
                rows.pop(0)
            if not rows:
                continue
            selected.append(rows.pop(0))
            subject_counts[subject] += 1
            progressed = True
        if not progressed:
            if remaining_subjects:
                subject_order.extend(remaining_subjects)
                remaining_subjects = []
                continue
            break
    return selected


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=20)
    p.add_argument("--scan-limit", type=int, default=400)
    p.add_argument("--max-per-subject", type=int, default=2)
    p.add_argument("--min-units", type=int, default=100)
    p.add_argument("--out", type=Path, default=Path("manifests/ibl_bwm_phase4.json"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ONE.setup(base_url=OPEN_ALYX, silent=True)
    one = ONE(base_url=OPEN_ALYX, username=PUBLIC_USER, password=PUBLIC_PASS)
    raw = one.alyx.rest("insertions", "list", project=BWM_PROJECT, limit=args.scan_limit)
    candidates = [row for ins in raw if (row := compact_insertion(ins)) is not None]
    selected = select_balanced(candidates, args.target, args.max_per_subject, args.min_units)
    if len(selected) < args.target:
        raise SystemExit(f"selected only {len(selected)}/{args.target}; lower filters or scan more")

    payload = {
        "dataset": "ibl_bwm",
        "project": BWM_PROJECT,
        "selection": {
            "target": args.target,
            "scan_limit": args.scan_limit,
            "max_per_subject": args.max_per_subject,
            "min_units": args.min_units,
        },
        "n_recordings": len(selected),
        "n_subjects": len({r["subject_id"] for r in selected}),
        "labs": sorted({r["lab"] for r in selected}),
        "recordings": selected,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {args.out}")
    print(f"recordings={payload['n_recordings']} subjects={payload['n_subjects']} labs={len(payload['labs'])}")
    for subject, n in sorted(Counter(r["subject_id"] for r in selected).items()):
        print(f"  {subject}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
