"""Explore the ABC Atlas manifest to find the parcellation annotation file."""
from __future__ import annotations
from pathlib import Path
from abc_atlas_access.abc_atlas_cache.abc_project_cache import AbcProjectCache

CACHE_DIR = Path("data/abc_atlas_cache")

cache = AbcProjectCache.from_s3_cache(cache_dir=CACHE_DIR)
print(f"manifest: {cache.current_manifest}\n")

for d in cache.list_directories:
    try:
        files = cache.list_metadata_files(d)
    except Exception as e:
        files = [f"<{e}>"]
    if not files:
        continue
    # Highlight anything with 'parcellation' in name
    relevant = [f for f in files if "parcell" in f.lower() or "cluster_annotation" in f.lower()]
    if relevant or d == "MERFISH-C57BL6J-638850":
        print(f"== {d} ==")
        for f in files:
            mark = "  <-- candidate" if ("parcell" in f.lower() or "cluster_annotation" in f.lower()) else ""
            print(f"  {f}{mark}")
        print()
