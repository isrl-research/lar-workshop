# Experiment Log

---

## [14-Mar-2026] — Fortification Round 2 Fetch + NULL Clearance

Tagged `alcohol` as `solvent` (0 NULLs remaining in `core/all_variants_working.csv`); created `solvent/` category folder with README documenting classification rationale. Tagged `hpmc vegetarian capsule` as `thickener|gelling agent` (matched `f_could_be`; consistent with Codex INS 464). Ran Gemini-2.0-flash enrichment on 20 pending fortification variants (`enrich-fortification-r2/`): 20/20 records, zero UNSURE, zero parse errors, zero `?`-prefixed values; output appended to `fortification_agent/fetch/enrich-fortification/output_formatted.txt` (78 lines total). Taxonomy fold-in and variant resolution deferred to next fortification session.

---

## [14-Mar-2026] — NULL Triage Session: core/all_variants_working.csv

38 rows in `core/all_variants_working.csv` carried `f_revised = NULL`. This session classified 36 of them and deleted 2.

**Classifications applied:**

- 20 rows → `fortification_agent`: vitamins (vit. d2, retinyl acetate, retinyl palmitate, pantothenic acid, pantothenol, pteroylmonoglutamic acid, choline chloride), minerals (molybdenum, phosphorus, sodium selenite, sodium selenate, copper sulphate, cupric sulphate, chromium chloride, manganese sulphate, magnesium bisglycinate, magnesium phosphate dibasic, tri basic calcium phosphate, mineral chromium picolinate), and generic mineral group entry (chloride — IS_GROUP).
- 14 rows → `health_supplement`: nutraceuticals (inositol, l-theanine, glucuronolactone), Ayurvedic/botanical (trifala, aavarampoo, moringa extract, guduchi extract, neem azadirachta indica leaf, grape seed extract), branded enzyme blends (digezyme, proabsor8 blend papain), and probiotics (lactobilus casei, bacillus coagulans, bacillus coagulans snz 1969).

**Deletions:**

- `distilled water` — removed. Carrier/process water; not a food ingredient; no schema home in this dataset.
- `sparkling water` — removed. Same reasoning.

**Rows remaining NULL (2):**

- `alcohol` — classification deferred; decision pending.
- `hpmc vegetarian capsule` — INS 464; not in current additives taxonomy; routed to `additives/pending.csv` for separate enrichment.

**Files created:**

- `fortification_agent/pending_enrichment.csv` — 20 rows; these variants are classified but not yet enriched (no taxonomy entry, no variant resolution).
- `health_supplement/pending_enrichment.csv` — 14 rows; same status.
- `additives/pending.csv` — 1 row (hpmc vegetarian capsule, INS 464).

**Post-triage counts in `core/all_variants_working.csv`:**

| f_revised | count |
|---|---|
| fortification_agent | 92 |
| health_supplement | 20 |
| NULL | 2 |
| total rows | 1894 |

**Deduplication flag:** `cupric sulphate` and `copper sulphate` are both present in the fortification batch; these are label variants of the same compound and should be deduplicated in the next fortification enrichment session.

**Spelling flag:** `lactobilus casei` — likely `Lactobacillus casei`; to be corrected during health_supplement enrichment.

---

## [13-Mar-2026 23:30 IST] — Fortification Agent Enrichment Session

Ran the full enrichment pipeline for fortification_agent: removed 6 sports/functional variants (reclassified to health_supplement), deduplicated 72 label variants to 58 canonical inputs, ran Gemini enrichment (gemini-2.0-flash, temp 0) — 58/58 records, zero parse errors — and built fortification_taxonomy.json with 53 entries. One edge case handled in taxonomy build: compound label entries (Fortified Wheat Flour + Niacin/Thiamin) arrived before their standalone counterparts in the output file; fixed with a two-pass build that deprioritises compound labels. Session closed with cp/ snapshot; variant resolution (Step 5) and 5 SME flag items (L-HPC classification, sodium img OCR confirmation, over-broad FSSAI mandate on thiamin/zinc/folic acid, IS_GROUP corrections, source_type UNSURE on leucine/valine) deferred to next session.

---
