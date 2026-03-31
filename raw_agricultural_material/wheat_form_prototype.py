"""
wheat_form_prototype.py — IFID Wheat Entry CLI

Diagnostic prototype: guided brand entry form for wheat ingredients.
Surfaces schema gaps by classifying every wheat_working.csv row against
what the structured form can and cannot accept.

Run from workshop root:
    python3 raw_agricultural_material/wheat_form_prototype.py
"""

import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
except ImportError:
    print("rich is required. Install it with:  pip install rich")
    sys.exit(1)

import json
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to workshop root)
# ---------------------------------------------------------------------------
WHEAT_CSV = Path("raw_agricultural_material/wheat_working.csv")
TAX_JSON = Path("fortification_agent/fortification_taxonomy.json")


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, dict]:
    """Load wheat working CSV and fortification taxonomy."""
    if not WHEAT_CSV.exists():
        print(f"[ERROR] Not found: {WHEAT_CSV}  (run from workshop root)")
        sys.exit(1)
    if not TAX_JSON.exists():
        print(f"[ERROR] Not found: {TAX_JSON}  (run from workshop root)")
        sys.exit(1)

    df = pd.read_csv(WHEAT_CSV)
    with open(TAX_JSON) as f:
        tax = json.load(f)
    return df, tax


def get_wheat_agents(tax: dict) -> list[dict]:
    """Return all agents where 'wheat flour' in fssai_mandate_food."""
    agents_dict = tax.get("fortification_agents", tax)
    result = []
    for key, agent in agents_dict.items():
        if "wheat flour" in agent.get("fssai_mandate_food", []):
            result.append({**agent, "_key": key})
    return result


# ---------------------------------------------------------------------------
# Break classification
# ---------------------------------------------------------------------------

BAKING_EXTRUSION_TERMS = ("baking", "extrusion")


def _field(row, col) -> str:
    """Return str value of a field, or '' if NaN."""
    v = row.get(col, "")
    if pd.isna(v):
        return ""
    return str(v).strip().lower()


def _has_process(row, *cols) -> bool:
    for col in cols:
        val = _field(row, col)
        for term in BAKING_EXTRUSION_TERMS:
            if term in val:
                return True
    return False


def classify_row(row, duplicate_variants: set) -> tuple[str, str]:
    """
    Return (break_type, reason) for a wheat_working row.
    Returns ('OK', '') if classifiable via the form.

    Priority: DUPLICATE_VARIANT → OUT_OF_SCOPE → FERMENTATION_PATH
              → DATA_MODEL_MISMATCH → COMPOUND_PARSE_FAIL
              → NO_FORM_PATH → AGENT_AMBIGUITY → OK
    """
    variant = str(row.get("variant", "")).strip()
    v_lower = variant.lower()

    e_explicit = _field(row, "e_explicit")
    e_could_be = _field(row, "e_could_be")
    m_explicit = _field(row, "m_explicit")
    milling_grade = _field(row, "milling_grade")
    question_tags_raw = str(row.get("question_tags", "False")).strip()
    question_tags = question_tags_raw == "True"

    # 1. DUPLICATE_VARIANT
    if variant in duplicate_variants:
        return ("DUPLICATE_VARIANT", f"'{variant}' appears more than once in source data")

    # 2. OUT_OF_SCOPE — baked / extruded product
    if _has_process(row, "e_explicit", "e_could_be"):
        return ("OUT_OF_SCOPE", "baked or extruded product — not a raw agricultural entry")

    # 3. FERMENTATION_PATH
    if "fermentation" in e_explicit:
        return ("FERMENTATION_PATH", "fermentation processing — fortification question does not apply")

    # 4. DATA_MODEL_MISMATCH — 'fortified' stored as a milling_grade
    if milling_grade == "fortified":
        return (
            "DATA_MODEL_MISMATCH",
            "'fortified' is a processing grade in the data but a separate checkbox in the form",
        )

    # 5. COMPOUND_PARSE_FAIL — multiple ingredient/product concepts in one string
    compound_signals = (
        v_lower.startswith("noodle"),
        "wheat flour" in v_lower and v_lower.count("wheat") > 1 and not v_lower.startswith("whole wheat"),
    )
    if any(compound_signals):
        return ("COMPOUND_PARSE_FAIL", "multiple ingredient or product concepts concatenated — cannot parse into single structured entry")

    # 6. NO_FORM_PATH — no form information anywhere
    if not m_explicit and not milling_grade and not e_explicit:
        return ("NO_FORM_PATH", "no m_explicit, no milling_grade, no e_explicit — cannot map to any form choice")

    # 7. AGENT_AMBIGUITY — iron or ferrous declared without specifying form
    if v_lower.endswith(" iron") or ("ferrous" in v_lower and "fumarate" not in v_lower and "sulphate" not in v_lower):
        return (
            "AGENT_AMBIGUITY",
            "iron declared without specifying form — taxonomy has Electrolytic Iron, Ferrous Fumarate, Ferrous Sulphate; no canonical mapping",
        )

    return ("OK", "")


def get_duplicate_variants(df: pd.DataFrame) -> set:
    counts = df["variant"].value_counts()
    return set(counts[counts > 1].index)


def render_break_report(df: pd.DataFrame, console: Console) -> None:
    """Render rich Table of all break classifications for all rows."""
    duplicates = get_duplicate_variants(df)

    table = Table(
        title="Break Report — All Wheat Rows",
        box=box.MINIMAL_DOUBLE_HEAD,
        show_lines=True,
        title_style="bold yellow",
    )
    table.add_column("variant", style="cyan", no_wrap=True)
    table.add_column("break_type", no_wrap=True)
    table.add_column("reason", overflow="fold")

    severity_style = {
        "OK": "dim green",
        "OUT_OF_SCOPE": "yellow",
        "COMPOUND_PARSE_FAIL": "yellow",
        "NO_FORM_PATH": "yellow",
        "FERMENTATION_PATH": "cyan",
        "DATA_MODEL_MISMATCH": "red",
        "AGENT_AMBIGUITY": "red",
        "DUPLICATE_VARIANT": "dim",
    }

    ok_count = 0
    break_count = 0

    for _, row in df.iterrows():
        break_type, reason = classify_row(row, duplicates)
        style = severity_style.get(break_type, "white")
        if break_type == "OK":
            ok_count += 1
        else:
            break_count += 1
        table.add_row(
            str(row["variant"]),
            break_type,
            reason if reason else "—",
            style=style,
        )

    console.print()
    console.print(
        Panel(table, style="yellow", subtitle=f"{break_count} breaks  |  {ok_count} OK")
    )


# ---------------------------------------------------------------------------
# Form flow
# ---------------------------------------------------------------------------

FORM_CHOICES = {
    "1": ("whole_grain",         "Whole grain"),
    "2": ("semolina_coarse",     "Semolina / coarse"),
    "3": ("fine_flour_whole",    "Fine flour — whole"),
    "4": ("fine_flour_refined",  "Fine flour — refined"),
    "5": ("flakes",              "Flakes"),
    "6": ("none",                "None of these"),
}

FLOUR_FORMS = {"fine_flour_whole", "fine_flour_refined"}
SEMOLINA_OR_FLOUR = {"semolina_coarse", "fine_flour_whole", "fine_flour_refined"}


def print_step(console: Console, n: int, total: int, title: str) -> None:
    console.print(f"\n[dim]Step {n} of {total}[/dim]  [bold]{title}[/bold]")


def ask_form_choice(console: Console) -> tuple[str, str]:
    console.print()
    for k, (_, label) in FORM_CHOICES.items():
        console.print(f"  [bold cyan][{k}][/bold cyan]  {label}")
    console.print()
    while True:
        choice = Prompt.ask("[dim]Enter number[/dim]", choices=list(FORM_CHOICES.keys()))
        return FORM_CHOICES[choice]


def ask_agents(wheat_agents: list[dict], console: Console) -> list[dict]:
    """Multi-select from wheat flour agents. Returns selected agents."""
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Canonical name")
    table.add_column("Nutrient type")
    table.add_column("Regulatory category")

    for i, a in enumerate(wheat_agents, 1):
        table.add_row(str(i), a["canonical_name"], a["nutrient_type"], a["regulatory_category"])

    console.print(table)

    console.print("[dim]Enter numbers separated by commas (e.g. 1,3,5) — or [bold]all[/bold] for all agents[/dim]")
    while True:
        raw = Prompt.ask("Selected agents").strip()
        if raw.lower() == "all":
            return wheat_agents
        try:
            indices = [int(x.strip()) - 1 for x in raw.split(",")]
            selected = [wheat_agents[i] for i in indices if 0 <= i < len(wheat_agents)]
            if selected:
                return selected
        except (ValueError, IndexError):
            pass
        console.print("[red]Invalid input — try again[/red]")


ZINC_AGENTS = {"zinc_sulphate", "zinc_sulphate_monohydrate"}


def zinc_disambiguation(selected: list[dict], console: Console) -> list[dict]:
    """If zinc class selected, disambiguate between sulphate variants."""
    has_zinc = any(a["_key"] in ZINC_AGENTS for a in selected)
    if not has_zinc:
        return selected

    console.print()
    console.print(
        Panel(
            "[bold yellow]Warning:[/bold yellow] Zinc Sulphate and Zinc Sulphate Monohydrate are "
            "[bold]separate taxonomy entries[/bold] with different regulatory classifications.\n\n"
            "The form requires you to specify which one appears on the label.",
            title="Agent Disambiguation",
            style="yellow",
        )
    )

    zinc_choice = Prompt.ask(
        "Which zinc form?",
        choices=["Zinc Sulphate", "Zinc Sulphate Monohydrate", "Both", "Unsure"],
    )

    # Remove any zinc entries already in selected, then re-add correct one
    non_zinc = [a for a in selected if a["_key"] not in ZINC_AGENTS]

    zinc_map = {a["_key"]: a for a in selected if a["_key"] in ZINC_AGENTS}
    # If zinc entries were not already split, look them up from original list
    # (caller passes the full selected list which may have only one zinc entry)

    if zinc_choice == "Both":
        return selected  # keep whatever zinc entries are in selected
    elif zinc_choice == "Zinc Sulphate":
        zs = next((a for a in selected if a["_key"] == "zinc_sulphate"), None)
        return non_zinc + ([zs] if zs else [])
    elif zinc_choice == "Zinc Sulphate Monohydrate":
        zsm = next((a for a in selected if a["_key"] == "zinc_sulphate_monohydrate"), None)
        return non_zinc + ([zsm] if zsm else [])
    else:  # Unsure
        console.print("[dim]Zinc disambiguation deferred — entry flagged for review.[/dim]")
        for a in selected:
            if a["_key"] in ZINC_AGENTS:
                a["_flag"] = "UNSURE_ZINC_FORM"
        return selected


def render_entry(entry: dict, console: Console) -> None:
    """Render structured IFID entry panel."""
    lines = []
    lines.append(f"[bold]source:[/bold]      {entry.get('source', '—')}")
    lines.append(f"[bold]form:[/bold]        {entry.get('form_label', '—')}")

    fortified = entry.get("fortified")
    if fortified is None:
        lines.append("[bold]fortification:[/bold]  n/a (form does not support fortification)")
    elif fortified:
        agents = entry.get("agents", [])
        agent_names = ", ".join(a["canonical_name"] for a in agents) if agents else "—"
        flags = [a.get("_flag") for a in agents if a.get("_flag")]
        lines.append(f"[bold]fortified:[/bold]   yes")
        lines.append(f"[bold]agents:[/bold]      {agent_names}")
        if flags:
            lines.append(f"[dim yellow]flags:       {', '.join(flags)}[/dim yellow]")
    else:
        lines.append("[bold]fortified:[/bold]   no")

    if entry.get("malted"):
        lines.append("[bold]processing:[/bold]  malted / fermented  [dim](fortification step skipped)[/dim]")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="Structured IFID Entry",
            style="green",
            subtitle="Panel 1 of 2",
        )
    )


def run_form(df: pd.DataFrame, tax: dict, console: Console) -> dict:
    """Main interactive form flow. Returns structured entry dict."""
    wheat_agents = get_wheat_agents(tax)
    entry: dict = {"source": "wheat"}

    console.print()
    console.print(
        Panel(
            "[bold]IFID Ingredient Entry — Wheat[/bold]\n\n"
            "This form captures a single wheat ingredient as a brand would enter it.\n"
            "Source [bold]wheat[/bold] is pre-selected. Navigate structured choices below.\n"
            "A break report follows regardless of the path taken.",
            style="bold blue",
        )
    )

    # -----------------------------------------------------------------------
    # Step 1 — Source (pre-selected)
    # -----------------------------------------------------------------------
    print_step(console, 1, 5, "Source")
    console.print("  [bold green]wheat[/bold green]  [dim](pre-selected — this form is wheat-only)[/dim]")

    # -----------------------------------------------------------------------
    # Step 2 — Physical form
    # -----------------------------------------------------------------------
    print_step(console, 2, 5, "Physical form")
    console.print("[dim]  Derived from m_explicit + milling_grade taxonomy[/dim]")
    console.print("[dim]  Select the best match for the ingredient on the label:[/dim]")

    form_key, form_label = ask_form_choice(console)
    entry["form_key"] = form_key
    entry["form_label"] = form_label

    if form_key == "none":
        console.print()
        console.print(
            Panel(
                "[bold yellow]No form path matched.[/bold yellow]\n\n"
                "This ingredient cannot be entered via the current form. "
                "It will appear in the break report as [bold]OUT_OF_SCOPE[/bold] or [bold]NO_FORM_PATH[/bold].",
                style="yellow",
            )
        )
        entry["fortified"] = None
        render_entry(entry, console)
        return entry

    # -----------------------------------------------------------------------
    # Step 3 — Milling / processing note (semolina or flour only)
    # -----------------------------------------------------------------------
    if form_key in SEMOLINA_OR_FLOUR:
        print_step(console, 3, 5, "Milling / processing note")
        malted = Confirm.ask("Is this malted or fermented?", default=False)
        entry["malted"] = malted
        if malted:
            console.print("[dim]  FERMENTATION_PATH — fortification question does not apply.[/dim]")
            entry["fortified"] = None
            render_entry(entry, console)
            return entry
    else:
        entry["malted"] = False

    # -----------------------------------------------------------------------
    # Step 4 — Fortification (flour only, not malted)
    # -----------------------------------------------------------------------
    if form_key in FLOUR_FORMS:
        print_step(console, 4, 5, "Fortification")
        fortified = Confirm.ask(
            "Is this flour fortified under FSSAI standards?", default=False
        )
        entry["fortified"] = fortified

        if not fortified:
            entry["agents"] = []
            render_entry(entry, console)
            return entry

        # -------------------------------------------------------------------
        # Step 5 — Agent multi-select
        # -------------------------------------------------------------------
        print_step(console, 5, 5, "Fortification agents")
        console.print(
            f"[dim]  Showing {len(wheat_agents)} agents where FSSAI mandate includes wheat flour[/dim]\n"
        )
        selected = ask_agents(wheat_agents, console)

        # Step 5b — Zinc disambiguation
        selected = zinc_disambiguation(selected, console)

        entry["agents"] = selected
    else:
        entry["fortified"] = None
        entry["agents"] = []

    render_entry(entry, console)
    return entry


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    console = Console()
    df, tax = load_data()

    # Run the form
    run_form(df, tax, console)

    # Always show break report
    console.print()
    console.print(
        Panel(
            f"Classifying all [bold]{len(df)}[/bold] rows in wheat_working.csv "
            "against the form's structured paths.\n"
            "[dim]Green = classifiable  |  Yellow = recoverable  |  Red = structural gap[/dim]",
            title="Break Report — Panel 2 of 2",
            style="yellow",
        )
    )
    render_break_report(df, console)

    console.print()
    console.print("[dim]Done.[/dim]\n")


if __name__ == "__main__":
    main()
