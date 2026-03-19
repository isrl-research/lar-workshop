"""
Stats reporter for fortification-taxonomy_clean_2026-03-19.json
Run from the cp/ directory: python stats_fortification_taxonomy.py
"""
import json
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

DATA_FILE = Path(__file__).parent / "fortification-taxonomy_clean_2026-03-19.json"

with DATA_FILE.open() as f:
    data = json.load(f)

agents = data["fortification_agents"]

# --- 1. Overview ---
console.print(Panel(
    f"[bold]Total canonical entries:[/bold] {len(agents)}\n"
    f"[bold]Group declarations:[/bold] {sum(1 for a in agents if a['is_group_declaration'])}\n"
    f"[bold]Specific compounds:[/bold] {sum(1 for a in agents if not a['is_group_declaration'])}",
    title="Overview",
    border_style="cyan"
))

# --- 2. By nutrient class ---
by_class = Counter(a["nutrient_class"] for a in agents)
t = Table(title="Entries by Nutrient Class", show_lines=True)
t.add_column("Nutrient Class", style="bold")
t.add_column("Count", justify="right")
t.add_column("% of total", justify="right")
for cls, count in sorted(by_class.items(), key=lambda x: -x[1]):
    t.add_row(cls, str(count), f"{count/len(agents)*100:.1f}%")
console.print(t)

# --- 3. Aliases coverage ---
with_aliases = sum(1 for a in agents if a["aliases"])
t2 = Table(title="Aliases Coverage", show_lines=True)
t2.add_column("Metric")
t2.add_column("Value", justify="right")
t2.add_row("Entries with at least one alias", str(with_aliases))
t2.add_row("Entries with no alias", str(len(agents) - with_aliases))
alias_counts = [len(a["aliases"]) for a in agents if a["aliases"]]
t2.add_row("Max aliases on one entry", str(max(alias_counts)) if alias_counts else "0")
t2.add_row("Mean aliases (entries with any)", f"{sum(alias_counts)/len(alias_counts):.1f}" if alias_counts else "0")
console.print(t2)

# --- 4. Source variant distribution ---
sv_counts = [len(a["source_row_variants"]) for a in agents]
t3 = Table(title="Source Row Variant Coverage", show_lines=True)
t3.add_column("Metric")
t3.add_column("Value", justify="right")
t3.add_row("Total source row variants absorbed", str(sum(sv_counts)))
t3.add_row("Entries mapped from 1 source row", str(sum(1 for c in sv_counts if c == 1)))
t3.add_row("Entries mapped from 2+ source rows", str(sum(1 for c in sv_counts if c >= 2)))
t3.add_row("Max source rows on one entry", str(max(sv_counts)))
console.print(t3)

# --- 5. Source type distribution ---
all_sources = []
for a in agents:
    all_sources.extend(a["source_variants"])
src_counts = Counter(all_sources)
t4 = Table(title="Source Type Distribution (across all entries)", show_lines=True)
t4.add_column("Source")
t4.add_column("Occurrences", justify="right")
for src, cnt in sorted(src_counts.items(), key=lambda x: -x[1]):
    t4.add_row(src, str(cnt))
console.print(t4)

# --- 6. Multi-source entries ---
multi = [(a["canonical_name"], a["source_variants"]) for a in agents if len(a["source_variants"]) > 1]
t5 = Table(title=f"Multi-Source Entries ({len(multi)} entries)", show_lines=True)
t5.add_column("Canonical Name")
t5.add_column("Sources")
for name, srcs in multi:
    t5.add_row(name, ", ".join(srcs))
console.print(t5)
