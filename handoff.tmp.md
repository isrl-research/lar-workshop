# Session Handoff — 2026-04-13
## For the next Claude session starting dairy insertion

---

## What you are working on

**Category:** dairy (`dairy/dairy_working.csv`, 122 rows)
**Goal:** Insert dairy ingredient-forms and relations into TypeDB (TypeDB 3.8.0)
**Status:** Design discussion complete. NO data inserted yet. Schema change needed first.

**Start by:** Reading `todo.tmp.md` and ticking off items as you go.
**Also read:** `db/graph.md` (canonical design reasoning), `db/schema.typeql` (current schema),
`decision-2026-04-13.tmp` (decisions made this session).

---

## Current TypeDB state (what is already in the DB)

**Sources (already inserted):**
- `milk` (source, is-declarable: false — taxonomy root)
- `cow milk` (source, is-declarable: true)
- `buffalo milk` (source, is-declarable: true)
- `camel milk` (source, is-declarable: true)
- `wheat`, `bansi wheat` (source)

**Ingredient forms (already inserted):**
- `flour`, `semolina`, `malted-wheat`, `wheat-flakes`

**Relations (already inserted):**
- 6× form-of (wheat/bansi wheat → their forms)
- 1× variety-of (bansi wheat variety-of wheat)

Nothing dairy has been inserted yet.

---

## The single most important thing to remember about how to insert

**The CSV rows are NOT what goes into the graph.**

The CSV contains label-derived strings like "pasteurised toned milk", "dahi starter culture",
"skimmed milk powder". These are research artefacts — the evidence trail for decisions.
What goes into the graph is the CONCLUSION: a structured `(source, form, processing-method)`
triple, expressed as a form-of relation.

"skimmed milk powder" → inserted as:
- form-id node: `skim-milk-powder`
- source: `cow milk` (or buffalo milk — both get their own form-of relation)
- processing-method on form-of: `skim | spray-drying`

The string "skimmed milk powder" lives in the lookup layer only (not built yet — that is fine).
The graph only sees the structured triple.

Every row that is a variant/alias/transliteration of the same thing collapses to ONE
form-id node + ONE or more form-of relations. dahi, yogurt (multiple rows), yoghurt —
all collapse to one (or at most two) form-id nodes + relations. Not one node per row.

---

## Key design decisions already made (see decision-2026-04-13.tmp for full reasoning)

1. **Cheese is declarable bare.** `cheese` is a valid FSSAI declaration. Declaring "mozzarella"
   is a voluntary specificity upgrade. `cheese` gets its own ingredient-form node.

2. **Form-level variety-of.** mozzarella/cheddar/paneer/cottage-cheese connect to `cheese`
   via `variety-of` — the same pattern as Alphonso mango to mango at source level. This
   requires a schema change: `variety-of` currently only connects `source → source`.
   **Schema must be extended before these are inserted.**

3. **Sugars are NOT the same pattern.** Brown vs white sugar = processual distinction →
   processing-method on form-of. NOT form-level variety-of.

4. **Lecithin/oil specificity is source-level.** Sunflower lecithin vs soy lecithin = same
   form, different sources → two form-of paths, one form-id node. No form variety-of.

5. **WPC and WPI are separate form-id nodes.** Different declared identities, different
   regulatory status. Not the same as whole vs refined flour. Both form-of whey
   (if whey is confirmed bare-declarable) or directly form-of source.

6. **Multi-hop chains already work.** `ingredient-form` plays `form-of:origin` in the
   current schema. whey → WPC chain is structurally valid today.

---

## Open questions that MUST be resolved before inserting (in order)

**Q1: Is "whey" declared bare on Indian product labels?**
- If yes → `whey` gets its own ingredient-form node, WPC/WPI are form-of whey
- If no → WPC/WPI go directly form-of cow milk / buffalo milk
- Ask Lalitha before inserting anything in the protein fraction group.

**Q2: Curd vs yogurt — one form-id or two?**
- In India, dahi (curd) and yogurt have separate FSSAI Standards of Identity
- They likely need separate form-id nodes
- But confirm before inserting — if Lalitha says they're the same declared form, they
  collapse to one node and the aliases go to lookup layer.

**Q3: Form-level variety-of in other categories?**
- Before finalizing the schema extension for variety-of at form level, check whether
  the pattern appears in spices, marine, or fermentation product categories
- If it does → design the extension to be general, not dairy-specific
- If it doesn't → still extend it, but note it as a dairy-introduced mechanism

---

## Rows to NOT insert (keep out of the graph)

- `whey-peptides` — health supplement, out of RAM scope
- `milk-flavouring` — flavouring agent category, not RAM
- `sweetened condensed milk` variants — flagged compound products (multi-ingredient)
- `mozzarella cheese lodized salt` — multi-source, not a clean form
- `rennet casein`, `romano cheese enzymes`, `dahi starter culture`, `cultured cream`,
  `active lactic cultures` — fermentation agents; ask Lalitha whether these go in RAM
  or a separate fermentation-agent category
- `milk products`, `milk components` — generic/underdeclared, not valid IFID forms
- `pasteurised amul milk` — brand name variant, lookup layer only, no graph node

---

## The schema change needed before cheese subtypes can be inserted

Current schema (db/schema.typeql):
```
relation variety-of,
  relates base,
  relates variety;
```
Currently, only `source` plays `variety-of:base` and `variety-of:variety`.

Change needed: `ingredient-form` must also be able to play both roles.
Use `typedb-expert` skill when writing the TypeQL for this.

Do NOT implement the schema change until Q3 (other-category check) is resolved.

---

## Skills to load for the next session

- `ifid-graph-critic` — load first, always, for any schema/design discussion
- `typedb-expert` — load when writing actual TypeQL
- `typedb-expert` has TypeDB 3.8.0 syntax. Do NOT use 2.x syntax.

---

## File locations

| File | What it is |
|---|---|
| `db/graph.md` | Primary reference. Read before anything else. |
| `db/schema.typeql` | Current schema |
| `dairy/dairy_working.csv` | 122-row dairy working file |
| `decision-2026-04-13.tmp` | Reasoning from this session |
| `todo.tmp.md` | Ordered task list for next session |
| `emf-info.md` | EMF axis definitions if needed |
