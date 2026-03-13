"""
stats_additives.py
Prints a statistics summary for the additives cleaned dataset.
Run from any directory — reads by path relative to this script.
Requires: pandas, rich
"""

from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

console = Console()

CSV_PATH = Path(__file__).parent / "additives_clean_2026-03-13.csv"

df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

N = len(df)

# ── helpers ──────────────────────────────────────────────────────────────────

def explode_pipe(series):
    return series[series != ""].str.split("|").explode().str.strip()

def table(title, columns, rows, col_styles=None):
    t = Table(title=title, box=box.SIMPLE_HEAD, show_footer=False)
    for i, col in enumerate(columns):
        style = col_styles[i] if col_styles else "default"
        t.add_column(col, style=style)
    for row in rows:
        t.add_row(*[str(x) for x in row])
    return t


# ── 1. overview ──────────────────────────────────────────────────────────────

console.print(Panel(
    Text(f"{N} entries  ·  source: additives_clean_2026-03-13.csv", justify="center"),
    title="Additives Taxonomy — Statistics",
    subtitle="iSRL / IFID",
))


# ── 2. source type distribution ──────────────────────────────────────────────

st_counts = df["source_type"].value_counts()
rows = [(k, v, f"{v/N*100:.1f}%") for k, v in st_counts.items()]
console.print(table(
    "Source Type Distribution",
    ["source_type", "n", "%"],
    rows,
    col_styles=["bold cyan", "default", "dim"],
))


# ── 3. codex category distribution ───────────────────────────────────────────

cc_counts = df["codex_category"].value_counts()
rows = [(k, v) for k, v in cc_counts.items()]
console.print(table(
    f"Codex Category Distribution  ({len(cc_counts)} categories)",
    ["codex_category", "n"],
    rows,
    col_styles=["bold cyan", "default"],
))


# ── 4. functional class distribution ─────────────────────────────────────────

all_fc = explode_pipe(df["functional_classes"])
fc_counts = all_fc.value_counts()
multi_fc = (df["functional_classes"].str.split("|").apply(
    lambda x: len([v for v in x if v.strip()]) if isinstance(x, list) else 0
) > 1).sum()

console.print(table(
    f"Functional Classes  ({len(fc_counts)} unique · {len(all_fc)} total assignments · {multi_fc}/{N} entries multi-class)",
    ["functional_class", "n"],
    [(k, v) for k, v in fc_counts.items()],
    col_styles=["bold cyan", "default"],
))


# ── 5. sources coverage ───────────────────────────────────────────────────────

has_sources = (df["sources"] != "").sum()
empty_sources = N - has_sources

by_type = df.groupby("source_type").apply(
    lambda g: (g["sources"] != "").sum()
).reset_index()
by_type.columns = ["source_type", "with_sources"]
by_type["total"] = df.groupby("source_type").size().values
by_type["empty"] = by_type["total"] - by_type["with_sources"]

rows = [(r.source_type, r.with_sources, r.empty, r.total)
        for r in by_type.itertuples()]

console.print(table(
    f"Sources Coverage  ({has_sources}/{N} populated · {empty_sources}/{N} empty)",
    ["source_type", "with sources", "empty", "total"],
    rows,
    col_styles=["bold cyan", "default", "default", "dim"],
))


# ── 6. unique source values ───────────────────────────────────────────────────

all_sources = explode_pipe(df["sources"])
src_counts = all_sources.value_counts()

newsource_flags = [s for s in all_sources if str(s).startswith("?newsource")]

console.print(table(
    f"Top Source Values  ({len(src_counts)} unique · {len(newsource_flags)} ?newsource flags)",
    ["source", "n"],
    [(k, v) for k, v in src_counts.head(20).items()],
    col_styles=["bold cyan", "default"],
))

if newsource_flags:
    console.print(Panel(
        "\n".join(newsource_flags),
        title=f"?newsource flags ({len(newsource_flags)})",
        border_style="yellow",
    ))


# ── 7. structural flags ───────────────────────────────────────────────────────

bio_empty = df[df["source_type"].isin(["plant", "animal"]) & (df["sources"] == "")]
synth_bio_ins = ["161g","1100","1104","575","1102","422","296","1204","1101","620","621","270"]
synth_bio = df[df["ins_number"].isin(synth_bio_ins)]
unclassified = df[df["codex_category"] == "Unclassified"]

flag_rows = [
    ("O-1", f"{len(bio_empty)}", "biological source_type, empty sources",
     ", ".join(bio_empty["ins_number"].tolist())),
    ("O-2", f"{len(synth_bio)}", "source_type=synthetic, biological sources listed",
     ", ".join(synth_bio["ins_number"].tolist())),
    ("O-3", f"{len(unclassified)}", "codex_category=Unclassified",
     ", ".join(unclassified["ins_number"].tolist())),
]

console.print(table(
    "Observed Issues (from 2026-03-13 session)",
    ["ref", "n", "description", "INS numbers"],
    flag_rows,
    col_styles=["bold yellow", "default", "default", "dim"],
))
