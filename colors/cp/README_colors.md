# Colors — Session Close Notes
**Date:** 2026-03-13
**Sources:**
- `additives/additives_taxonomy.json` — INS-keyed colour entries (Tier 1, read-only)
- `core/all_variants_working.csv` — non-INS colour variants from label corpus

---

## What this session did

Started with two inputs:
- 25 INS colour entries exported from the additives taxonomy → `colors_ins_clean.csv`
- 44 non-INS colour variant rows from the core working file → `colors_nonins_variants.csv`

Resolved 37 of 44 variant rows. 7 whole-food rows deferred to the raw_agricultural_material session.

---

## Resolution log

### Pass 1 — Explicit match to existing INS (25 rows removed)
FD&C-named synthetic dyes and botanical extract declarations where the INS already existed in the clean taxonomy. All 25 resolved without adding new entries.

Mapped to: INS 100 (×2), 102 (×2), 110 (×3), 129 (×6), 132 (×2), 133 (×3), 160a(i) (×1), 160b (×3), 160c (×2), 171 (×1).

### Pass 2 — INS exists in Codex but absent from taxonomy (6 rows resolved, 4 entries added)
INS 140 (Chlorophylls), 160d (Lycopene), 161b (Lutein) added to taxonomy.
One generic INS 150 (Caramel) added as a single entry to cover undifferentiated caramel colour declarations — the sub-types 150a, 150c, 150d already existed.

Resolved: lutein, lutein color, lutein-zeaxanthin complex → 161b; lycopene → 160d; caramel color → 150; chlorophyll color → 140 and 141.

### Pass 3 — Unresolvable group declarations (5 rows dropped)
`artificial color`, `artificial colors`, `synthetic food colors`, `color vegetable juice`, `vegetable juice concentrate for color` — no single INS resolvable. Dropped from working; not added to taxonomy.

### Pass 4 — INS absent from taxonomy, mineral source (1 row resolved, 1 entry added)
INS 174 (Silver) added. `silver leaf` resolved to INS 174.

---

## Taxonomy additions (5 new INS entries)

All 5 added to `additives/additives_taxonomy.json` and regenerated into `additives_clean_2026-03-13.csv` (now 153 rows, was 148).

| INS | Official name | source_type | sources |
|---|---|---|---|
| 140 | Chlorophylls | plant | green leaves, spinach, grass, nettles, alfalfa |
| 150 | Caramel | plant | sugarcane, corn, wheat, potato, glucose syrup |
| 160d | Lycopene | plant | tomato |
| 161b | Lutein | plant | marigold |
| 174 | Silver | mineral | — |

---

## core/all_variants_working.csv changes

- 37 resolved colour rows removed (1933 → 1896 rows).
- 7 case C rows retained with `f_revised` updated to `colour|raw_agricultural_material` so they surface during the raw_agricultural_material session.

Updated rows: kesar, safron, paprika, hibiscus, carrot powder, carrot flakes, pomegranate powder.

---

## Output files

### colors_ins_clean.csv (30 entries)
Clean INS colour taxonomy. Source: additives_taxonomy.json + 5 new entries added this session.
This is the reference file for any downstream colour resolution work.

### colors_nonins_variants.csv (7 rows — deferred)
Whole-food colour ingredients with no INS number. Deferred to the raw_agricultural_material session.
`f_explicit=colour` for all 7. `f_revised=colour|raw_agricultural_material`.

| variant | source | note |
|---|---|---|
| kesar | saffron | Hindi name for saffron; variant pair with `safron` |
| safron | saffron | Spelling variant of saffron; variant pair with `kesar` |
| paprika | paprika | Whole dried spice (drying, powder); distinct from INS 160c which is solvent-extracted oleoresin |
| hibiscus | hibiscus | Dried flower |
| carrot powder | carrot | Dried whole carrot; distinct from INS 160a(i) beta-carotene extract |
| carrot flakes | carrot | Dried whole carrot |
| pomegranate powder | pomegranate | Dried whole fruit powder |

---

## Downstream dependencies

- `additives/additives_taxonomy.json` — updated with 5 new entries; regenerate any derived files if re-running the additives session.
- `core/all_variants_working.csv` — 37 rows removed; this is the input for all future category sessions.
- Raw agricultural material session — will encounter the 7 deferred rows with dual f_revised tags.
