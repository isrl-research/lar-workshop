# Additives — Session Close Notes
**Date:** 2026-03-13
**Source:** `additives/additives_taxonomy.json`
**Output:** `additives_clean_2026-03-13.csv` — 153 entries, 6 fields
**Updated:** 2026-03-13 (colors session — 5 new INS entries added)

---

## What this file is

The additives taxonomy as of 2026-03-13, exported to CSV from the source JSON. The original additives session produced 148 entries. A subsequent colors session identified 5 INS-numbered colour entries absent from the taxonomy and added them directly: INS 140, 150, 160d, 161b, 174. The file was regenerated from the updated JSON on the same date. Current row count: 153.

---

## Session scope

Source of truth for this session: `additives/additives_taxonomy.json`.
Fields exported: `ins_number`, `official_name`, `source_type`, `sources`, `functional_classes`, `codex_category`.
Multi-value fields (`sources`, `functional_classes`) are pipe-delimited in the CSV.

---

## Distribution

**Source type** (148 entries):
- synthetic: 72 (48.6%)
- plant: 45 (30.4%)
- mineral: 18 (12.2%)
- animal: 13 (8.8%)

**Codex category** (12 categories):
- Thickeners, stabilisers, emulsifiers and gelling agents: 40
- Colours: 25
- pH adjusters, anti-caking and anti-foaming agents: 17
- Antioxidants and acidity regulators: 15
- Preservatives: 11
- Modified starches: 11
- Flavour enhancers: 8
- Sweeteners: 7
- Gases, waxes and propellants: 6
- Enzymes: 4
- Polyols: 2
- Unclassified: 2

**Functional classes:** 24 unique classes, 286 total assignments across 148 entries. 72 entries carry more than one functional class.

**Sources field:** 73 unique source values across 76 entries. 72/148 entries have an empty `sources` field — all synthetic entries. Empty `sources` for synthetic entries is by design; domain expert review is required to determine whether sources can be specified for synthetic substances.

---

## Observed issues

### O-1 — INS 141: plant source_type, empty sources
`INS 141` (Copper complexes of chlorophylls) has `source_type=plant` but `sources` is empty. Every other plant-type entry has at least one source listed. This is the only biological-type entry with no source.

### O-2 — 12 entries: source_type=synthetic with biological sources listed
12 entries carry `source_type=synthetic` but have biological, fermentation-derived, or multi-origin values in `sources`. These fall into three sub-cases:

**Process chemistry from biological precursor** — synthesized or fermentation-derived, without production method specified in the record:
- INS 575 (Glucono-delta-lactone): corn
- INS 270 (Lactic acid, L-, D- and DL-): corn
- INS 296 (Malic acid, DL-): apple, pear
- INS 620 (L-Glutamic acid): molasses, corn, wheat gluten
- INS 621 (Monosodium L-glutamate): molasses, corn, wheat gluten

**Multi-origin** — can be derived from either synthetic or biological sources depending on production route:
- INS 422 (Glycerol): palm, soybean, sunflower, rapeseed, lard, tallow, propylene, sugar fermentation

**Extracted from biological source** — no abiotic production route listed in sources:
- INS 161g (Canthaxanthin): algae
- INS 1100 (alpha-Amylase): barley malt, animal pancreas, *Bacillus subtilis*
- INS 1104 (Lipases): animal pancreas, fungi
- INS 1102 (Glucose oxidase): *Aspergillus niger*, *Penicillium*
- INS 1101 (Protease): papaya latex, papaya
- INS 1204 (Pullulan): starch hydrolysate from *Aureobasidium pullulans*

No `microbial` source_type is in use. Fermentation-derived and microbial-extracted entries are currently classified under `synthetic`. Whether a separate source_type is introduced for these is a taxonomy decision for domain expert review.

### O-3 — INS 296 and INS 1204: codex_category=Unclassified
Both are valid INS numbers with established Codex GSFA entries.

- **INS 296** (Malic acid, DL-): functional class is `acidity regulator`. Codex category is `Antioxidants and acidity regulators` — the same bucket as 15 other entries in this dataset. Additionally, `sources = ['apple', 'pear']` is the natural L-form origin; the DL-form is synthetic. The sources listed may have been inherited from malic acid generally without distinguishing the isomer.
- **INS 1204** (Pullulan): functional classes are glazing agent, thickener, stabilizer, bulking agent. Codex category is `Thickeners, stabilisers, emulsifiers and gelling agents`. May have been unclassified due to its late addition to Codex GSFA.

---

## Action items

### Claude tasks

**TASK-A0 — Verify existing sources list** *(prerequisite for TASK-A1)*
Before the sourcing round, audit the 73 unique values currently in the `sources` field across all 148 entries. Produce a verified dict of accepted source strings — normalised spelling, no duplicates, flagged ambiguities. This dict becomes the controlled vocabulary for TASK-A1.

**TASK-A1 — Sourcing round: fill missing sources** *(blocked by TASK-A0)*
Run a sourcing pass over all entries with empty or incomplete `sources`. Present the verified source dict from TASK-A0 as the selection list. Any source not in the dict must be prefixed `?newsource` for review. Resolve conflicts for ambiguous entries (e.g. INS 422 Glycerol, where production route determines the source) by flagging rather than assuming. Output: updated `sources` field per entry, with `?newsource` prefixes intact for human review.

**TASK-A3 — Verify additives taxonomy as a whole** *(blocked by SME-1 and TASK-A1)*
Once TASK-A1 and SME-1 are complete, run a full taxonomy verification pass: cross-check INS numbers against Codex GSFA, confirm codex_category assignments (including O-3 fixes), check source_type consistency against populated sources, flag any remaining structural inconsistencies. This is the final QA step before the taxonomy is used downstream.

### SME tasks

**SME-1 — Add sources for additives where known**
For entries where sources cannot be determined from public references alone — particularly additives common in Indian F&B that may have India-specific production routes or local raw material usage — a domain expert should review and add known sources directly. Any source added by SME review should be noted as such. SME-1 output feeds into TASK-A1 (the sourcing round uses SME-supplied sources as part of the verified dict).
