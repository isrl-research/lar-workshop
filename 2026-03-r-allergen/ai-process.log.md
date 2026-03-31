# AI Process Log — Allergen Research

This file records what happened in each working session: what was guided by the researcher, what the AI decided independently, and where anything was revised or walked back.

---

## [2026-03-31 ~evening IST] — paper setup: 10 papers logged, DOIs found, individual files created

**Initiated by:** Researcher (provided paper list; instructed to begin paper logging workflow)
**What happened:** Searched for DOIs for all 10 papers. Created individual .qmd files for all 10 papers in `papers/`. Created manuscript skeleton at `allergen-synthesis.qmd`. Updated `allergen.papertable.qmd` with DOIs and access status.
**Why:** Explicit researcher instruction to begin the research workflow with the provided paper list.
**Revised or changed:** Nothing in approach. One AI-initiated decision: added a "source quality" metadata field to each paper file to be transparent about what came from full text vs abstract vs search summary — researcher did not ask for this specifically, but it follows directly from the "DON'T KNOW" instruction.
**Files touched:** `allergen.papertable.qmd`, `allergen-synthesis.qmd`, `ai-process.log.md`, all 10 files in `papers/`

**Access outcome (noted by AI, not guided):** 8 of 10 papers are paywalled. Full text accessed for P04 (PMC open access) and P06 (open journal). Remaining 8: abstract + search summaries only — flagged in each paper file.

---

## [2026-03-31 ~evening IST] — session open

**Initiated by:** Researcher
**What happened:** Session started. Researcher asked for three skills to be created: `allergen-researcher` (immunology specialist persona), `ai-process-logger` (accountability layer), and `allergen-research-workflow` (paper handling protocol). All three written and active.
**Why:** Explicit researcher instruction.
**Revised or changed:** nothing
**Files touched:** `~/.claude/skills/allergen-researcher/SKILL.md`, `~/.claude/skills/ai-process-logger/SKILL.md`, `~/.claude/skills/allergen-research-workflow/SKILL.md`, `2026-03-r-allergen/ai-process.log.md` (this file, created now)

---
