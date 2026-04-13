# IFID Dairy Session — Todo

Start next session by reading handoff.tmp.md, then tick off items here as you go.

---

## Schema changes (must happen before any dairy data insertion)

- [ ] Extend `variety-of` to connect `ingredient-form → ingredient-form`
      Currently: only `source → source`. Needed for: cheese → mozzarella/cheddar/paneer/cottage-cheese.
      Before implementing: verify pattern appears in at least one other category (spices, marine, fermentation).
      See decision-2026-04-13.tmp Decision 3.

---

## Open questions to resolve before inserting

- [ ] Is "whey" declared bare on Indian labels?
      If yes: `whey` gets its own ingredient-form node, WPC/WPI are form-of whey.
      If no: WPC/WPI go directly form-of source (cow milk etc.), no whey node needed.
      Ask Lalitha or check FSSAI label corpus.

- [ ] Does form-level variety-of appear outside dairy?
      Test candidates: spice types (cinnamon varieties?), vinegar types, fermentation products.
      If pattern recurs → extend variety-of cleanly as a general mechanism.
      If dairy-only → examine whether a simpler approach suffices.

---

## Dairy forms to confirm and insert

Distinct ingredient-form nodes identified from dairy_working.csv (source-agnostic):

### Raw / minimally processed
- [ ] `whey` (if confirmed bare-declarable — see open question above)
- [ ] `skim-milk` (skimmed/partly skimmed milk — grade of liquid milk)
- [ ] `toned-milk` (fat-adjusted liquid milk)
- [ ] `condensed-milk`
- [ ] `milk-powder` (whole milk powder)
- [ ] `skim-milk-powder`
- [ ] `milk-snf` (solids-not-fat — verify if this is its own declared form or always paired)

### Fat-fraction forms
- [ ] `cream`
- [ ] `butter`
- [ ] `ghee`

### Fermented / coagulated forms
- [ ] `curd` (dahi — fermented milk solid, fresh)
- [ ] `yogurt` (fermented, distinct from curd? needs confirmation — see note below)
- [ ] `cheese` (declarable bare — parent node for cheese subtypes)
- [ ] `paneer`
- [ ] `sour-cream`
- [ ] `ice-cream`

### Protein fractions
- [ ] `casein`
- [ ] `whey-protein-concentrate` (WPC — separate form-id from WPI)
- [ ] `whey-protein-isolate` (WPI)
- [ ] `milk-protein-concentrate` (MPC)
- [ ] `lactose`

### Cheese subtypes (form-level variety-of cheese — requires schema change first)
- [ ] `mozzarella`
- [ ] `cheddar`
- [ ] `cottage-cheese`
- [ ] `paneer-cheese` (or is paneer already the right node? confirm with Lalitha)

---

## Note on curd vs yogurt
The CSV has both with identical EMF scores and fermentation process. In India:
- Dahi (curd) = traditional fermented milk, specific bacterial cultures, FSSAI Standard
- Yogurt = distinct FSSAI Standard, often with added cultures, thicker set
Are these ONE form-id or TWO? Confirm before inserting. If two: both are form-of source
via fermentation. If one: dahi/yogurt are lookup-layer aliases for the same form-id.

---

## Rows to skip / flag (do not insert)

- [ ] `whey-peptides` — classified health_supplement, not RAM. Out of scope.
- [ ] `milk-flavouring` — classified flavouring agent. Out of scope for dairy/RAM.
- [ ] `sweetened-condensed-milk` variants — flagged flag_compound_product. Multi-ingredient.
- [ ] `mozzarella cheese lodized salt` — multi-source row. Not a clean form.
- [ ] `rennet-casein`, `romano-cheese-enzymes`, `dahi-starter-culture` — fermentation agents.
      Scope question: do fermentation agents belong in RAM graph or separate?
- [ ] `milk-products`, `milk-components` — generic/underdeclared. Not IFID-valid forms.
- [ ] Brand-specific rows: `pasteurised amul milk` — brand name, not a form. Lookup layer only.

---

## form-of relations to write (after form-id nodes confirmed)

For each form-id: which sources does it connect to, and what processing-method?
Example:
- ghee ← form-of(churning|clarification) ← cow milk
- ghee ← form-of(churning|clarification) ← buffalo milk
- whey-protein-concentrate ← form-of(ultrafiltration-concentration) ← whey (or ← cow milk)

Full relation list: to be drafted once open questions resolved.
