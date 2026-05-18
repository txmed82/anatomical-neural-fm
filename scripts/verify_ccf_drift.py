"""Sanity-check that IBL CCFv2017 acronyms are semantically consistent with ABC Atlas
CCFv2020 parcellation_structure acronyms.

The agent's research flagged a potential issue: IBL stores numeric `brainLocationIds_ccf_2017`,
but ABC Atlas joins on acronym + Allen ontology, not on numeric IDs. So the right
question is: does the same acronym refer to the same anatomical structure in both
ontology versions?

This script enumerates every CCFv2017 acronym present in our local HDF5s, looks up
its IBL Allen name, and reports the resolution against ABC Atlas's parcellation
table. Output is a printed table — no file written.

If most acronyms match by name (or fall back to a semantically reasonable ancestor),
the acronym-based join we already do is correct. The numeric-ID remap the agent
suggested is unnecessary in that case.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "vendor" / "torch_brain"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from anatomical_poyo_smoke import (  # noqa: E402
    PRIORS_PATH, _resolve_acronyms_with_fallback,
)
from iblatlas.regions import BrainRegions  # noqa: E402
from torch_brain.dataset import Dataset  # noqa: E402


def main() -> int:
    ds = Dataset(dataset_dir=REPO_ROOT / "data/brainsets/ibl_bwm", keep_files_open=True)
    priors_df = pd.read_parquet(PRIORS_PATH)
    abc_available = set(priors_df["region_acronym"].unique())
    br = BrainRegions()

    # Collect IBL acronyms across all our recordings + their CCFv2017 IDs
    seen: dict[str, int] = {}
    for rid in ds.recording_ids:
        rec = ds.get_recording(rid)
        ids = np.asarray(rec.units.region_id, dtype=np.int64)
        acs = np.asarray(rec.units.region_acronym).astype(str)
        for a, i in zip(acs, ids):
            seen.setdefault(a, int(i))

    resolution = _resolve_acronyms_with_fallback(sorted(seen), abc_available)

    print(f"{'IBL acr':<12} {'CCFv2017 id':<12} {'IBL name':<48} {'ABC resolution':<24} {'note'}")
    print("=" * 120)
    direct = 0
    fallback = 0
    unknown = 0
    for acr in sorted(seen):
        ibl_id = seen[acr]
        try:
            ibl_name = br.id2name(np.array([ibl_id]))[0]
        except Exception:
            ibl_name = "?"
        resolved = resolution.get(acr)
        if resolved == acr:
            direct += 1
            note = "direct match"
        elif resolved is not None:
            fallback += 1
            try:
                resolved_id = br.acronym2id(resolved)
                resolved_id = int(np.atleast_1d(resolved_id)[0])
                resolved_name = br.id2name(np.array([resolved_id]))[0]
            except Exception:
                resolved_name = "?"
            note = f"ancestor → {resolved_name}"
        else:
            unknown += 1
            note = "no match (fiber tract / unmapped)"
        resolved_str = resolved if resolved else "—"
        print(f"{acr:<12} {ibl_id:<12} {ibl_name[:47]:<48} {resolved_str:<24} {note}")

    print("\nSummary:")
    print(f"  unique IBL acronyms: {len(seen)}")
    print(f"  direct ABC match:    {direct}")
    print(f"  ancestor fallback:   {fallback}")
    print(f"  unresolved:          {unknown}")
    print()
    if unknown == 0 or all(seen[a] == 0 or "fiber" in note for a in sorted(seen)):
        print("Conclusion: acronym-based join (with hierarchical fallback) covers all real regions.")
        print("CCFv2017→2020 numeric-ID remap is unnecessary for our use case.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
