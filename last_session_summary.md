# Last Session Summary — 2026-04-09

## What this session was about

A design session — no TypeDB inserts. The session resolved two open questions from the
wheat build (source-type vocabulary, fortification deferral) and then produced a fundamental
schema redesign driven by the dairy category challenge. The new architecture (ingredient-declaration
relation + lookup layer) is agreed in design but not yet implemented in TypeDB.

---

## What was done

### File changes
- `core/all_variants_working.csv`: 1,666 → 1,660 rows — deleted 6 encoded wheat forms
  (semolina, wheat flakes, malted wheat, whole wheat flour ×2, refined wheat flour)
- `dairy/dairy_working.csv`: created, 122 rows extracted from core (see stats below)
- `raw_agricultural_material/tql/DESIGN.md`: added decisions 008, 009, 010

### TypeQL written but NOT yet run in TypeDB
Source-type update for wheat and bansi wheat (still needs to be executed):
```typeql
match $s isa source, has source-name "wheat", has source-type $st;
update $s has source-type = "plant";

match $s isa source, has source-name "bansi wheat", has source-type $st;
update $s has source-type = "plant";
```

---

## dairy_working.csv stats (122 rows)

| f_revised | rows |
|---|---|
| processed_ingredient | 67 |
| raw_agricultural_material | 25 |
| lipid base | 17 |
| fermentation_agent | 7 |
| flag_compound_product | 2 |
| sweetener / health_supplement / carrier / flavouring | 4 |

dairy_product_subtype already tagged on 32 rows: hard_cheese (6), paneer (6), yogurt (6),
fresh_curd (4), soft_cheese (3), heat_concentrated (3), fermented_cream (2), others.
119/122 rows have source=milk. buffalo milk and camel milk have 1 row each.

---

## Key design decisions made (see DESIGN.md 008–010 for full rationale)

### 008 — source-type vocabulary
`natural` is gone. Valid values: `plant`, `dairy`, `animal`, `marine`, `fungal`,
`microbial`, `synthetic`. Dietary classification is now derivable from source-type.

### 009 — ingredient-declaration replaces derived-from
`derived-from` is removed. Replaced by `ingredient-declaration` relation:
- relates `source` (source entity)
- relates `form` (ingredient-form entity — source-agnostic)
- owns `processing-method @card(0..)`

`ingredient-form` nodes are now truly source-agnostic. `bansi semolina` as a node is
gone — it becomes `ingredient-declaration(source: bansi wheat, form: semolina)`.
`variety-of` stays untouched — biological variety between sources, unchanged.

### 010 — lookup layer (separate from TypeDB)
Label strings, multilingual names, and brand-specific variant names live in a separate
lookup layer, not in the TypeDB model. The lookup layer maps strings → (source, form)
pairs. TypeDB never sees "bansi semolina" as a name — it only sees the structured
(bansi wheat, semolina) declaration. This means translation and variant resolution
never require schema changes.

---

## What the heuristic settled on (source variety nodes)

> A source variety gets its own source node when it appears as a declared ingredient
> on a label. Derived-form nodes for that variety are created lazily — only when a
> label actually declares that specific (source, form) combination.

Cow milk, buffalo milk, camel milk are independent source nodes (variety-of milk)
because they appear on labels as raw ingredient declarations. Their derived forms
(toned, standardised, ghee, paneer) all hang off the canonical source via
ingredient-declaration. Variety-specific derived forms (camel milk powder) get nodes
only when a label explicitly declares them.

---

## Next session: dairy

**Start with:**
1. Run the two source-type update queries for wheat and bansi wheat
2. Implement the schema redesign in TypeDB:
   - Remove `derived-from` relation
   - Add `ingredient-declaration` relation (source + form + processing-method)
   - Remove `ingredient-form` plays derived-from roles
   - Migrate existing wheat data: convert derived-from instances → ingredient-declaration instances
   - Delete `bansi semolina` node, replace with ingredient-declaration(bansi wheat, semolina)
3. Begin dairy source nodes: `milk` (canonical), `cow milk`, `buffalo milk`, `camel milk`
4. Begin dairy ingredient-form nodes: the 25 raw_agricultural_material rows in dairy_working.csv
   are the first target

**Open question before dairy forms:**
Does `is-allergen` on the `source` entity still work, or does it need to move to
`ingredient-declaration`? Wheat starch (allergen) vs corn starch (not allergen) — the
allergen flag belongs to the (source, form) combination, not the source alone.
Resolve this before inserting dairy forms.

---

## Key files

| File | State |
|---|---|
| `db/schema.typeql` | Stale — reflects old derived-from model. Needs full rewrite next session. |
| `db/data.typedb` | Stale — wheat data uses derived-from. Migration required. |
| `raw_agricultural_material/wheat_working.csv` | 1 row remaining (fortified wheat flour iron, still blocked on nutrient-agent) |
| `dairy/dairy_working.csv` | 122 rows, ready for analysis |
| `raw_agricultural_material/tql/DESIGN.md` | Up to date — decisions 001–010 |
