# IFID Dairy Session — Todo
## Updated: 2026-04-14

Start next session by reading handoff.tmp.md, then tick off items here as you go.

---

## Immediate: before any new insertions

- [ ] **Back-migrate source names to `{family} {specific}` format**
      Rename in TypeDB: `cow milk` → `milk cow`, `buffalo milk` → `milk buffalo`,
      `camel milk` → `milk camel`. Schema unchanged; only source-name attribute values.
      Do this before any new form-of relations reference these sources.

---

## Open questions — resolve before inserting dependent forms

- [ ] **Is "whey" declared bare on Indian labels?**
      If yes: `whey` gets its own form-id node; WPC and WPI are form-of(whey).
      If no: WPC and WPI go directly form-of source (milk cow, milk buffalo).
      This gates the entire protein fraction insertion path.

- [ ] **Does form-level variety-of appear outside dairy?**
      Test candidates: spice varieties (e.g. cinnamon types), vinegar types, fermented
      products. If the pattern recurs in at least one other category → general mechanism,
      keep. If dairy-only → may still be valid but note the limited precedent.

- [ ] **Is paneer a cheese subtype or a standalone form?**
      FSSAI defines paneer under a separate standard from cheese. It is produced by
      coagulation + pressing without rennet or ageing. `variety-of(paneer, cheese)`
      may be wrong — paneer is arguably not a sub-type of cheese but a distinct
      coagulated milk product. Confirm before inserting.

---

## Done this session ✓

- [x] Insert 6 dairy form-id nodes: butter, ghee, cream, curd, yogurt, milk-powder
- [x] Insert 12 form-of relations (6 forms × milk cow + milk buffalo)
- [x] Schema change: variety-of extended to ingredient-form → ingredient-form
- [x] Establish source naming convention: `{family} {specific}`
- [x] Establish processing-method hyphenation convention

---

## Next insertion batch — cheese family

Requires variety-of for ingredient-form (schema done). Confirm paneer status first.

- [ ] `cheese` form-id node (declarable bare, is-declarable: true at form level)
- [ ] form-of relations: cheese ← milk cow, milk buffalo (processing-method: coagulation)
- [ ] `mozzarella` form-id node + variety-of(base: cheese, variety: mozzarella)
- [ ] `cheddar` form-id node + variety-of(base: cheese, variety: cheddar)
- [ ] `cottage-cheese` form-id node + variety-of(base: cheese, variety: cottage-cheese)
- [ ] `paneer` form-id node + form-of relations (coagulation + pressing)
      (variety-of cheese only if paneer-as-cheese-subtype is confirmed)

---

## Next insertion batch — remaining dairy forms

- [ ] `skim-milk` — liquid, skimming process, cow + buffalo milk
- [ ] `toned-milk` — liquid, fat standardisation (check processing-method vocabulary)
- [ ] `condensed-milk` — concentrate, evaporation
- [ ] `skim-milk-powder` — powder, skim + spray-drying
- [ ] `sour-cream` — semi-solid, fermentation (confirm FSSAI status vs plain cream)
- [ ] `ice-cream` — gel? confirm matter-state; composition is multi-ingredient question

---

## Protein fraction batch — blocked on whey question

- [ ] `whey` form-id (only if bare-declarable — see open question)
- [ ] `whey-protein-concentrate` (WPC)
- [ ] `whey-protein-isolate` (WPI)
- [ ] `milk-protein-concentrate` (MPC)
- [ ] `casein`
- [ ] `lactose`

Processing-method for protein fractions:
- WPC: `ultrafiltration`
- WPI: `ultrafiltration` + `ion-exchange` or `diafiltration` (confirm exact value)
- Casein: `isoelectric-precipitation` or `rennet-coagulation` (two routes — confirm)
- Lactose: `crystallisation` (from whey permeate)

---

## Rows to skip / flag permanently

These will never become graph nodes — note here so they are not re-evaluated:

- `whey-peptides` — classified health_supplement, out of RAM scope
- `milk-flavouring` — classified flavouring agent, out of RAM scope
- `sweetened-condensed-milk` variants — flag_compound_product, multi-ingredient
- `mozzarella cheese lodized salt` — multi-source row, not a clean form
- `rennet-casein`, `romano-cheese-enzymes`, `dahi-starter-culture` — fermentation agents;
  scope question: do these belong in RAM or a separate fermentation-agent category?
- `milk-products`, `milk-components` — generic/underdeclared, not IFID-valid
- Brand-specific rows (e.g. `pasteurised amul milk`) — lookup layer only, not graph nodes
