# EMF Scoring Model

This document explains the EMF model in a simplified way to assist discussion about iSRL-26-0x-R-Metadata [(#6)](https://github.com/isrl-research/sandbox-research/discussions/6) and iSRL-26-04-D-Modelling [(#8)](https://github.com/isrl-research/sandbox-research/discussions/8) for contributors involved in data modelling design decisions. If you have a specific query about the logic behind scoring or nutritional / legal aspects, check the papers listed below and tag @isrl-research/research-core in the relevant thread.

EMF is a scoring system that describes how far a food ingredient has drifted from its original biological source. Three scores — E, M, F — each capture a different dimension of that drift. The full model is described in the main paper and justified in the companion.

> **Prototype data notice:** The `tagged_variants.csv` file released alongside this document is a work-in-progress prototype. Scores, zone assignments, and tags may contain errors and are not final. Use it to explore the modelling problem and schema design — do not treat it as a validated dataset or cite it in analysis.

---

## The Three Axes

### E — Anthropogenic Energy Score `[0, 1]`

What kind of process was applied? Lower scores = simple physical steps; higher scores = chemical synthesis.

```
processes = [sorting, washing, chilling, de-husking, milling, cold pressing, churning,
             pasteurization, clarification, fermentation, roasting, refining, fractionation,
             solvent extraction, interesterification, hydrogenation, acetylation,
             synthetic vanillin, synthetic flavors]
```

### M — Matter Score `[0, 1]`

How different is the ingredient's physical/chemical form from what it started as?

```
matter_states = [whole/fresh pieces, cut/sliced pieces, pulp/puree, coarse grits,
                 flour/fine powder, flakes, dense block, concentrate, powder, juice,
                 whey powder, skim/defatted meal, starch flour, oil, fat fraction,
                 protein concentrate, protein isolate, granules, extract/oleoresin,
                 oleoresin, emulsifier powder, essential oil, modified starch powder,
                 crystalline chemical]
```

### F — Functional Score `[0, 1]`

Is the ingredient's identity defined by its source or by what it does in a product? Especially does law view it as a variant of source or by what it does Low F = source-first identity. High F = function-first identity.

```
functional_classes = [base ingredient, taste profile / spice, lipid base, bulking agent,
                      humectant, firming agent, raising agent, flavouring agent, thickener,
                      stabiliser, gelling agent, sweetener, foaming agent, colour, emulsifier,
                      anticaking agent, acidity regulator, antioxidant, preservative,
                      antifoaming agent, sequestrant, bleaching agent, flour treatment agent,
                      carrier, propellant, packaging gas]
```

---

## N — Natural States

The botanical part of the source organism the ingredient came from. This is not a scored axis — it records which plant part (or animal/microbial equivalent) the ingredient originates from.

```
natural_states = [fruit, seed, bark, root, leaf, stem, flower, bud, resin, gum, latex,
                  rhizome, bulb, tuber, pod, hull, husk, peel, rind, pith, pulp, kernel,
                  nut, berry, grain, spore, shoot, tendril, stamen, pistil, sap, exudate]
```

---

## Using the CSV Files

Three companion CSVs ship with this model, one per scored axis:

| File | Columns | Rows |
|---|---|---|
| `e_scores.csv` | `tag, score` | 19 process tags |
| `m_scores.csv` | `tag, score` | 24 matter-state tags |
| `f_scores.csv` | `tag, score` | 26 functional-class tags (3 scores left blank — see below) |

**Merge on `tag`** to attach scores to any ingredient dataset that has been tagged with EMF labels:

```python
import pandas as pd

e = pd.read_csv('e_scores.csv')
m = pd.read_csv('m_scores.csv')
f = pd.read_csv('f_scores.csv')

# df must have columns named 'e_tag', 'm_tag', 'f_tag' (or rename as needed)
df = pd.merge(df, e.rename(columns={'tag': 'e_tag', 'score': 'E'}), on='e_tag', how='left')
df = pd.merge(df, m.rename(columns={'tag': 'm_tag', 'score': 'M'}), on='m_tag', how='left')
df = pd.merge(df, f.rename(columns={'tag': 'f_tag', 'score': 'F'}), on='f_tag', how='left')
```

**Blank scores in f_scores.csv:** `flavouring agent`, `sweetener`, and `colour` have no score assigned in the justification companion. Rows for these tags are present with an empty `score` field. Treat them as `NaN` in analysis until score assignment. Likewise for any tag prefixed with `?` like `?hydrolysis`.

---

## tagged_variants.csv — Schema Reference

> **Prototype notice:** This file contains work-in-progress data. Scores, zone assignments, and tags are not finalised and may contain errors. Use for schema design and modelling exploration only.

This file contains one row per ingredient variant. Each row records the variant name, its source, the explicit and could-be tags for each EMF axis, the resulting scores, zone assignment, and two flags for uncertainty and unresolved tags.

### Columns

| Column | Type | Description |
|---|---|---|
| `variant` | string | The ingredient as it appears on the label (e.g. `refined sunflower oil`) |
| `source` | string | Canonical source(s), pipe-separated if multiple (e.g. `palm \| soybean \| sunflower`) |
| `e_explicit` | string / NULL | Process tag directly inferrable from the variant name. NULL if none. |
| `m_explicit` | string / NULL | Matter state tag directly inferrable from the variant name. NULL if none. |
| `f_explicit` | string / NULL | Functional class tag directly inferrable from the variant name. NULL if none. |
| `e_could_be` | string / NULL | Plausible process tag(s) not explicitly stated, pipe-separated if multiple. NULL if none. |
| `m_could_be` | string / NULL | Plausible matter state tag(s) not explicitly stated, pipe-separated if multiple. NULL if none. |
| `f_could_be` | string / NULL | Plausible functional class tag(s) not explicitly stated, pipe-separated if multiple. NULL if none. |
| `e_score` | float | E score from explicit tag. 0 if no explicit process tag. |
| `m_score` | float | M score from explicit tag. 0 if no explicit matter state tag. |
| `f_score` | float | F score from explicit tag. 0 if no explicit functional class tag. |
| `e_max` | float | Highest E score across explicit and could-be tags. |
| `m_max` | float | Highest M score across explicit and could-be tags. |
| `f_max` | float | Highest F score across explicit and could-be tags. |
| `d_min` | float | Minimum composite EMF distance using explicit scores only. |
| `d_max` | float | Maximum composite EMF distance using explicit + could-be scores. |
| `zone` | integer | Zone assignment (1, 2, or 3) based on composite score. |
| `uncertain` | boolean | True if d_min and d_max span a zone boundary — zone assignment may shift once tags are resolved. |
| `question_tags` | boolean | True if any tag is prefixed with `?` indicating an unvalidated or disputed process/state. |

### Example rows

```
variant,source,e_explicit,m_explicit,f_explicit,e_could_be,m_could_be,f_could_be,e_score,m_score,f_score,e_max,m_max,f_max,d_min,d_max,zone,uncertain,question_tags
oil,palm | soybean | sunflower | groundnut,NULL,oil,lipid base,cold pressing|refining|solvent extraction,NULL,NULL,0,0.7,0.22,0.82,0.7,0.22,0.298,0.544,1,True,False
snf,milk,NULL,powder,base ingredient,NULL,concentrate,NULL,0,0.42,0.12,0,0.42,0.12,0.174,0.174,1,False,False
tvp,soybean,NULL,protein concentrate,base ingredient,?extrusion,NULL,NULL,0,0.74,0.12,0.6,0.74,0.12,0.27,0.45,1,True,True
dha,algae | fish,NULL,oil,lipid base,solvent extraction,NULL,NULL,0,0.7,0.22,0.82,0.7,0.22,0.298,0.544,1,True,False
```

**Reading `uncertain: True`:** the variant `oil` has `d_min = 0.298` and `d_max = 0.544`. If could-be tags are confirmed, the composite score shifts significantly. Zone assignment should be treated as provisional until explicit tags are resolved.

**Reading `question_tags: True`:** the variant `tvp` has `?extrusion` as a could-be process tag. `?` prefix means the tag is not yet in the validated process list and needs flagging before it can be scored. See the Flagging Discrepancy section below.

---

## Flagging Discrepancy

If you see any discrepancy in the scores in the CSV files here vs the justification report — please create an issue or PR to fix it. For immediate analysis, treat the justification report as ground truth and resolve conflicts accordingly.

If a tag appears in the data that is not in the validated lists above, prefix it with `?` and raise it as an issue. New tags are not added to the validated lists without review.

---

## Papers

- **Main paper:** Identity, Transformation, and Function: A Tri-Axial Model for the Classification of Food Ingredient Identity
  <https://doi.org/10.5281/zenodo.18714527>

- **Justification companion:** Justification Companion to EMF-Scoring Model
  <https://doi.org/10.5281/zenodo.18713318>
