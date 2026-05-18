"""Smoke test: connect to public IBL Open Alyx, list BWM sessions, load one probe's cluster regions.

No write access, no large downloads — only cluster metadata (a few MB).
"""
from __future__ import annotations

import sys
from collections import Counter

from one.api import ONE

OPEN_ALYX = "https://openalyx.internationalbrainlab.org"
PUBLIC_USER = "intbrainlab"
PUBLIC_PASS = "international"


def main() -> int:
    ONE.setup(base_url=OPEN_ALYX, silent=True)
    one = ONE(base_url=OPEN_ALYX, username=PUBLIC_USER, password=PUBLIC_PASS)

    print("Searching BWM sessions...")
    eids = one.search(project="ibl_neuropixel_brainwide_01")
    print(f"  got {len(eids)} session ids (showing first 5):")
    for eid in eids[:5]:
        print(f"    {eid}")
    if not eids:
        print("ERROR: no sessions returned", file=sys.stderr)
        return 1

    eid = None
    insertions = []
    print(f"\nSearching for a session with probe insertions (scanning first 50)...")
    for candidate in eids[:50]:
        ins = one.alyx.rest("insertions", "list", session=candidate)
        if ins:
            eid = candidate
            insertions = ins
            print(f"  found session {eid} with {len(ins)} insertion(s)")
            break
    if eid is None:
        print("ERROR: no session in first 50 had insertions", file=sys.stderr)
        return 1
    for ins in insertions:
        print(f"    pid={ins['id']}  name={ins['name']}")

    pid = insertions[0]["id"]
    probe_name = insertions[0]["name"]
    print(f"\nProbe {probe_name} ({pid}): loading cluster regions...")
    # In ONE, probe data lives in alf/<probe_name>/pykilosort (or similar)
    collections = one.list_collections(eid)
    probe_collections = [c for c in collections if probe_name in c]
    print(f"  collections matching probe: {probe_collections}")
    if not probe_collections:
        print("ERROR: no collections for probe", file=sys.stderr)
        return 1

    # Prefer the pykilosort collection if present
    coll = next((c for c in probe_collections if "pykilosort" in c), probe_collections[0])
    print(f"  using collection: {coll}")

    clusters = one.load_object(eid, "clusters", collection=coll)
    n_clusters = len(clusters["channels"])
    print(f"  loaded {n_clusters} clusters; keys: {list(clusters.keys())}")

    print("\nLoading channels object for CCF region join...")
    channels = one.load_object(eid, "channels", collection=coll)
    print(f"  channels keys: {list(channels.keys())}")

    # Resolve cluster → channel → CCF region
    ccf_key = next((k for k in channels if "brainLocationIds" in k), None)
    if ccf_key is None:
        print("ERROR: no brainLocationIds_* field on channels", file=sys.stderr)
        return 1
    print(f"  using channels[{ccf_key!r}]")
    cluster_channel = clusters["channels"]
    region_ids = channels[ccf_key][cluster_channel]
    print(f"  {len(set(region_ids))} unique CCF region IDs across {n_clusters} clusters")

    # Resolve IDs → acronyms using iblatlas (brings in Allen ontology)
    try:
        from iblatlas.regions import BrainRegions

        br = BrainRegions()
        acronyms = br.id2acronym(region_ids)
        ctr = Counter(acronyms.tolist() if hasattr(acronyms, "tolist") else list(acronyms))
        print(f"  top 10 regions by cluster count: {ctr.most_common(10)}")
    except ImportError:
        print("  iblatlas not installed — run `uv add iblatlas` to resolve IDs to acronyms")

    return 0


if __name__ == "__main__":
    sys.exit(main())
