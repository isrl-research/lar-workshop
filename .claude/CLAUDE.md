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
declarations; the system resolves unstructured strings to canonical structured entries.
The core problem is that the same ingredient appears hundreds of ways on labels
(atta / whole wheat flour / gehun ka atta / fortified wheat flour) and the DB needs
to handle all of them without duplication or lookup failure.

---

## Category pipeline — current status

Each category follows: raw data → working CSV → taxonomy JSON → track-a report → TypeDB schema.

| Category | Status |
|---|---|
| `additives/` | Track A done. 158-entry taxonomy JSON. 126 residual rows in `enrichment_pending.csv` (bucket A reclassifications + non-INS + generic labels). Source field in taxonomy is still an unstructured string — **this is the known tech debt blocking TypeDB conversion**. |
| `colors/` | Track A done. Clean INS CSV + non-INS variants CSV. No pending enrichment. |
| `fortification_agent/` | Track A done. 68 canonical agents. Pending: variant resolution (Step 5) + 5 SME flags. |
| `health_supplement/` | `pending_enrichment.csv` open (14 rows). No taxonomy yet. |
| `raw_agricultural_material/` | `wheat_working.csv` present (30 rows). No taxonomy. **Active focus.** |
| `solvent/` | README only. One entry (ethanol). No taxonomy. |
| `core/` | `all_variants_working.csv` — 1,666 rows, active working file. `all_variants.csv` — 2,292 rows, Tier 1, never touch. |

---

## Why raw_agricultural_material is the current priority

The `source` field across all categories (additives taxonomy, fortification, etc.)
is an unstructured string list (e.g. `["corn", "wheat", "soybean"]`). Until there
is a proper `Source` entity type with structured properties, converting any category
to TypeDB creates tech debt — every category would need to be remodelled when sources
get structured. Building the source taxonomy via `raw_agricultural_material` first
unblocks everything else.

---

## EMF framework

**Read `/home/lalithakanha/isrl-research/workshop/emf-info.md` for exact scores and axis values.**

EMF is a tri-axial scoring system that measures how far an ingredient has drifted
from its original biological source. It was built to answer one specific question
deterministically: **is X a variant of ingredient Y, or a standalone ingredient?**

- **E** (Anthropogenic Energy): what kind of process was applied — low = physical, high = chemical synthesis
- **M** (Matter): how different is the physical/chemical form from the source
- **F** (Functional): is the ingredient's identity source-anchored (F low) or function-anchored (F high)

**The decision rule:** if two ingredient-forms have close EMF vectors → one is a variant
of the other. If EMF vectors have drifted significantly on any axis → they are standalone
ingredients (possibly connected by a `derived-from` relation, but not variants).

Examples:
- milk → milk powder: small EMF drift → variant
- milk → butter: M and F shift substantially → standalone ingredient
- acai berry → acai berry flavouring (nature identical): E and F blow out → standalone, connected by `derived-from`

EMF scores are **analysis artefacts** — they live in the CSVs as evidence for decisions,
not in the TypeDB schema. What goes into TypeDB is the *conclusion*: variant relationship
or standalone node + `derived-from` relation.

---

## TypeDB data model — current thinking (not yet built)

**Version: TypeDB 3.8.0. Use the `typedb-expert` skill for all TypeQL work.**

Core insight: a raw agricultural material (e.g. wheat) simultaneously:
- is a `source` for additives (lecithin comes from soy)
- is an `ingredient` when declared bare on a label ("contains: wheat")
- is the upstream node from which processed forms (atta, maida, sooji) are `derived-from`

This means wheat should be **one entity node playing multiple roles**, not separate
entity types. "Variant vs standalone" is expressed as a **relation** (`derived-from`),
not as subtyping. Subtyping (`milk-powder sub milk`) would be semantically wrong —
milk powder IS-NOT-A milk in the type system.

The `derived-from` relation carries the processing information (milling grade, process
method) as relation-owned attributes, not as entity attributes. Process steps are the
*evidence for* the derived-from conclusion, not first-class entities themselves.

**Open design questions (not yet resolved):**
1. Single entity type with roles vs distinct types with shared supertype
2. Where EMF decomposition lives (probably only in CSV, not TypeDB)
3. How to handle manufactured sub-ingredients (wafer, pasta) vs raw materials — subtype or flag

**Search strategy:** graph traversal at query time is acceptable for now.
A lookup index over all variant combinations can be built later as a separate layer.

---

## Key file paths

| File | What it is |
|---|---|
| `emf-info.md` | EMF axis definitions, process/matter/function score values |
| `core/all_variants_working.csv` | 1,666 rows — master working file, all categories |
| `additives/additives_taxonomy.json` | 158-entry additive taxonomy |
| `raw_agricultural_material/wheat_working.csv` | 30 wheat variant rows with EMF scores |
| `experiment.log.md` | Session log — always update after completing a task |
| `last_session_summary.md` | Last session handoff notes |

---

## Workflow conventions

- Working files stay in category folder until session closes, then snapshot to `cp/`
- Never touch `core/all_variants.csv` (Tier 1 — raw source of truth)
- Commit after each meaningful session with descriptive message
- Log every completed task to `experiment.log.md`
- The `isrl-file-lifecycle` skill manages session open/close protocol
