# Experiment Log

---

## [19-Mar-2026 20:30 IST] — Fortification Agents Taxonomy Working JSON

Built `fortification-taxonomy/fortification-taxonomy_working.json` from `fortification_agent_working.csv` (72 source rows), distilling it into 53 clean canonical taxonomy entries across four nutrient classes (water-soluble vitamins, fat-soluble vitamins, amino acids, mineral nutrients). Applied all plan decisions: 4 composite/misclassified rows excluded, 15 label-noise and duplicate variants folded into canonical entries, 2 OCR typos corrected (phenylalaline → Phenylalanine, sodium img → Sodium Iodate). All 6 verification checks passed cleanly: 53 entries confirmed, no milling_grade=fortified leak, l-hpc absent, typo corrections in place, and all 72 source rows accounted for via source_row_variants or exclusion list.

---

## [19-Mar-2026 23:45 IST] — Residuals Auto-Resolution: Phase 1–3

Analysed all 262 additive-lane residual rows in `core/all_variants_working.csv` against `additives/additives_taxonomy.json` (153 entries); identified and removed 136 rows across three committed phases. Phase 1 removed 130 confirmed matches (exact, label-prefix, synonym, and typo-corrected variants) after QC filtering 8 false positives from the substring matcher (notably ammonia→150c and sulphite→150d which were caramel colour entries, not the target compounds). Phase 2 manually added 5 missing INS entries (297 Fumaric acid, 319 TBHQ, 321 BHT, 527 Ammonium hydroxide, 968 Erythritol) to the taxonomy with all by_function/by_category/by_source_type indexes updated and JSON validity confirmed; Phase 3 then removed the 6 corresponding rows. Working CSV now at 1,666 rows; 126 residuals remain for decision-call curation (misclassified nutrients, non-INS ingredients, generic class labels).

---

## [19-Mar-2026 22:05 IST] — Core Working CSV Cleanup + Next Category Analysis

Removed all 92 `fortification_agent` rows from `core/all_variants_working.csv` (1,894 → 1,802 rows); verified with wc -l (1,803 lines including header) and grep confirming 0 residual matches. `core/all_variants.csv` (Tier 1) remains untouched at 2,292 rows. Category breakdown printed: top categories are raw_agricultural_material (514), taste profile/spice (333), flavouring agent (200), lipid base (179), processed_ingredient (145); health_supplement sits at 20 rows with stub already in place — confirmed as next session target, with 14 data rows in `health_supplement/pending_enrichment.csv` and README documenting 6 reclassified variants from the fortification session.

---

## [19-Mar-2026 21:15 IST] — Pending Enrichment Review + Taxonomy Expansion + Session Close

Reviewed all 20 rows in `pending_enrichment.csv` against the Phase 1 taxonomy: 5 folded into existing entries (vit. d2, retinyl acetate, retinyl palmitate, pteroylmonoglutamic acid, cupric sulphate/chromium picolinate with descriptor prefix stripped), and 15 added as new canonical entries covering selenium compounds, chromium salts, choline, B5 forms, and additional magnesium/calcium/manganese salts, bringing the taxonomy to 68 total entries. `taxonomy_log.md` created recording 68 fortification agents and 153 additives as of 2026-03-19. Session closed per lifecycle contract: working JSON promoted to `fortification-taxonomy_clean_2026-03-19.json`, cp/ populated with cleaned file, stats script, and README; committed and pushed to origin/main cleanly.

---
