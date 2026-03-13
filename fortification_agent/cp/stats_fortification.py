#!/usr/bin/env python3
"""
stats_fortification.py
Session stats for fortification_agent — 2026-03-13

Run from fortification_agent/cp/:
    python stats_fortification.py
"""

import csv
import json
from collections import Counter

WORKING_CSV = "./fortification_agent_working_2026-03-13.csv"
TAXONOMY_JSON = "../fortification_taxonomy.json"

def main():
    # --- Working CSV stats ---
    with open(WORKING_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    print(f"\n{'='*55}")
    print("FORTIFICATION AGENT — SESSION STATS (2026-03-13)")
    print(f"{'='*55}")
    print(f"\nWorking CSV: {WORKING_CSV}")
    print(f"  Total variants : {len(rows)}")

    nc = Counter(r.get("nutrient_class", "") for r in rows)
    print(f"\nnutrient_class distribution ({len(rows)} rows):")
    for val, count in nc.most_common():
        label = val if val else "(blank)"
        pct = 100 * count / len(rows)
        print(f"  {label:30s}: {count:3d}  ({pct:.1f}%)")

    # Source distribution
    src = Counter(r.get("source", "") for r in rows)
    print(f"\nsource distribution (top 10):")
    for val, count in src.most_common(10):
        label = val if val else "(blank)"
        print(f"  {label:30s}: {count:3d}")

    # Flag columns if present
    if "canonical_key" in rows[0]:
        resolved = sum(1 for r in rows if r.get("canonical_key"))
        print(f"\nResolution:")
        print(f"  resolved (canonical_key set) : {resolved}")
        print(f"  unresolved                   : {len(rows) - resolved}")
        flags = Counter(r.get("flag", "") for r in rows if r.get("flag"))
        if flags:
            print(f"\nFlags:")
            for flag, count in flags.most_common():
                print(f"  {flag:30s}: {count}")
    else:
        print(f"\n  Note: resolution columns not yet added (canonical_key, resolution_type, flag).")
        print(f"  Run resolution step before using this file downstream.")

    # --- Taxonomy stats ---
    print(f"\n{'-'*55}")
    print(f"Taxonomy: {TAXONOMY_JSON}")
    try:
        with open(TAXONOMY_JSON) as f:
            tax = json.load(f)
        agents = tax.get("fortification_agents", {})
        print(f"  Total entries     : {len(agents)}")

        nt = Counter(v["nutrient_type"] for v in agents.values())
        print(f"\n  nutrient_type distribution:")
        for val, count in nt.most_common():
            flag = "  [?-prefix]" if val.startswith("?") else ""
            print(f"    {val:35s}: {count:3d}{flag}")

        rc = Counter(v["regulatory_category"] for v in agents.values())
        print(f"\n  regulatory_category distribution:")
        for val, count in rc.most_common():
            print(f"    {val:35s}: {count:3d}")

        st = Counter(v["source_type"] for v in agents.values())
        print(f"\n  source_type distribution:")
        for val, count in st.most_common():
            print(f"    {val:35s}: {count:3d}")

        unsure = [k for k, v in agents.items() if "UNSURE" in json.dumps(v)]
        q_vals = [k for k, v in agents.items() if any(
            str(fv).startswith("?") for fv in v.values() if isinstance(fv, str)
        )]
        groups = [k for k, v in agents.items() if v.get("is_group_declaration")]
        print(f"\n  Flags:")
        print(f"    UNSURE entries        : {len(unsure)}")
        print(f"    ?-prefixed entries    : {len(q_vals)}")
        print(f"    group_declaration     : {len(groups)}")

    except FileNotFoundError:
        print(f"  WARNING: {TAXONOMY_JSON} not found.")

    print(f"\n{'='*55}\n")

if __name__ == "__main__":
    main()
