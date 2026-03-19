# Last Session Summary — 2026-03-19

## What was done this session

- Removed 92 `fortification_agent` rows from `core/all_variants_working.csv` (1,894 → 1,802)
- Analysed all 262 additive-lane residual rows against `additives/additives_taxonomy.json`
- Phase 1: removed 130 confirmed taxonomy matches (synonyms, label-prefix formats, typo corrections)
- Phase 2: manually added 5 missing INS entries to taxonomy (153 → 158 entries)
  - INS 297 Fumaric acid, INS 319 TBHQ, INS 321 BHT, INS 527 Ammonium hydroxide, INS 968 Erythritol
- Phase 3: removed 6 rows matching those new entries
- **Working CSV now at 1,666 rows. 3 commits on main.**

---

## What remains — 126 residual rows needing decision calls

### Bucket A — Misclassified (wrong lane, clearest wins)

**antioxidant (17 rows)** — all nutrients, not food antioxidants. Reclassify to:
- `fortification_agent`: ferrous sulphate, encapsulated ferrous sulphate, ferric pyrophosphate, potassium iodate, potassium iodide, sodium molybdate, thiamine mononitrate (×2), thiamin hydrohloride, pyridoxine hydroxide, vitamins pantothenol, vitamins vitamin b12, antioxidant vitamin d
- `health_supplement`: creatine monohydrate, catechins, goji berry, resveratrol

**preservative (8 rows)** — mixed bag:
- → `health_supplement`: lactobacillus acidophilus, l.bacillus delbruecki subsp, limosilactobacillus reuteri, lactic acid ferments, latic culture (typo)
- → `fortification_agent`: sodium selenite angydrate (anhydrate)
- → process descriptor (drop or flag): uv treated and ozonized
- → keep / review: sulphites (generic multi-INS, too vague to resolve)

**sweetener|bulking agent (10 rows)** — prebiotics, not additives:
- → `health_supplement`: fos, fructooligosaccharide, fructo-oligosaccharide (×3), fructo oligosaccharide, fructooligosaccharides, fructo-oligosaccharides, fructo-oligosaccharides prebiotic fibre, corn syrup solids (check — may be INS 1702 or similar)

**flour treatment agent (1 row)**:
- → `fortification_agent`: l-lysine hydrochloride (amino acid)

**antioxidant|preservative (1 row)**:
- → `health_supplement` or flag: latic culture (probiotic, typo of lactic culture)

---

### Bucket B — Non-INS substances (legitimate ingredients, no INS number)

**thickener (12 rows)**: isabgol, psyllium husk, psyllium powder, cluster bean powder (guar raw form), methocel k4m (HPMC), edible gum (generic), modified starch (generic), modified starch maize, modified starch tapioca, costarch, sodium starch glycolate, modified maize starch

**bulking agent (9 rows)**: maltodextrin (×2), corn maltodextrin, wheat maltodextrin, wheat dextrin, citrus fiber, citrus fibre, croscarmellose sodium, 2'-fucosyllactose human milk oligosaccharide

**raising agent (6 rows)**: yeast, dried yeast, navsadar, naushadar, papad khar (traditional Indian alkalis — no INS), baking powder (compound mixture — no single INS)

**gelling agent (5 rows)**: fish gelatin, bovine gelatin, food grade fish gelatin, capsule shell ingredient gelatin, nata de coco

**humectant (2 rows)**: aloe vera juice, hyaluronic acid

**firming agent (3 rows)**: magnesium sulfate, magnesium taurate, dipotassium phosphate (check INS 340 — may be resolvable)

**anticaking agent (8 rows)**: calcium silicate (INS 552 — missing from taxonomy, could add), zinc oxide (INS 1504?), magnesium stearate (INS 572?), ferric ammonium citrate (INS 381?), tribasic calcium phosphate, magnesium hydrogen phosphate, anticaking agents (generic), magnesium stearate

**solvent (2 rows)**: alcohol, ethyl alcohol — ethanol, not an INS additive

**packaging gas (2 rows)**: packaging gas nitrogen, packaging gases nitrogen — INS 941 (taxonomy error: 941 listed as Dimethylpolysiloxane, should be Nitrogen). Taxonomy data quality issue to note.

**emulsifier|stabiliser (1 row)**: cake gel — composite product

**thickener|bulking agent (1 row)**: psyllium husk powder

**thickener|gelling agent (1 row)**: hpmc vegetarian capsule

**binding agent|thickener|stabiliser (1 row)**: binding agent gum acacia — should have matched INS 414; check why it didn't

**carrier (1 row)**: carrier lactose — lactose has no food additive INS

**propellant (1 row)**: nitrogen — same taxonomy error issue as packaging gas

**antifoaming agent (1 row)**: antifoaming agent — generic class label only

**coating agent (1 row)**: pharmaceutical glaze — pharmaceutical grade, not food INS

---

### Bucket C — Generic class labels only (no substance, probably drop)

**emulsifier (12 rows)**: emulsifier, emulsifiers, emulsfying, emuslifier (typos), cloudifier, mayonnaise, emulsifier vegetable origin, sunflower creamer — no specific INS substance identifiable

**acidity regulator (9 rows)**: acidity regulator, acidity regulators, acid regulator, acidity regulator ins, acidity regulators ns, alkaline salt, distilled vinegar, synthetic vinegar, magnesium malate

**stabiliser (3 rows)**: stabilizer ns 415, stabilizer hydrolysed vegetable protein, stabilizer hydrolyzed vegetable protein — hydrolysed vegetable protein has no INS

---

## Recommended next steps (in order)

1. **Bulk reclassify the 17 antioxidant rows** — split to `fortification_agent` / `health_supplement` (clear list above, no taxonomy work needed)
2. **Bulk reclassify preservative misclassified rows** — probiotics → `health_supplement`, selenite → `fortification_agent`
3. **Bulk reclassify FOS/prebiotic rows** from `sweetener|bulking agent` → `health_supplement`
4. **Decide on non-INS policy** — do these get a `non-INS` flag section in taxonomy, or a separate non-INS file?
5. **Check INS 552, 381 etc.** for anticaking — 3–4 more entries may be addable to taxonomy
6. **Flag or drop generic class labels** — rows with no substance are label noise

---

## Key files

| File | State |
|---|---|
| `core/all_variants_working.csv` | 1,666 rows — active working file |
| `core/all_variants.csv` | 2,292 rows — Tier 1, never touch |
| `additives/additives_taxonomy.json` | 158 entries (was 153) |
| `health_supplement/pending_enrichment.csv` | 14 rows — stub open, not yet sessioned |
| `fortification_agent/experiment.log.md` | Up to date |
