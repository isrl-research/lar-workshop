# Schema Design Decisions

Rationale for structural choices in the IFID TypeDB schema.
Add a new entry whenever a non-obvious decision is made so future sessions
(and future contributors) know *why* it is the way it is, not just *what* it is.

---

## 001 — Nodes exist only for declared ingredient forms

A node in the graph represents a form that actually gets declared on a food label.
Intermediate processing steps that are never declared do not get nodes.

**Example:** wheat → wheat flour → wheat gluten.
Both wheat flour and wheat gluten appear on labels, so both get nodes.
The intermediate "gluten dough before drying" never appears on a label — no node.

**Consequence:** graph depth reflects ingredient genealogy, not process chemistry.
Some chains are shallow (wheat → semolina, one hop).
Some are deeper (wheat → wheat flour → wheat gluten → vital wheat gluten).
That is correct. It mirrors how ingredients are actually declared and understood.

---

## 002 — Processing decisions live on the `derived-from` relation, not on the node

The *difference* between whole wheat flour and refined wheat flour is the milling grade.
That difference is a property of the *path from wheat to that form*, not of the form itself.

If milling-grade were on the node, you would need to reconstruct the path from scattered
attributes. With it on the relation, the path *is the graph* — you traverse it and read
what each hop says.

---

## 003 — Subtypes are driven by functional class, not source

`flour-form`, `flavouring-form`, `oil-form` etc. are subtypes of `ingredient-form`.
The subtype is determined by the functional class (F-axis in EMF), not the source.

**Why:** `milling-grade` is a property of something whose identity is defined by milling.
Putting it on a generic `ingredient-form` supertype would allow nonsensical combinations
(olive oil with milling-grade: whole). Each subtype owns only the attributes that are
semantically valid for that class.

**Flavouring example:** `flavouring-type` (natural / nature-identical / artificial) is an
attribute of `flavouring-form`, inherited from the ingredient's function — not from its
source. Natural mango flavouring gets `flavouring-type: natural` because of what it is
legally/functionally, not because mango is natural.

---

## 004 — `derived-from` allows chaining (ingredient-form can be a base)

An `ingredient-form` can be the `base` in a `derived-from` relation, not just `source`.
This is required because some forms derive from other forms, not directly from the source.

**Example:** iron-fortified whole wheat flour derives from whole wheat flour (not wheat).
**Example:** wheat gluten derives from wheat flour (not wheat).

Without this, the schema would force all forms to connect directly to the raw source,
losing the intermediate genealogy.

---

## 005 — Role of EMF in schema design

EMF (Energy–Matter–Function) is a scoring framework that answers two questions:
1. Is X a variant of ingredient Y, or a standalone ingredient?
   → answered by EMF distance: close vectors = variant, drifted vectors = standalone
2. Which subtype does an ingredient form belong to?
   → answered by F-axis: high F (function-first) drives subtype by functional class;
     low F (source-first) drives subtype by matter form

EMF scores are **analysis artefacts** — they live in the CSVs as evidence for decisions.
They do not live in TypeDB. What enters TypeDB is the *conclusion*:
a `derived-from` relation (for variants/derived forms) or a standalone node.

EMF is not a rabbit hole. It provides the deterministic structure that replaces intuition
for the variant-vs-standalone decision. Without it, every case is a judgement call.
With it, you have a repeatable rule. The schema would have been impossible to design
consistently without it.

---

## 006 — Subtype rule: depth must be real, not invented to fit

A subtype is only justified if it has genuine internal categorical depth — attributes whose
values represent meaningfully distinct, independently declarable categories.

`flour-form` is justified: `milling-grade` has real depth (whole / refined / fortified).
These are distinct grades with nutritional and legal implications that brands must declare.

`semolina` was initially placed in `flour-form` with `milling-grade: "semolina"` — but
this was circular. The category was invented to hold the thing. Semolina has no internal
depth: there is no "whole semolina" vs "refined semolina" distinction that matters.
Semolina's identity is fully captured by `matter-state: "coarse grits"` +
`processing-method: "milling"` on the `derived-from` relation.

**Rule:** if you find yourself inventing a milling-grade (or equivalent) value that is
just the ingredient's own name, the ingredient does not belong in that subtype.

---

## 008 — `source-type` vocabulary: plant / dairy / animal, not natural

`source-type` must carry dietary classification, not biological origin.

**Wrong:** `natural` — all three of plant, dairy, and animal are natural. The value
conveys no information that isn't already derivable from the entity existing.

**Correct vocabulary:**

| Value | Dietary status |
|---|---|
| `plant` | vegetarian |
| `dairy` | vegetarian (lacto) |
| `animal` | non-vegetarian |
| `marine` | non-vegetarian (fish, shellfish — worth separating from animal, common on Indian labels) |
| `fungal` | vegetarian (mushrooms, yeast) |
| `microbial` | vegetarian (bacterial cultures, fermentation starters) |
| `synthetic` | case-by-case — some are veg-certified, some are not |

`natural` is derivable: anything that isn't `synthetic` is natural.
Derivable values carry no information — they should not appear in `source-type`.

**Migration:** wheat and bansi wheat were inserted with `source-type: natural`.
Both updated to `source-type: plant` at the start of the dairy session (2026-04-09).

---

## 009 — `derived-from` is replaced by `ingredient-declaration`

The `derived-from` relation conflated two things: what a form *is* (its processing and
matter-state) and what *source* it comes from. These are separate concerns.

**New relation:**
```
relation ingredient-declaration,
  relates source,          ← played by source entity
  relates form,            ← played by ingredient-form entity
  owns processing-method @card(0..);
```

`ingredient-form` nodes are now truly source-agnostic. `bansi semolina` as a named
node is gone — it becomes `ingredient-declaration(source: bansi wheat, form: semolina,
processing-method: coarse milling)`. The form node `semolina` exists once.

**Why form→form derivation chains are not needed:**
Every declared ingredient traces to a source. Intermediate processing steps
(e.g., whole wheat flour as an intermediate before wheat gluten) are manufacturing
details, not label declarations. They live as `processing-method` values on the
`ingredient-declaration`, not as separate relation hops.

**Migration required:**
All existing `derived-from` instances in the wheat data must be converted to
`ingredient-declaration` instances. `bansi semolina` node must be deleted.
`db/schema.typeql` and `db/data.typedb` are stale until this migration runs.

---

## 010 — lookup layer is separate from the TypeDB model

Label strings, multilingual names, and brand-specific variant names do not live in
TypeDB. They live in a separate lookup layer whose sole job is to map strings to
`(source, form)` pairs.

**Why:**
"bansi semolina", "bansi rawa", "बान्सी रवा" are all names for the same structured
combination `(bansi wheat, semolina)`. The names are surface declarations. The
`(source, form)` pair is the identity. Keeping them in separate layers means:

- Adding Tamil/Kannada/Hindi names never touches the TypeDB schema
- The model is queried by stakeholders using structured (source, form) traversal
- Variant noise from label strings never enters the core model
- Translation is an index problem, not a schema problem

**Consequence for ingredient-form canonical-name:**
The `canonical-name @key` on `ingredient-form` is a model-internal identifier
(e.g., "semolina"), not a user-facing label string. User-facing strings live in the
lookup layer only.

---

## 007 — matter-state must be set explicitly; no auto-enforcement in TypeDB

TypeDB has no triggers. When inserting a `flour-form`, `matter-state` is not auto-set.
Every insertion of a typed ingredient-form must explicitly include `has matter-state`.

**App-layer constraint (TODO):** insertion logic for any `flour-form` must always include:
- `has matter-state "flour"` for whole/refined grades
- `has matter-state "coarse grits"` for semolina-equivalent forms (if semolina ever
  becomes flour-form, which it currently is not — see 006)

TypeDB functions could derive matter-state at read time, but cannot write it.
Until an app layer enforces this, treat it as a required field convention, not a
schema-enforced constraint.
