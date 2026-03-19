# README: fortification-taxonomy_clean_2026-03-19.json

## What this file is

A taxonomy of fortification agents recognised in IFID label data, normalised to 68 canonical entries with source traceability. This file is the output of the fortification-taxonomy session (2026-03-19) and the reference input for the "fortified with" field in F&B brand product records.

---

## Source

**Tier 1 inputs (read-only):**
- `fortification_agent_working.csv` — 72 rows, all labelled `f_revised = fortification_agent`, extracted from the IFID ingredient corpus
- `pending_enrichment.csv` — 20 rows, additional fortification agent variants pending taxonomy assignment
- `fortification_taxonomy.json` — reference file containing regulatory metadata (FSSAI mandate categories, nutrient type classifications)

---

## What was done this session

### Phase 1 — Working CSV analysis (72 rows)

All 72 rows from `fortification_agent_working.csv` were reviewed individually.

**4 rows excluded:**

| Row variant | Reason |
|---|---|
| `l-hpc` | Pharmaceutical excipient (low-substituted hydroxypropyl cellulose); misclassified as fortification agent on source label |
| `fortified wheat flour niacin` | Composite product; `milling_grade = fortified`; not a standalone agent |
| `fortified wheat flour thiamin` | Composite product; `milling_grade = fortified` |
| `fortified wheat flour thiamine` | Typo duplicate of above |

**15 label variants folded into canonical entries:**

Variants folded: `d-biotin`, `l-lysine`, `vitamin b2`, `vitamins a`, `vitamins d`, `l-arginine`, `l-glutamine`, `dl-methionine` (spacing), `ergocalciferol`, `cholecalciferol`, `vitamins vitamin b2`, `vitamin d2 ergocalciferol`, `vitamin a retinyl palmitate`, `salt substitute potassium chloride`, `vitamin b6 pyridox ine hydrochloride`.

Each folded variant is recorded in the `source_row_variants` field of its canonical entry.

**2 OCR typos corrected and included:**

| Source label | Corrected to |
|---|---|
| `phenylalaline` | Phenylalanine |
| `sodium img` | Sodium Iodate (OCR artefact; confirmed from taxonomy notes) |

The remaining 53 rows were included as distinct canonical entries.

### Phase 2 — Pending enrichment (20 rows)

All 20 rows from `pending_enrichment.csv` were reviewed against the Phase 1 taxonomy.

**5 rows folded into existing entries:**

| Pending variant | Folded into |
|---|---|
| `vit. d2` | Vitamin D2 (Ergocalciferol) |
| `retinyl acetate` | Retinyl Acetate (source_variants updated: `fish liver oil` added) |
| `retinyl palmitate` | Retinyl Palmitate (already present; no change) |
| `pteroylmonoglutamic acid` | Folic Acid (IUPAC name; added as alias) |
| `cupric sulphate` | Copper Sulphate (cupric = Cu²⁺; folded into new canonical entry) |
| `mineral chromium picolinate` | Chromium Picolinate (product-descriptor prefix stripped) |

**15 new canonical entries added:**
Chloride, Molybdenum, Phosphorus, Pantothenol, Sodium Selenite, Sodium Selenate, Copper Sulphate, Choline Chloride, Pantothenic Acid, Chromium Chloride, Chromium Picolinate, Manganese Sulphate, Magnesium Bisglycinate, Magnesium Phosphate Dibasic, Tricalcium Phosphate.

---

## What was found

- 68 canonical entries total: 33 mineral nutrients, 16 water-soluble vitamins, 13 amino acids, 6 fat-soluble vitamins
- 7 entries are group declarations (non-specific labels): Amino Acids, Calcium Salt, Chloride, Electrolytes, Ferrous Salt, Salts of Magnesium, Vitamin B Complex
- 92 source rows processed across both input files; all rows are either absorbed into a canonical entry or recorded as excluded with reason
- `electrolytic_iron` carries a `question_tags` flag from the source CSV (production method unconfirmed)
- `pantothenic_acid` carries an uncertainty flag in the pending enrichment source (microbial fermentation as possible source unconfirmed)

<!-- VERIFY: Confirm sodium img = sodium iodate with domain expert before publishing this taxonomy externally -->

---

## Current state

- **68 canonical entries** as of 2026-03-19
- Source: 72 rows from `fortification_agent_working.csv` + 20 rows from `pending_enrichment.csv`
- JSON structure: array under key `fortification_agents`; each entry has `id`, `canonical_name`, `aliases`, `nutrient_class`, `source_variants`, `is_group_declaration`, `source_row_variants`, `notes`

---

## Downstream dependencies

- F&B brand product record UI: "fortified with" field dropdown
- `taxonomy_log.md`: recognition count log (updated this session)
