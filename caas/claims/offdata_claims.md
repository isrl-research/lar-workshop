# OFF Data Claims
Source: caas/core/off-data/products-raw.tsv
Verified: 2026-03-16

---

## Claims

- 01. Of 19,748 rows in the raw OpenFoodFacts export, 4,104 pass the minimum filter (brand, product name in English, ingredient text in English), a pass rate of 20.78 percent.

- 02. ingredients_text_en is the only ingredient column with coverage above 1 percent. It has 4,592 non-null rows (23.25 percent). All 29 other language columns combined add 69 additional rows.

- 03. 6,905 rows have both a brand identifier and an English product name but no ingredient text in any language. The data gap is at the ingredient field, not at product identity.

- 04. The four core macronutrient fields have null rates between 65.61 and 66.00 percent across all 19,748 rows: energy_value 65.61 percent (6,792 non-null), fat_value 66.00 percent (6,715 non-null), proteins_value 65.89 percent (6,737 non-null), carbohydrates_value 65.77 percent (6,759 non-null).

- 05. The three Hindi language columns have the following non-null counts across 19,748 rows: product_name_hi 111, ingredients_text_hi 11, generic_name_hi 2.

- 06. Replacing product_name_en OR generic_name_en with product_name_en alone as a filter condition reduces the output from 4,105 rows to 4,104 rows. generic_name_en contributes one unique row.

- 07. The raw dataset has 486 columns. The filtered dataset retains 4 columns: product_name_en, brands, brands_tags, and ingredients_text_en.

---

## Evidence Per Claim

### Claim 01
Raw row count: 19,748. Filter applied: brands OR brands_tags non-empty, AND product_name_en non-empty, AND ingredients_text_en non-empty. Rows passing all three conditions: 4,104. Pass rate: 20.78 percent. Rows removed: 15,644 (79.22 percent).

### Claim 02
ingredients_text_en: 4,592 non-null rows. ingredients_text_fr: 94. ingredients_text_de: 15. ingredients_text_hi: 11. All remaining 26 language columns: 69 rows combined when de-duplicated against English coverage. Pooling all 30 ingredient language columns yields 4,661 rows with any ingredient text, against 4,592 for English alone.

### Claim 03
Rows passing (brands OR brands_tags) AND product_name_en: 11,009. Of these, rows also passing ingredients_text_en: 4,104. Rows with brand and name but no ingredient text: 6,905.

### Claim 04
Null rates computed on the full 19,748-row dataset. energy_value: 12,956 null, 6,792 non-null, 65.61 percent null. fat_value: 13,033 null, 6,715 non-null, 66.00 percent null. proteins_value: 13,011 null, 6,737 non-null, 65.89 percent null. carbohydrates_value: 12,989 null, 6,759 non-null, 65.77 percent null.

### Claim 05
Non-null counts on the full 19,748-row dataset. product_name_hi: 111 non-null, 19,637 null, 99.44 percent null. ingredients_text_hi: 11 non-null, 19,737 null, 99.94 percent null. generic_name_hi: 2 non-null, 19,746 null, 99.99 percent null.

### Claim 06
Filter A: (brands OR brands_tags) AND (product_name_en OR generic_name_en) AND ingredients_text_en. Result: 4,105 rows. Filter B: (brands OR brands_tags) AND product_name_en AND ingredients_text_en. Result: 4,104 rows. Difference: 1 row. That row had generic_name_en populated and product_name_en empty. In the 4,105-row set, generic_name_en has 451 non-null values (10.99 percent non-null, 89.01 percent null).

### Claim 07
Raw column count: 486. Columns retained after filter: product_name_en, brands, brands_tags, ingredients_text_en. Column count in working dataset: 4. The 482 removed columns include all non-English name and ingredient variants, all nutrient sub-fields, environmental scores, packaging fields, and contributor metadata.
