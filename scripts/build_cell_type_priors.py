"""Build per-region cell-type priors from the Allen Brain Cell Atlas (Yao 2023 MERFISH).

Output: data/cell_type_priors/region_subclass_priors.parquet
  columns: region_acronym (CCFv2020), subclass, proportion
A subclass taxonomy of ~338 mouse-brain cell types; each region gets a
probability distribution over subclasses computed from MERFISH cell counts.

The CCFv2017→2020 remap is handled at training time by joining on acronym
(most acronyms persist; unmappable ones get logged).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from abc_atlas_access.abc_atlas_cache.abc_project_cache import AbcProjectCache

CACHE_DIR = Path("data/abc_atlas_cache")
OUT_DIR = Path("data/cell_type_priors")
# In the current ABC Atlas release, parcellation info lives in a -CCF directory,
# and taxonomy (subclass/cluster) lives in the base MERFISH directory.
PARCEL_DIR = "MERFISH-C57BL6J-638850-CCF"
PARCEL_FILE = "cell_metadata_with_parcellation_annotation"
TAXON_DIR = "MERFISH-C57BL6J-638850"
TAXON_FILE = "cell_metadata_with_cluster_annotation"


def main() -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Initializing ABC Atlas cache at {CACHE_DIR}...")
    cache = AbcProjectCache.from_s3_cache(cache_dir=CACHE_DIR)
    print(f"  current manifest: {cache.current_manifest}")

    print(f"\nDownloading parcellation table: {PARCEL_DIR}/{PARCEL_FILE}...")
    df = cache.get_metadata_dataframe(directory=PARCEL_DIR, file_name=PARCEL_FILE)
    print(f"  rows: {len(df):,}")
    print(f"  parcellation/taxonomy columns: "
          f"{[c for c in df.columns if 'parcellation' in c or c in ('class','subclass','supertype','cluster')]}")

    region_col = "parcellation_structure"
    subclass_col = "subclass"
    if region_col not in df.columns or subclass_col not in df.columns:
        print(f"ERROR: missing cols. have: {df.columns.tolist()}", file=sys.stderr)
        return 1
    # Drop rows missing either field
    df = df.dropna(subset=[region_col, subclass_col])
    print(f"  rows after dropna({region_col}, {subclass_col}): {len(df):,}")

    # Compute counts per (region, subclass) → normalize to proportion within each region
    counts = (
        df.groupby([region_col, subclass_col], observed=True)
          .size()
          .rename("count")
          .reset_index()
    )
    totals = counts.groupby(region_col, observed=True)["count"].transform("sum")
    counts["proportion"] = counts["count"] / totals
    counts = counts.rename(columns={region_col: "region_acronym", subclass_col: "subclass"})
    counts = counts[["region_acronym", "subclass", "count", "proportion"]]

    # Save
    out_path = OUT_DIR / "region_subclass_priors.parquet"
    counts.to_parquet(out_path, index=False)
    print(f"\nWrote {out_path}")
    print(f"  rows: {len(counts):,}")
    print(f"  unique regions:    {counts['region_acronym'].nunique()}")
    print(f"  unique subclasses: {counts['subclass'].nunique()}")

    # Save the subclass taxonomy (the K-dim ordering for our prior vectors)
    taxonomy = (
        counts.groupby("subclass", observed=True)["count"].sum()
              .sort_values(ascending=False)
              .reset_index()
    )
    taxonomy_path = OUT_DIR / "subclass_taxonomy.parquet"
    taxonomy.to_parquet(taxonomy_path, index=False)
    print(f"\nWrote {taxonomy_path}")
    print(f"  top 10 subclasses by total cells:")
    for row in taxonomy.head(10).itertuples():
        print(f"    {row.subclass:50s}  {int(row.count):>10,}")

    # Quick sanity peek: what are the priors for a few IBL regions we care about?
    for region in ("PO", "LP", "CA1", "DG-mo", "SSp-tr5"):
        sub = counts[counts["region_acronym"] == region].sort_values("proportion", ascending=False)
        if len(sub) == 0:
            print(f"\n  {region}: NOT FOUND in ABC Atlas — acronym remap needed")
            continue
        print(f"\n  {region}: top 5 subclasses")
        for row in sub.head(5).itertuples():
            print(f"    {row.subclass:50s}  {row.proportion:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
