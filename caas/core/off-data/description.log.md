# data/ — Raw → Processed TSV Pipeline

This folder holds the four stages of the OpenFoodFacts product dataset, moving from raw export to a validated Indian FMCG subset. The pipeline is driven by `scripts/clean.py`.

## Files

| File | Stage | Rows | Columns | Notes |
|---|---|---|---|---|
| `products-raw.tsv` | Stage 0 | 19,748 | 486 | Original OpenFoodFacts export, unmodified |
| `products-en-columns.tsv` | Stage 1 | 19,748 | 402 | English-language columns retained; `scripts/remove-columns.py` strips the rest |
| `products-en-filtered.tsv` | Stage 2 | ~19,748 | 402 | Rows filtered to require the fields used downstream (product name, ingredients, categories) |
| `products-final.tsv` | Stage 3 | 4,104 | 402 | Validated Indian FMCG products; 20.78% of raw dataset |

## Pipeline

```
products-raw.tsv
  → remove-columns.py     → products-en-columns.tsv
  → clean.py (filter)     → products-en-filtered.tsv
  → clean.py (validate)   → products-final.tsv
```

## Key numbers

- Start: 19,748 rows, 486 columns
- After column pruning: 402 columns retained
- After validation: 4,104 rows (20.78% pass rate)
- Criteria: Indian origin, FMCG category, non-empty ingredient string
