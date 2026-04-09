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

## [26-Mar-2026 17:45 IST] — Track A Analysis Report (fortification_agent/track-a.log.qmd)

Wrote `fortification_agent/track-a.log.qmd` — a Quarto research log synthesising the completed fortification curation: 92 source rows, 68 canonical agents across 4 nutrient classes, 10 excluded rows (4 structural, 6 reclassified to health_supplement). Report covers nutrient class breakdown, source type distribution, data quality zones, FSSAI mandate notes from enrichment (flagged as unverified), and a 4-question handoff brief for Track B. Verified against taxonomy JSON and working CSV for all counts before writing; rendered cleanly with `quarto render` on first attempt.

---

## [26-Mar-2026 19:15 IST] — Synthesis reports for additives, colors, and label conventions sessions

Wrote three Quarto synthesis reports from finished sessions: `caas/label-conventions.log.qmd`, `additives/track-a.log.qmd`, and `colors/track-a.log.qmd`. All counts verified against source files before writing — the additives JSON now holds 158 entries (not 148 as in the README, which was written before the 5 colors session additions), and the label-conventions report ran pattern searches across 1,026 raw product rows to confirm 88 products using E-numbers, 113 using INS notation, and 4 distinct notation variants including bare parenthetical numbers. All three rendered cleanly with `quarto render` on first attempt.

---

## [26-Mar-2026 20:30 IST] — Consolidated curation synthesis report

Committed the 3 session logs as audit trail, then wrote `caas/curation-synthesis.log.qmd` — a single report superseding them. The report opens with one framing question (normalisation failure modes and taxonomy lookup failure modes) and keeps findings and implications in separate sections: findings cover notation variants across 1,026 products, the 158-entry taxonomy distribution including 13 animal-derived entries and 12 O-2 source_type tension entries, and the colours session's 30 INS entries and 7 deferred whole-food colorants. No deadblocks; rendered cleanly on first attempt.

---

## [26-Mar-2026 22:15 IST] — Reframe curation-synthesis.log.qmd: form/taxonomy design framing

Rewrote the framing of `caas/curation-synthesis.log.qmd` in place — no new file. The original implications section was written from a parser/pipeline premise; the revision reframes every implication as a form field design question (field type, options, edge cases the current form cannot represent). Changes: front matter description updated; §1 rewritten to establish IFID as a structured form; one parser-specific sentence removed from §2a findings; §3 Implications fully replaced with 6 numbered subsections covering additive search index, source_type as a form field, dietary flags, functional class field design, the missing raw_agricultural_material category, and class-only declarations; "Generic class-only declarations" removed from Open Questions (promoted to Implications §6); one line added to the AI authorship constraints noting the framing correction. Rendered cleanly on first attempt.

---

## [26-Mar-2026 23:45 IST] — Round 3 corrections to curation-synthesis.log.qmd + session retrospective

**Corrections (6 targeted changes to `caas/curation-synthesis.log.qmd`):**

Applied a planned set of corrections to remove noise and fix category misplacements that survived the round 1–2 revision passes: (1) added `{#sec-colour}` anchor to the colour declarations heading and replaced the invalid `§2c` cross-reference with a proper in-document link; (2) cut the negative-framing FD&C sentence ("do not appear for non-colour additives") and replaced with a single positive-framing sentence pointing to colour declarations; (3) removed the class-only colour declarations block (`artificial color`, `synthetic food colors`, etc.) from §2c — these strings appeared due to missing INS capture in data collection, not a taxonomy/form design question; (4) removed the FSSAI Variant 4 unverified sentence from findings and moved it to Open Questions as a named tracking item; (5) removed Implications §6 (Generic class-only declarations) — same reason as (3); (6) reframed two schema-state assertions ("the current schema has no field for X") in Implications §2 and §3 as design questions the data raises, not confirmed gaps. Rendered cleanly on first attempt. Anchor resolved without broken link warning.

**Session retrospective — comparative analysis of two logs:**

Conducted a comparison between `fortification_agent/track-a.log.qmd` (no revisions) and `caas/curation-synthesis.log.qmd` (three revision rounds) to identify what the fortification log got right from the start. The comparison surfaced two findings:

First: the fortification log was anchored to a governing design question from its first sentence. The question acted as a pre-writing filter — every sentence could be tested against it before being written. The curation-synthesis had no governing question; its filter was only "is this true?" and that filter let through everything.

Second, identified by Lalitha A R: "is this true?" is a necessary condition for a sentence to belong in a research document, not a sufficient one. The sufficient test is "why is this relevant and how does it contribute to the governing question?" Every sentence removed across three rounds of revision was accurate. None failed the truth test. All failed the relevance test.

The retrospective also developed the epistemic category framework: each sentence belongs to exactly one of verified fact from data, inference from verified fact, open question, or design question — and each makes a different demand on the reader. Misplacing a sentence assigns the reader the wrong stance: accepting something uncertain, acting on something unverified, or holding open something that has already been answered. The specific misplacements in curation-synthesis were: FSSAI Variant 4 (open question placed in findings), schema state assertions (unverified claim placed in implications as confirmed gap), class-only declarations (data artifact placed in findings as taxonomy requirement).

Retrospective written up as an experiment log and posted to iSRL sandbox-research Discussions #10: https://github.com/isrl-research/sandbox-research/discussions/10#discussioncomment-16329574

---

## [27-Mar-2026 18:30 IST] — wheat_form_prototype.py — IFID Wheat Entry CLI

Built `raw_agricultural_material/wheat_form_prototype.py`, a 5-step guided CLI that simulates how a brand would enter a wheat ingredient into IFID via structured choices (source → physical form → malted check → fortification → agent multi-select with zinc disambiguation). The form exposes schema gaps by classifying all 32 rows in wheat_working.csv against seven break types: OUT_OF_SCOPE, COMPOUND_PARSE_FAIL, NO_FORM_PATH, FERMENTATION_PATH, DATA_MODEL_MISMATCH, AGENT_AMBIGUITY, and DUPLICATE_VARIANT. All four verification paths ran cleanly: whole grain closes after step 2, refined flour without fortification closes after step 4, fortified whole flour triggers the zinc disambiguation prompt, and all 32 rows appear in the break report (17 breaks, 15 OK).

---

## [09-Apr-2026] — Schema redesign session: ingredient-declaration + dairy bootstrap

Design-only session — no TypeDB inserts. Three outcomes:

**1. source-type vocabulary fixed (design decision 008)**
`natural` replaced with typed vocabulary: `plant`, `dairy`, `animal`, `marine`, `fungal`,
`microbial`, `synthetic`. TypeQL update queries written for wheat and bansi wheat
(natural → plant) but not yet executed — flagged for next session start.

**2. Core schema redesign agreed (design decisions 009, 010)**
`derived-from` relation is replaced by `ingredient-declaration` (source + form +
processing-method). `ingredient-form` nodes are now source-agnostic — `bansi semolina`
as a node is gone, replaced by ingredient-declaration(bansi wheat, semolina). A lookup
layer (separate from TypeDB) owns all label strings and multilingual names, resolving
them to (source, form) pairs. This unblocks translation without schema changes and
removes variant noise from the core model. `db/schema.typeql` and `db/data.typedb` are
now stale — migration required next session before any new inserts.

**3. Dairy category bootstrapped**
`core/all_variants_working.csv`: 6 encoded wheat rows deleted (1,666 → 1,660).
`dairy/dairy_working.csv`: created, 122 rows. f_revised breakdown: processed_ingredient
(67), raw_agricultural_material (25), lipid base (17), fermentation_agent (7), others (6).
dairy_product_subtype tagged on 32 rows. Dairy is the next active category.

---

## [27-Mar-2026 22:15 IST] — variant_class_analysis.py — Signal/Noise Classification of 1,666 Variants

Built `core/variant_class_analysis.py`, a rule-based classifier that tags all 1,666 rows in `core/all_variants_working.csv` with one or more of 13 variant classes across two axes (noise: orthographic_noise, redundant_variant, compound_noise, out_of_scope; signal: linguistic_signal, transliteration_signal, canonical_form, form_signal, process_signal, grade_signal, fortification_signal, abbreviation_signal, multi_source). The main deadblock was unclassified rate: initial run hit 50.4% unclassified because the taxonomy had no class for plain English canonical names and form/grade/process uniqueness constraints were too strict; resolved by adding a `canonical_form` class, relaxing uniqueness to allow overlap with `redundant_variant`, and expanding all three vocabulary sets substantially (form, grade, process words). Final run: 1.5% unclassified (25 rows), all 7 verification criteria pass — đường/zucker/sucre/พริก caught as linguistic_signal, atta/maida/ghee/dahi/sooji as transliteration_signal, sait/palmolien/paim oil/wheatflour as orthographic_noise. Outputs: `variant_signal_class` column written to `all_variants_working.csv`, summary to `core/variant_class_report.csv`.

---
