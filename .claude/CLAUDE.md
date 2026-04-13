# IFID Workshop — Project Context

This is the iSRL IFID (Indian Food Informatics Data Project) research workspace.
The goal is to build a structured, graph-backed ingredient database where any way
a brand or consumer might think of an ingredient — name, language, form, function —
resolves to the correct node.

## Important: never guess acronyms or definitions

If an acronym, term, or proper noun is unfamiliar or ambiguous, **ask Lalitha directly**.
Do not fill in a plausible-sounding expansion. IFID = Indian Food Informatics Data Project
is an example of exactly the kind of thing that would have been confidently wrong.

---

## What IFID is

A structured form-based database of food ingredients. Brands fill in ingredient
declarations via a structured form — not free text. The form enforces the right level
of specificity at input, so underdeclared ingredients (e.g. "vegetable oil") cannot
be submitted. The downstream parsing mess that plagues other food databases does not
happen here because the input was never unstructured to begin with.

IFID is a substrate — it defines what a correct ingredient declaration looks like.
Other services resolve up to it. It does not accommodate label noise; it replaces
the conditions that produce label noise.

---

## TypeDB graph — active build

**Use the `ifid-graph-critic` skill at the start of any session involving schema
decisions, data modelling, or ingredient taxonomy structure. This is the default
posture for graph work: discuss and stress-test before implementing.**

**Also use `typedb-expert` for all TypeQL syntax, queries, and driver usage.**
Version pinned to TypeDB 3.8.0.

The design reasoning for every structural decision lives in **`db/graph.md`**.
Read it before any graph session. The schema (`db/schema.typeql`) and data
(`db/data.typedb`) are consequences of the reasoning there — not the source of truth.

### What is built

Schema: `source`, `ingredient-form`, `form-of` (with `processing-method`), `variety-of`.
No subtypes of `ingredient-form` currently exist.

Data inserted: wheat, bansi wheat, milk (taxonomy root, not declarable), cow milk,
buffalo milk, camel milk. Forms: flour, semolina, malted-wheat, wheat-flakes.
Relations: 6× form-of, 1× variety-of (bansi wheat sub wheat).

### Core model decisions (reasoning in graph.md)

- `ingredient-form` is source-agnostic. Source-specific names live in the lookup layer only.
- Processing differences between forms (whole vs refined flour) belong on the `form-of`
  relation as `processing-method`, not on the node.
- `is-declarable` on `source` separates taxonomy roots (`milk`) from valid form-of origins
  (`cow milk`). The input form enforces this — underdeclared sources cannot be submitted.
- `is-allergen` on `source`, not on `ingredient-form`. Allergenicity is source-determined.
- `variety-of` is a separate relation from `form-of` — taxonomic vs processual edges.
- EMF scores never enter TypeDB. Only conclusions (relations or standalone nodes) do.
- Subtypes require genuine internal categorical depth. Do not create subtypes speculatively.

### What is not in TypeDB (by design)

- EMF scores — analysis artefacts, live in CSVs
- Label strings, multilingual names, brand aliases — live in the lookup layer (not yet built)
- Intermediate processing steps that are never declared on a label

---

## EMF framework

**Read `emf-info.md` for exact scores and axis values.**

Tri-axial scoring: E (Anthropogenic Energy), M (Matter), F (Functional).
Used to answer one question deterministically: is X a variant of Y, or a standalone?
Close EMF vectors → variant. Drifted vectors → standalone (possibly `derived-from`).

EMF scores are analysis artefacts. They live in CSVs. They never enter TypeDB.
What enters TypeDB is the conclusion: a relation or a standalone node.

---

## Category pipeline — current status

Each category follows: raw data → working CSV → taxonomy JSON → TypeDB schema.

| Category | Status |
|---|---|
| `raw_agricultural_material/` | TypeDB schema live. Wheat + dairy sources inserted. **Active focus.** |
| `additives/` | Track A done. 158-entry taxonomy JSON. Source field still unstructured string — blocked on RAM taxonomy completing first. |
| `colors/` | Track A done. Clean INS CSV + non-INS variants CSV. |
| `fortification_agent/` | Track A done. 68 canonical agents. Pending: variant resolution + 5 SME flags. |
| `health_supplement/` | `pending_enrichment.csv` open (14 rows). No taxonomy. |
| `solvent/` | README only. One entry (ethanol). No taxonomy. |
| `core/` | `all_variants_working.csv` — 1,666 rows. `all_variants.csv` — 2,292 rows, Tier 1, never touch. |

---

## Why raw_agricultural_material is the current priority

The `source` field across all categories is an unstructured string list
(`["corn", "wheat", "soybean"]`). Until there are proper `source` nodes in the graph,
converting any other category to TypeDB creates tech debt — every category would need
remodelling when sources get structured. RAM builds the foundation that unblocks everything.

---

## Key file paths

| File | What it is |
|---|---|
| `db/graph.md` | **Primary reference.** Full reasoning behind every schema decision. Read before any graph session. |
| `db/schema.typeql` | Current TypeDB schema (consequence of graph.md) |
| `db/data.typedb` | Current TypeDB data (binary) |
| `emf-info.md` | EMF axis definitions and score values |
| `core/all_variants_working.csv` | 1,666 rows — master working file, all categories |
| `additives/additives_taxonomy.json` | 158-entry additive taxonomy |
| `raw_agricultural_material/wheat_working.csv` | 30 wheat variant rows with EMF scores |

---

## Workflow conventions

- Working files stay in category folder until session closes, then snapshot to `cp/`
- Never touch `core/all_variants.csv` (Tier 1 — raw source of truth)
- Commit after each meaningful session with descriptive message
- The `isrl-file-lifecycle` skill manages session open/close protocol
- Use `ifid-graph-critic` for all graph/schema design sessions
- Use `typedb-expert` for all TypeQL syntax and query work
