# Session Handoff — 2026-04-14
## For the next Claude session continuing dairy insertion

---

## What you are working on

**Category:** dairy (`dairy/dairy_working.csv`, 122 rows)
**Goal:** Continue inserting dairy ingredient-forms and relations into TypeDB (TypeDB 3.8.0)
**Status:** First batch inserted. 6 forms + 12 relations in DB. Schema change (variety-of
for ingredient-form) done. See decision-2026-04-14.tmp for full reasoning.

**Start by:** Reading `todo.tmp.md` for current state, then `decision-2026-04-14.tmp`
for today's decisions, then `decision-2026-04-13.tmp` for the prior session's structural
decisions. Also read `db/graph.md` (canonical design reasoning) and `db/schema.typeql`.

---

## Naming conventions — CRITICAL, do not deviate

**Sources:** `{family} {specific}` format. `milk cow`, not `cow milk`. `milk buffalo`,
not `buffalo milk`. All sources follow this pattern.

**Processing-method values:** hyphenated, no spaces. `spray-drying` not `spray drying`.
`whole-milling` not `whole milling`. Check `ref/processing-method_list.csv` — the CSV
still has spaces; use hyphenated form regardless.

**Back-migration needed:** The three milk sources currently in the DB still have old
format names (`cow milk`, `buffalo milk`, `camel milk`). These need to be updated to
`milk cow`, `milk buffalo`, `milk camel` before any new relations are inserted that
reference them. Do this first.

---

## Current TypeDB state

**Sources in DB:**
- `milk` (is-declarable: false — taxonomy root)
- `milk cow`, `milk buffalo`, `milk camel`
- `wheat`, `bansi wheat`

**Ingredient forms in DB:**
- Wheat: `flour`, `semolina`, `malted-wheat`, `wheat-flakes`
- Dairy: `butter`, `ghee`, `cream`, `curd`, `yogurt`, `milk-powder`

**Relations in DB:**
- 6× wheat form-of (wheat/bansi wheat → their forms)
- 1× variety-of (bansi wheat variety-of wheat)
- 12× dairy form-of (butter/ghee/cream/curd/yogurt/milk-powder × cow milk + buffalo milk)

**Schema state:**
- `variety-of` now connects both `source → source` AND `ingredient-form → ingredient-form`
- All other schema unchanged from 2026-04-13

---

## The most important thing to remember about how to insert

The CSV rows are NOT what goes into the graph. The CSV contains label-derived strings —
research artefacts. What goes into the graph is the CONCLUSION: a structured
`(source, form, processing-method)` triple. Variants, aliases, and transliterations
collapse to one form-id node + one or more form-of relations.

"Malai" and "cream" are the same form-id if they have the same EMF vector and
processing path. The string "malai" lives in the lookup layer only.

---

## What to do next (priority order)

1. **Resolve open question: is whey bare-declared?** — This gates the entire WPC/WPI
   insertion path. Check FSSAI label corpus or ask Lalitha. If whey IS bare-declared:
   whey gets its own form-id node, and WPC/WPI are form-of(whey). If NOT: WPC/WPI go
   directly form-of source.

3. **Insert cheese + cheese subtypes** — Schema now supports variety-of for ingredient-form.
   `cheese` as a form-id node (declarable bare). `mozzarella`, `cheddar`, `cottage-cheese`
   as form-id nodes, each connected to `cheese` via variety-of. Paneer is separate
   (coagulation + pressing, no ageing — a distinct Indian form, not a cheese subtype in
   FSSAI terms; confirm before using variety-of here).

4. **Insert next clean batch** — paneer, condensed-milk, skim-milk, toned-milk, cream-cheese.
   See todo.tmp.md for full list.

5. **Resolve form-level variety-of outside dairy** — test whether the pattern appears in
   spices, fermented forms, or marine-derived ingredients. If it does, the variety-of
   mechanism is general; if not, it stays a dairy-specific application.

---

## Files for this category

- `dairy/tql/01_dairy_forms.tql` — form-id node insertions (run first)
- `dairy/tql/02_dairy_relations.tql` — form-of relations (run after 01)
- `dairy/dairy_working.csv` — 122-row working file, source of truth for what's in scope
