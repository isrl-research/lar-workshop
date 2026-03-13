# Fortification Agent — Pre-session Notes
**Date:** 2026-03-13
**Source:** `core/all_variants_working.csv` (1,933 rows, INS entries removed from `core/all_variants.csv`)
**Entries in this category:** 78 rows (`f_revised = fortification_agent`)

---

## What is in this category

Four distinct sub-groups:

### 1. Vitamins
Fat-soluble and B-group. Multiple label variants per substance — expect normalisation work.

| Substance | Variants seen | Source |
|---|---|---|
| Vitamin A | vitamin a, vitamin a acetate, vitamin a palmitate, vitamin a retinyl palmitate, vitamins a | synthetic; D3 also from lanolin / fish liver oil |
| Vitamin D | vitamin d, vitamin d2, vitamin d2 ergocalciferol, vitamin d3, vitamins d, ergocalciferol, cholecalciferol | synthetic; fish liver oil; lanolin |
| Riboflavin (B2) | riboflavin, riboflavin 5'-phosphate sodium, vitamin b2, vitamins vitamin b2 | fermentation |
| Pyridoxine (B6) | pyridoxine hydrochloride, vitamin b6, vitamin b6 pyridox ine hydrochloride, vitamin b6 pyridoxal-5-phosphate | synthetic |
| B12 | cyanocobalamin, vitamin b12 | synthetic |
| Thiamin (B1) | thiamin, thiamine, fortified wheat flour thiamin, fortified wheat flour thiamine | synthetic; wheat (flour-fortified form) |
| Niacin | niacin, nicotinamide, fortified wheat flour niacin | synthetic |
| Others | folic acid, biotin, d-biotin, calcium b-hydroxy-b-methylbutyrate monohydrate cahmb | synthetic |

Notes:
- `vitamin b complex` is a group declaration — cannot resolve to a single entity.
- Fortified wheat flour variants (niacin, thiamin, thiamine) are compound declarations — the carrier (wheat flour) and the nutrient are declared together. Normalisation will need to separate nutrient from carrier or treat as a compound entry.

### 2. Minerals (salts)
All source `mineral`. 100% certain. No processing info needed — form is the key differentiator.

| Mineral | Forms |
|---|---|
| Iron | ferrous fumarate, ferrous gluconate, electrolytic iron, ferrous salt |
| Magnesium | carbonate, gluconate, hydroxide, oxide, sulphate, threonate, aspartate, salts of magnesium (group) |
| Zinc | zinc gluconate, zinc sulphate, zinc sulphate monohydrate |
| Potassium | potassium chloride, salt substitute potassium chloride |
| Others | manganese citrate, iodate, sodium img (unclear — likely sodium iodate, needs verification) |

Notes:
- `salts of magnesium` and `electrolytes` are group declarations.
- `sodium img` is a probable OCR/transcription artefact — likely `sodium iodine` or `sodium iodate`. Needs SME confirmation.

### 3. Amino acids
All source `synthetic`. All certain. Standard L-forms with some label noise.

Variants: l-arginine, l-arginine hcl, arginine; l-lysine, l-lysine hcl, lysine; l-glutamine, glutamine; methionine, dl-methionine, dl methionine; leucine; valine; threonine; phenylalaline (likely typo for phenylalanine); taurine.

Notes:
- `amino acids` is a group declaration — unresolvable without label context.
- `phenylalaline` is a probable spelling error for phenylalanine. Flag for correction.
- `dl methionine` and `dl-methionine` are the same entry with hyphenation difference.

### 4. Sports/functional crossover
Entries sourced from sports nutrition and health supplement product labels, not conventional food.

creatine monohydrate micronized, l-carnitine, l-camitine (typo variant), whey peptides, glutamine peptides, calcium b-hydroxy-b-methylbutyrate monohydrate cahmb.

Sources: `synthetic | corn`, `milk`. All zone=2.

Notes:
- These sit awkwardly in `fortification_agent`. They are functional ingredients in the sports nutrition context, not classical fortification agents.
- Decision needed at session open: keep in fortification_agent or move to a separate functional_ingredient category.

---

## Field completeness (78 rows)

| Field | Populated | Empty |
|---|---|---|
| source | 78/78 (100%) | 0 |
| m_explicit | 76/78 (97.4%) | 2 |
| uncertain=False | 77/78 (98.7%) | 1 |
| e_explicit | 10/78 (12.8%) | 68 |
| zone=1 | 27/78 (34.6%) | — |
| zone=2 | 51/78 (65.4%) | — |

`e_explicit` is mostly empty — expected, since most entries are crystalline chemicals with no notable processing step. Not a gap.

Physical form: 67/78 are `crystalline chemical`. 3 are `oil` (fat-soluble vitamins). 3 are `flour/fine powder` (fortified flour entries).

---

## Known issues to address at session open

1. **Group declarations** (unresolvable to single entity): `amino acids`, `electrolytes`, `vitamin b complex`, `vitamins a`, `vitamins d`, `salts of magnesium` — decision needed on how to handle.
2. **`sodium img`** — probable transcription artefact, likely `sodium iodate`. Needs confirmation.
3. **`phenylalaline`** — probable spelling error for phenylalanine.
4. **`dl methionine` / `dl-methionine`** — same substance, hyphenation variant.
5. **`l-camitine` / `l-carnitine`** — same substance, transcription error.
6. **Fortified wheat flour entries** — compound declarations mixing carrier and nutrient.
7. **Sports/functional crossover entries** — category classification decision pending.

---

## Reference standards for verification

- FSSAI Food Fortification Resource Centre: mandatory fortification standards (wheat flour, rice, edible oil, milk, salt)
- Codex GSFA: vitamins and minerals as food additives
- FSSAI Health Supplements, Nutraceuticals, Foods for Special Dietary Use (FSSAI-HSNFSDU) regulations: amino acids, creatine, L-carnitine, HMB fall under this, not conventional food additives
