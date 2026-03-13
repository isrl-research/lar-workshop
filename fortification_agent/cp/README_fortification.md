# Fortification Agent — Session Notes
**Date:** 2026-03-13
**Source:** `fortification_agent/fortification_agent_working.csv`
**Snapshot:** `fortification_agent_working_2026-03-13.csv` — 72 variants, 29 columns

---

## Session scope

Starting point: `fortification_agent_working.csv` — 78 label variants from `core/all_variants_working.csv`.

This session completed enrichment (taxonomy build) but did not complete variant resolution.
The snapshot in this folder reflects the cleaned working file, not a fully resolved output.

---

## What happened this session

### Step 1 — Sports/functional rows removed

6 rows removed from `fortification_agent_working.csv` and reclassified in `core/all_variants_working.csv` (`f_revised`: `fortification_agent` → `health_supplement`):

| Variant | Reason |
|---|---|
| l-carnitine | Sports/ergogenic use |
| l-camitine | Sports/ergogenic use (OCR variant of l-carnitine) |
| creatine monohydrate micronized | Sports/ergogenic use |
| calcium b-hydroxy-b-methylbutyrate monohydrate cahmb | Sports/ergogenic use (HMB) |
| whey peptides | Sports/protein supplement use |
| glutamine peptides | Sports/protein supplement use |

Stub folder created: `health_supplement/README_health_supplement.md`.

### Step 2 — Deduplication

72 remaining variants collapsed to 58 canonical inputs by removing label noise:
- `dl methionine` / `dl-methionine` → DL-Methionine
- `vitamin b6 pyridox ine hydrochloride` → Pyridoxine Hydrochloride
- `riboflavin` / `vitamin b2` / `vitamins vitamin b2` → Riboflavin
- `glutamine` / `l-glutamine` → Glutamine
- `arginine` / `l-arginine` → Arginine
- `lysine` / `l-lysine` → Lysine (but l-lysine HCl kept distinct)
- `biotin` / `d-biotin` → Biotin
- `ergocalciferol` / `vitamin d2 ergocalciferol` → Ergocalciferol
- `vitamin a palmitate` / `vitamin a retinyl palmitate` → Retinyl Palmitate
- `potassium chloride` / `salt substitute potassium chloride` → Potassium Chloride
- `fortified wheat flour thiamin` / `fortified wheat flour thiamine` → Fortified Wheat Flour + Thiamin

Output: `fortification_agent/fetch/enrich-fortification/input_substances.txt` — 58 entries.

### Step 3 — Gemini enrichment

Model: `gemini-2.0-flash`, temperature 0, batch size 20, 3 batches.
Input: 58 substances. Output: 58 records, 0 parse errors.

Raw output: `fortification_agent/fetch/enrich-fortification/output_raw.txt`
Formatted: `fortification_agent/fetch/enrich-fortification/output_formatted.txt`

Run statistics:
- NUTRIENT_TYPE: mineral_salt 20, vitamin_b_group 14, amino_acid 11, vitamin_fat_soluble 8, group_declaration 3, functional_ingredient 1, ?pharmaceutical_excipient 1
- REG_CATEGORY: fssai_mandatory_fortification 23, fssai_hsnfsdu 21, unregulated 10, fssai_permitted_additive 4
- SOURCE_TYPE: synthetic 37, mineral 14, UNSURE 6, microbial 1
- FSSAI_MANDATE coverage: milk 15, wheat flour 13, edible oil 11, rice 8, salt 7
- UNSURE entries: 6 | ?-prefixed: 1 (L-HPC) | IS_GROUP::true: 4

### Step 4 — Taxonomy built

Output: `fortification_agent/fortification_taxonomy.json` — 53 entries.
- 5 duplicate canonical keys collapsed (compound label variants and Vitamin D2/D3/B12 label variants resolve to same canonical as standalone entries)
- F4 fix applied: Calcium Salt, Ferrous Salt set to `is_group_declaration: true` (Gemini returned false; both are generic group terms)
- Compound label entries deprioritised: standalone entries take precedence where key conflicts occur

---

## What is NOT done — continue next session

### Step 5 — Variant resolution (not started)

72 label variants in the working CSV need `canonical_key`, `resolution_type`, `flag` columns added.
Resolution is deterministic against `fortification_taxonomy.json` for most entries.

### Pending SME decisions (surface before resolving)

| Flag | Item | Question |
|---|---|---|
| F1 | L-HPC (`?pharmaceutical_excipient`) | Remove from dataset entirely, or reclassify to additives? |
| F2 | `sodium img` → Sodium Iodate | Confirm OCR resolution before finalising |
| F3 | FSSAI_MANDATE for Thiamin, Zinc Sulphate, Folic Acid | Gemini returned all-5-foods mandate — likely over-broad; verify against FSSAI standards |
| F5 | SOURCE_TYPE UNSURE for Leucine, Valine | Likely microbial (same production route as Arginine); confirm |

### Step 6 — Session close (not done)

- Promote working file to `fortification_agent_clean_2026-03-13.csv` once resolution is complete
- Update `core/all_variants_working.csv` to remove resolved rows
- Commit

---

## Files in this folder

| File | Description |
|---|---|
| `fortification_agent_working_2026-03-13.csv` | Working file snapshot — 72 variants, sports rows removed, no resolution columns yet |
| `stats_fortification.py` | Run for session statistics on working CSV and taxonomy |
| `README_fortification.md` | This file |

---

## Files produced this session (outside cp/)

| File | Description |
|---|---|
| `fortification_agent/fortification_taxonomy.json` | 53-entry taxonomy, built from Gemini enrichment |
| `fortification_agent/fetch/enrich-fortification/input_substances.txt` | 58 deduplicated canonical inputs |
| `fortification_agent/fetch/enrich-fortification/system_instructions.xml` | Gemini system instructions |
| `fortification_agent/fetch/enrich-fortification/run_fetch.py` | Fetch script |
| `fortification_agent/fetch/enrich-fortification/output_raw.txt` | Raw Gemini responses |
| `fortification_agent/fetch/enrich-fortification/output_formatted.txt` | Parsed one-line-per-record output |
| `health_supplement/README_health_supplement.md` | Stub for 6 reclassified sports/functional variants |
| `core/all_variants_working.csv` | Updated — 6 rows reclassified to health_supplement |
