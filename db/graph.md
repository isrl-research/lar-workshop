# IFID Graph — Design Reasoning

This document records the *why* behind every structural decision in the IFID TypeDB model.
It exists so future sessions can continue without re-deriving decisions that were already
fought through. The schema (`db/schema.typeql`) and data (`db/data.typedb`) are consequences
of what is written here — not the other way around.

---

## The substrate principle — read this first

IFID is not a label parser. It is not downstream of labels. It does not accommodate
what brands currently write and try to resolve it into something structured.

**IFID defines what correct looks like.** It is the substrate — the standard that all
other services must resolve up to. The input mechanism is a structured form. A brand
cannot submit "vegetable oil" — the form requires a source-specific selection before
submission is possible. Underdeclared inputs are not a problem IFID handles; they are
a problem IFID structurally prevents. The downstream "parsing mess" (multilingual strings,
abbreviations, inconsistent naming across labels) does not happen because the input was
never free-text to begin with.

This is the opposite of how most food databases work. Most are built by scraping labels
and normalising noise post-hoc. IFID replaces that approach entirely: correctness is
enforced at input, not recovered after the fact. Unstructured label text is not IFID's
concern — it is the problem that IFID makes unnecessary for any system that uses it.

Everything below flows from this. The graph encodes the standard. The lookup layer (not
yet built) is a separate index for mapping historical or external string representations
to structured `(source, form)` pairs — it serves interoperability with systems that
pre-date IFID, not IFID's own input pipeline.

---

## Why graph, not relational

The same material plays multiple roles simultaneously:
- wheat is a `source` (lecithin comes from soy; atta comes from wheat)
- wheat is an `ingredient` when declared bare ("contains: wheat")
- wheat is the upstream node from which atta, maida, sooji are derived

A relational schema would need a row for each role, with join logic to reconcile them.
A graph represents this naturally: one wheat node, multiple relations, each encoding a
different role in context. Traversal at query time handles the rest.

The graph also encodes genealogy — atta and maida both connect to wheat, so "all wheat
derivatives" is a single traversal query, not a hand-coded union.

---

## Why the difference between forms belongs on the relation, not the node

Whole wheat flour and refined wheat flour look like two different things. They are not.
They are the same *form* (flour) reached by two different *paths* from the same source
(wheat). The difference is the milling process — and milling is something that happened
on the way, not a property of the flour sitting in a bag.

If you put `milling-grade` on the node, you create two separate flour nodes with no
structural connection between them. Querying "all wheat flours" requires knowing both
node identities in advance. The graph cannot tell you they are related — you already
have to know.

If you put `processing-method` on the `form-of` relation, whole wheat flour and refined
wheat flour are the same `flour` node reached via different edges:
`(wheat → flour, processing-method: milling-whole)` and
`(wheat → flour, processing-method: milling-refined)`.
"All wheat flours" is a single traversal from wheat through `form-of` to flour. The path
*is* the information.

**The general rule:** if the difference between two things is a process that happened
between them, put it on the edge. If the difference is intrinsic to what the thing *is*,
put it on the node.

---

## Why `ingredient-form` is source-agnostic

The early model had source-specific form nodes: `cow-toned-milk`, `buffalo-toned-milk`.
This was wrong for three reasons:

1. It baked naming into structure. The name "buffalo toned milk" is a label string.
   The *thing* is `(buffalo milk, toned milk)` — a structured pair. These are different
   levels of abstraction and they should not live in the same place.

2. It broke traversal. With three disconnected nodes, querying "all toned milk" requires
   knowing all three names. There is no graph path from one to another. The graph has
   lost the information that they are the same *form*.

3. It would explode combinatorially. Every new source would create new form nodes.
   Eventually you have hundreds of nodes that are all just the same form with a different
   source prefix in the name.

The correct model: one `toned-milk` form node. Three `form-of` relation instances from
three source nodes. The source-specific name ("buffalo toned milk") lives in the lookup
layer only, mapping that string to the structured pair `(buffalo milk, toned milk)`.

`form-id` — the key on `ingredient-form` — is a model-internal identifier. It is not
a display name, not a label string, not user-facing. Display names live in the lookup
layer.

---

## Why the lookup layer is entirely separate from TypeDB

"bansi semolina", "bansi rawa", "बान्सी रवा" are three surface names for the same
structured identity: `(bansi wheat, semolina)`. Adding a new language should not require
touching the graph. It is a string-mapping problem, not a schema problem.

The lookup layer maps strings → `(source, form)` pairs. TypeDB is queried using
structured pairs. These are two different systems. Keeping them separate means:

- The graph never sees label noise
- Adding multilingual names, brand aliases, or regional variants is an index operation,
  not a schema migration
- The model stays clean regardless of how many label variants exist in the wild

---

## Why nodes only exist for declared ingredient forms

A node represents a form that actually gets declared on a label. Intermediate processing
steps that are never declared do not get nodes.

Wheat gluten is declared. "Gluten dough before drying" is never declared — it is a
manufacturing intermediate. It gets no node. The processing steps that produced wheat
gluten from wheat flour are encoded as `processing-method` values on the `form-of`
relation, not as separate hops in the graph.

This keeps graph depth proportional to ingredient genealogy as understood by brands and
consumers — not to process chemistry as understood by food technologists. The graph should
answer label questions, not factory questions.

---

## Why subtypes need genuine internal depth

A subtype is justified only if it has attributes whose values represent meaningfully
distinct, independently important categories — categories that affect regulatory,
dietary, or functional classification.

`flour-form` was initially created with a `milling-grade` attribute (whole / refined /
fortified). It was later removed. Why? Because once milling-grade was correctly recognised
as a processing characteristic — something that belongs on the `form-of` relation — the
subtype had nothing left to own. A subtype with nothing to own does not earn its place.

The test: if you find yourself inventing an attribute value that is just the ingredient's
own name (e.g., `milling-grade: "semolina"`), the ingredient does not belong in that
subtype. Semolina has no internal depth — there is no "whole semolina" vs "refined
semolina" distinction that matters dietarily or regulatorily. Semolina's identity is fully
captured by `matter-state: coarse grits` + `processing-method: milling-coarse` on `form-of`.

Do not create a subtype to make an entry fit somewhere. Surface the question instead.

---

## Why `is-declarable` exists on `source`

The substrate principle creates a tension: some sources exist in the graph for traversal
purposes but are not themselves valid declaration targets.

`milk` is an example. It is the taxonomy root for `cow milk`, `buffalo milk`, `camel milk`,
which hang off it via `variety-of`. It exists because you need to traverse the source
family. But a `form-of` relation should never terminate at `milk` as origin — "milk" is
underdeclared by IFID's standard. Which milk? The dietary and regulatory classification
(veg, halal, kosher) depends entirely on the answer.

`is-declarable: false` marks taxonomy roots. `is-declarable: true` marks valid `form-of`
origins. This is enforced at the application layer. New sources enter the graph as
declarable or non-declarable when added — no schema change required.

**What determines the declarable floor:** three axes. If source matters for (1) dietary
classification (veg/non-veg, halal, kosher), or (2) regulatory distinction (FSSAI treats
sources differently), or (3) functional behaviour (the ingredient performs differently
depending on source) — then specificity at that level is mandatory. The IFID input form
enforces this: a brand cannot reach submission without specifying a source that meets
the declarable floor. "Vegetable oil" is not a selectable option — the form requires
which oil.

---

## Why `is-allergen` lives on `source`, not on `ingredient-form`

Allergenicity in Indian food labelling is source-determined. Wheat starch is an allergen;
corn starch is not. The difference is the source — not the form. An allergen flag on the
form node would be meaningless because the same form (starch) would need different flags
depending on the source it came from.

One flag on the source node captures this correctly. The allergenicity propagates to all
forms derived from that source via graph traversal — no duplication, no inconsistency.

Edge cases (e.g., highly refined wheat oil where some regulations grant exemption) are
handled at the application layer, not in the schema. The schema encodes the conservative
default — if the source is an allergen, everything derived from it inherits that until
explicitly exempted downstream.

---

## Why `source-type` vocabulary excludes "natural"

`source-type` exists to carry dietary classification — the information that determines
whether an ingredient is vegetarian, vegan, halal, or kosher. Valid values:
`plant`, `dairy`, `animal`, `marine`, `fungal`, `microbial`, `synthetic`.

`natural` is derivable: anything that is not `synthetic` is natural. A derivable value
carries no information. Including it would be noise — it tells you nothing that the entity's
existence doesn't already imply. Every attribute value must earn its place by encoding
something that cannot be inferred.

---

## Why EMF scores never enter TypeDB

EMF (Energy–Matter–Function) is a tri-axial scoring framework that answers one question
deterministically: is X a variant of ingredient Y, or a standalone ingredient? Close EMF
vectors → variant. Drifted vectors → standalone (possibly connected by `derived-from`,
but not the same node).

EMF scores are analysis artefacts. They live in the CSVs as the evidence trail for
decisions made during taxonomy work. Once a decision is made — "semolina is a standalone
form, not a variant of flour" — the score has done its job. What enters TypeDB is the
conclusion: a `form-of` relation (for derived forms) or a standalone node (for standalones).

Storing the score would be storing the working, not the result. The graph encodes results.

EMF is also what makes the variant-vs-standalone decision repeatable and non-arbitrary.
Without it, every case is a judgement call. With it, there is a rule. The schema's
structural cleanliness is a direct consequence of having that rule — it forced every
early intuition about subtyping into a testable framework and eliminated several wrong
turns before they became structural debt.

---

## Why `variety-of` is a separate relation from `form-of`

`bansi wheat` is a botanical variety of wheat — it is not a processed form of wheat.
The relationship between them is taxonomic (genus/species/variety), not processual
(source → transformation → form). These are fundamentally different kinds of edges.

`form-of` encodes: a source underwent a process and became a form.
`variety-of` encodes: this source is a taxonomic sub-type of that source.

Conflating them would make traversal ambiguous. "All forms of wheat" and "all varieties
of wheat" are different queries with different answers, and they should remain so.

A variety can be the origin in its own `form-of` relations. `bansi wheat → semolina
(milling-coarse)` is a valid form-of. The variety node stands on its own as a source.

---

## The two things the schema does not do (by design)

**It does not parse.** No label string ever enters TypeDB. No unstructured text ever
touches IFID at any level. The input is a structured form; the output is a structured
graph. There is no parsing step because there is nothing to parse.

**It does not contain working.** EMF scores, taxonomy flags, SME notes, pipeline status —
these live in CSVs and working files. The graph only holds conclusions that have been
committed as part of the standard.
