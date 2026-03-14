# Solvent — Category Notes

## What this category covers

Substances whose primary food-relevant role is as a carrier or solvent — not as a nutrient, additive, flavour, or functional ingredient in their own right.

Currently 1 variant: `alcohol` (ethanol from sugarcane/molasses fermentation).

---

## Why alcohol is here

`alcohol` (ethanol) in the IFID dataset carries source attribution: sugarcane | molasses, with `e_explicit: fermentation`. It is a fermentation product, not a fermentation agent. The scoring model assigned `f_score: 0` and `f_max: 0` — no food-function signal was detected.

Nearest alternatives considered and rejected:

| Tag | Reason rejected |
|---|---|
| `fermentation_agent` | That category is for agents that *cause* fermentation (yeast, cultures), not products of it |
| `raw_agricultural_material` | Ethanol is a processed fermentation product, not a raw material |
| `processed_ingredient` | Too broad; obscures the specific solvent/carrier role |
| deletion (like water rows) | Unlike distilled/sparkling water, ethanol appears on ingredient lists in a defined functional role |

Codex Alimentarius and FSSAI classify food-grade ethanol primarily as a solvent and carrier (used in flavour extraction, as a carrying medium for permitted food additives, and as a direct ingredient in alcoholic products). `solvent` is the closest schema-consistent tag.

**Context dependency:** if a future enrichment pass establishes that a specific product's alcohol entry is functioning as a base ingredient for an alcoholic beverage rather than a solvent, reclassification to `processed_ingredient` or a new `base_ingredient` tag should be considered at that point.

---

## Enrichment status

No enrichment session run for this category. 1 variant, low priority. Revisit if additional solvent-class variants surface during triage.
