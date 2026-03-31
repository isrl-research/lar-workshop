# EMF Scoring Model

This document explains the EMF model in a simplified way to assist discussion about iSRL-26-0x-R-Metadata [(#6)](https://github.com/isrl-research/sandbox-research/discussions/6) and iSRL-26-04-D-Modelling [(#8)](https://github.com/isrl-research/sandbox-research/discussions/8) for contributors involved in data modelling design decisions. If you have a specific query about the logic behind scoring or nutritional / legal aspects, check the papers listed below and tag @isrl-research/research-core in the relevant thread.

EMF is a scoring system that describes how far a food ingredient has drifted from its original biological source. Three scores — E, M, F — each capture a different dimension of that drift. The full model is described in the main paper and justified in the companion.

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

## Papers

- **Main paper:** Identity, Transformation, and Function: A Tri-Axial Model for the Classification of Food Ingredient Identity
  <https://doi.org/10.5281/zenodo.18714527>

- **Justification companion:** Justification Companion to EMF-Scoring Model
  <https://doi.org/10.5281/zenodo.18713318>