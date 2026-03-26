"""
Reads caas/core/off-data/products-raw.tsv and prints the numbers
reported in offdata_claims.md for direct verification.
"""

from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

TSV = Path(__file__).parent.parent / "core" / "off-data" / "products-raw.tsv"

console.print(f"\n[bold]Source:[/bold] {TSV}")
df = pd.read_csv(TSV, sep="\t", low_memory=False, on_bad_lines="skip")
console.print(f"[bold]Loaded:[/bold] {len(df):,} rows, {len(df.columns):,} columns\n")


def nonempty(series):
    return series.notna() & (series.astype(str).str.strip() != "") & (series.astype(str).str.strip() != "nan")


# ── Claim 01 & 07 ─────────────────────────────────────────────────────────────
console.rule("[bold]Claim 01 + 07 — Filter yield and column reduction")

brand_ok = nonempty(df["brands"]) | nonempty(df["brands_tags"])
name_ok  = nonempty(df["product_name_en"])
ing_ok   = nonempty(df["ingredients_text_en"])
mask     = brand_ok & name_ok & ing_ok

t = Table(box=box.SIMPLE_HEAVY)
t.add_column("Condition", style="cyan")
t.add_column("Rows passing", justify="right")
t.add_column("% of raw", justify="right")

t.add_row("Raw rows",                              f"{len(df):,}",          "100.00%")
t.add_row("brands OR brands_tags non-empty",       f"{brand_ok.sum():,}",   f"{brand_ok.sum()/len(df)*100:.2f}%")
t.add_row("product_name_en non-empty",             f"{name_ok.sum():,}",    f"{name_ok.sum()/len(df)*100:.2f}%")
t.add_row("ingredients_text_en non-empty",         f"{ing_ok.sum():,}",     f"{ing_ok.sum()/len(df)*100:.2f}%")
t.add_row("ALL THREE (final filtered set)",        f"{mask.sum():,}",       f"{mask.sum()/len(df)*100:.2f}%")
t.add_row("Rows removed",                          f"{len(df)-mask.sum():,}", f"{(len(df)-mask.sum())/len(df)*100:.2f}%")

console.print(t)
console.print(f"Raw columns: {len(df.columns)}  |  Retained columns: 4  |  Dropped: {len(df.columns)-4}\n")


# ── Claim 02 ──────────────────────────────────────────────────────────────────
console.rule("[bold]Claim 02 — ingredients_text_* column coverage")

ing_cols = sorted([c for c in df.columns if c.startswith("ingredients_text_")])
ing_counts = {c: nonempty(df[c]).sum() for c in ing_cols}
ing_counts = dict(sorted(ing_counts.items(), key=lambda x: -x[1]))

t2 = Table(box=box.SIMPLE_HEAVY)
t2.add_column("Column", style="cyan")
t2.add_column("Non-null", justify="right")
t2.add_column("% of raw", justify="right")

for col, count in ing_counts.items():
    if count > 0:
        t2.add_row(col, f"{count:,}", f"{count/len(df)*100:.2f}%")

console.print(t2)

en_count  = ing_counts.get("ingredients_text_en", 0)
non_en    = sum(v for k, v in ing_counts.items() if k != "ingredients_text_en")
any_ing   = pd.Series(False, index=df.index)
for c in ing_cols:
    any_ing = any_ing | nonempty(df[c])

console.print(f"ingredients_text_en alone:      {en_count:,} rows")
console.print(f"All other language cols combined (raw sum): {non_en:,} rows")
console.print(f"Any ingredient language (union): {any_ing.sum():,} rows")
console.print(f"Additional rows beyond EN only:  {any_ing.sum() - en_count:,}\n")


# ── Claim 03 ──────────────────────────────────────────────────────────────────
console.rule("[bold]Claim 03 — Brand+name without ingredient text")

brand_and_name       = brand_ok & name_ok
brand_name_with_ing  = brand_and_name & ing_ok
brand_name_no_ing    = brand_and_name & ~ing_ok

t3 = Table(box=box.SIMPLE_HEAVY)
t3.add_column("Segment", style="cyan")
t3.add_column("Rows", justify="right")

t3.add_row("brand AND product_name_en",                    f"{brand_and_name.sum():,}")
t3.add_row("brand AND name AND ingredients_text_en",       f"{brand_name_with_ing.sum():,}")
t3.add_row("brand AND name, NO ingredient text (any lang)",f"{brand_name_no_ing.sum():,}")

console.print(t3)
console.print()


# ── Claim 04 ──────────────────────────────────────────────────────────────────
console.rule("[bold]Claim 04 — Macronutrient null rates (full 19,748 rows)")

nutrients = ["energy_value", "fat_value", "proteins_value", "carbohydrates_value"]

t4 = Table(box=box.SIMPLE_HEAVY)
t4.add_column("Column", style="cyan")
t4.add_column("Non-null", justify="right")
t4.add_column("Null", justify="right")
t4.add_column("Null %", justify="right")

for col in nutrients:
    nn  = df[col].notna().sum()
    nl  = df[col].isna().sum()
    pct = nl / len(df) * 100
    t4.add_row(col, f"{nn:,}", f"{nl:,}", f"{pct:.2f}%")

console.print(t4)
console.print()


# ── Claim 05 ──────────────────────────────────────────────────────────────────
console.rule("[bold]Claim 05 — Hindi column coverage")

hi_cols = ["product_name_hi", "ingredients_text_hi", "generic_name_hi"]

t5 = Table(box=box.SIMPLE_HEAVY)
t5.add_column("Column", style="cyan")
t5.add_column("Non-null", justify="right")
t5.add_column("Null", justify="right")
t5.add_column("Null %", justify="right")

for col in hi_cols:
    nn  = df[col].notna().sum()
    nl  = df[col].isna().sum()
    pct = nl / len(df) * 100
    t5.add_row(col, f"{nn:,}", f"{nl:,}", f"{pct:.2f}%")

console.print(t5)
console.print()


# ── Claim 06 ──────────────────────────────────────────────────────────────────
console.rule("[bold]Claim 06 — generic_name_en contribution")

name_or  = nonempty(df["product_name_en"]) | nonempty(df["generic_name_en"])
mask_or  = brand_ok & name_or & ing_ok
mask_en  = brand_ok & name_ok & ing_ok   # product_name_en only (same as mask above)

filtered_or = df[mask_or]
gen_nn_in_filtered = nonempty(filtered_or["generic_name_en"]).sum()
gen_null_rate = (1 - gen_nn_in_filtered / len(filtered_or)) * 100

t6 = Table(box=box.SIMPLE_HEAVY)
t6.add_column("Filter variant", style="cyan")
t6.add_column("Rows", justify="right")

t6.add_row("name = product_name_en OR generic_name_en", f"{mask_or.sum():,}")
t6.add_row("name = product_name_en only",               f"{mask_en.sum():,}")
t6.add_row("Difference (rows generic_name_en adds)",    f"{mask_or.sum() - mask_en.sum():,}")
t6.add_row("generic_name_en non-null in OR-filtered set", f"{gen_nn_in_filtered:,} / {len(filtered_or):,}  ({100-gen_null_rate:.2f}% non-null)")

console.print(t6)
console.print()
