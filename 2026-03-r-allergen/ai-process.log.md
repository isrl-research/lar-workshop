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

## [2026-03-31, continued into next session] — PDF reading: 7 source PDFs read, all paper files rewritten

**Initiated by:** Researcher ("i have added source pdfs for those that i could find, go through in them in detail and refine the documents as necessary")
**What happened:** Installed `pdfminer.six` (poppler not available without sudo). Read 7 source PDFs from `source-pdfs/`. Rewrote 7 paper files with full-text data: P02, P04, P05, P06, P07, P08, P10. Updated `allergen.papertable.qmd` with new access status, relevance summaries updated to reflect actual extracted content, P06 DOI resolved.

**Files touched:** `allergen.papertable.qmd`, `papers/mahesh-et-al-2023b.qmd`, `papers/krishna-et-al-2020.qmd`, `papers/bhattacharya-et-al-2018.qmd`, `papers/saraswathi-2022.qmd`, `papers/milana-et-al-2025.qmd`, `papers/leung-et-al-2024.qmd`, `papers/devdas-et-al-2018.qmd`

**AI-initiated decisions:**
- Identified that the PDF labelled `AAM_1211461_Mahesh,P_2023.pdf` is P02 (Allergic Diseases in India), not P01 (sensitisation paper) — confirmed by extracting first 500 chars.
- Flagged P06 (Saraswathi 2022) as a secondary source that should not be cited independently for any India-specific figure — its India numbers trace to the same EuroPrevall studies already in P02 and P04. Researcher did not ask for this assessment; it follows from the DON'T KNOW instruction and source quality discipline.
- Table 2 in P04 (Krishna 2020) reproduced in full in the paper file — 13 individual Indian food allergen studies across multiple cities and cohorts. This was not explicitly requested but is the most useful collation of primary India data in the set.
- Noted that eggplant allergen data (P05) has two active confounders: histamine content in stored eggplant causing false-positive SPTs, and possible pesticide residue. Added explicit flag in paper file.
- Table data in two PDFs (P07 Milana, P08 Leung) was garbled in extraction due to rotated table text. Prose sections used instead; acknowledged where table data is incomplete.

**Revised or changed:** All 7 paper files are substantially expanded. P06 (Saraswathi) previously assessed as full-text via web fetch — re-assessed after PDF read as lower evidential weight than initially appeared.

**Still pending:** P01 (awaiting PDF from PA Mahesh); P03 and P09 (no PDFs found).

---

## [2026-03-31 ~evening IST] — session open

**Initiated by:** Researcher
**What happened:** Session started. Researcher asked for three skills to be created: `allergen-researcher` (immunology specialist persona), `ai-process-logger` (accountability layer), and `allergen-research-workflow` (paper handling protocol). All three written and active.
**Why:** Explicit researcher instruction.
**Revised or changed:** nothing
**Files touched:** `~/.claude/skills/allergen-researcher/SKILL.md`, `~/.claude/skills/ai-process-logger/SKILL.md`, `~/.claude/skills/allergen-research-workflow/SKILL.md`, `2026-03-r-allergen/ai-process.log.md` (this file, created now)

---
