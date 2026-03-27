"""
variant_class_analysis.py
--------------------------
Rule-based signal/noise classification for IFID variants.

Run from workshop root:
    python3 core/variant_class_analysis.py

Outputs:
  - core/all_variants_working.csv  (new column: variant_signal_class)
  - core/variant_class_report.csv
  - Terminal rich report
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box
from rich.rule import Rule

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
CORE_DIR = ROOT / "core"
PRIMARY_CSV = CORE_DIR / "all_variants_working.csv"
REPORT_CSV = CORE_DIR / "variant_class_report.csv"
FORTIFICATION_CSV = ROOT / "fortification_agent" / "fortification_agent_working.csv"
WHEAT_CSV = ROOT / "raw_agricultural_material" / "wheat_working.csv"

# ---------------------------------------------------------------------------
# Vocabulary dictionaries
# ---------------------------------------------------------------------------

TRANSLITERATION_VOCAB: set[str] = {
    "atta", "maida", "sooji", "rava", "rawa", "suji", "ghee", "dahi",
    "khoa", "mishri", "kakvi", "poha", "chirva", "besan", "jeera",
    "methi", "haldi", "ajwain", "hing", "kesar", "elaichi", "namak",
    "shakkar", "papad", "bansi", "tulsi", "amla", "jamun", "mosambi",
    "navsadar", "naushadar", "nushadar", "papad khar", "ragi", "urad",
    "chana", "toor", "moong", "masoor", "kalanamak", "khandsari",
    "sharkara", "navsadar", "paua", "sago",
    # Extended Indian food vocab
    "isabgol", "kalonji", "mulethi", "maricha", "nannari", "vallarai",
    "pudina", "khand", "mishri", "gur", "shakkar", "khandsari",
    "badam", "pista", "kaju", "anjeer", "khajur", "meva",
    "imli", "kokum", "aamchur", "anardana",
    "dalchini", "laung", "tejpatta", "jaiphal", "javitri",
    "saunf", "kalongi", "radhuni",
    # Longer Indian/regional names
    "athimathuram", "sauncharnamak", "shveta jiraka",
    "vallarai keerai", "nannari ver", "mulethi root",
    "kasuri", "bajra", "jowar", "nachni", "rajgira",
    "singhara", "rajma", "kabuli", "matki", "kulith",
    "amchur", "chironji", "makana", "makhana", "lotus",
    "paneer",
}

# OCR/corruption swaps: corrupted → canonical
OCR_SWAPS: dict[str, str] = {
    "paim": "palm",
    "sait": "salt",
    "salz": "salt",
    "palmolien": "palmolein",
    "palmoléin": "palmolein",
    "wheatflour": "wheat flour",
    "palmolein ": "palmolein",
    "palm olein": "palmolein",
    "anistar": "anise",
    "vannila": "vanilla",
    "costarch": "cornstarch",
    "carot": "carrot",
}

FORM_WORDS: set[str] = {
    "flour", "powder", "oil", "oils", "paste", "cream", "flakes", "grits",
    "meal", "extract", "concentrate", "puree", "juice", "starch",
    "bran", "germ", "isolate", "hydrolysate", "syrup", "pellets",
    "butter", "fat", "wax", "resin", "fiber", "fibre", "residue",
    "cake", "press cake", "marc", "hull", "husk", "chaff",
    "butterfat", "whey", "snf", "protein", "casein", "lactose",
    "molasses", "treacle", "vinegar", "curd", "culture", "serum",
    "ghee", "dahi", "water", "liquor", "milk", "mass", "nibs",
    "petal", "seed", "seeds", "leaf", "leaves", "bark", "root",
    "grit", "grits", "flake", "flakes", "chip", "chips",
    "crumb", "crumbs", "granule", "granules", "pellet", "pellets",
    "gel", "gum", "wax", "resin", "mucilage",
    # Additional form terms
    "sauce", "solids", "crispies", "crisps", "sticks", "nuts",
    "stearin", "gelatin", "gelatine", "gluten", "dextrin", "dextrose",
    "whitener", "cheese", "honey", "sugar", "dal", "dhal",
    "dices", "dice", "peels", "peel", "zest", "rind",
    "wafer", "biscuit", "cracker", "crisp",
    "beans", "grain", "grains", "kernel", "kernels",
    "drink", "beverage", "infusion", "decoction",
    "slurry", "emulsion", "suspension", "solution",
    "fats", "oils", "waxes",
    "semolina", "rava",
    "salt", "flavouring", "flavoring", "flavour", "flavor",
    "agent", "agents", "additive", "additives", "enzyme", "enzymes",
    "distillate", "rennet", "coagulant",
    "glycoside", "glycosides", "peptide", "peptides",
    "sulphate", "sulfate", "chloride", "oxide", "carbonate",
    "phosphate", "citrate", "acetate", "lactate", "gluconate",
}

PROCESS_WORDS: set[str] = {
    "refined", "malted", "fermented", "dried", "roasted",
    "hydrogenated", "modified", "bleached", "dehydrated",
    "organic", "partially", "skimmed", "homogenised",
    "hydrolyzed", "hydralyzed", "instantised", "clarified",
    "interesterified", "fractionated", "evaporated", "condensed",
    "pasteurised", "pasteurized", "sterilised", "sterilized",
    "full-fat", "low-fat", "fat-free", "cultured", "acidified",
    "ultra-heat", "uht", "spray-dried", "freeze-dried",
    "solvent-extracted", "cold-pressed", "expeller-pressed",
    "defatted", "deoiled", "degummed", "neutralised", "neutralized",
    "winterized", "dewaxed", "deodorised", "deodorized",
    "dry", "dried", "toned", "standardised", "standardized",
    "concentrated", "reconstituted", "fortified", "enriched",
    "smoked", "cured", "pressed", "filtered", "decaffeinated",
    "vegan", "plant-based", "natural", "artificial", "synthetic",
    "activated", "neutralized", "treated", "processed", "instant",
    # Additional process terms
    "puffed", "fried", "grated", "powdered", "ground",
    "milled", "crushed", "minced", "chopped", "sliced",
    "flattened", "rolled", "extruded", "toasted",
    "soluble", "insoluble", "hydrated", "dehydrated",
    "low-sodium", "sodium-free", "salt-free", "unsalted",
    "nylon", "resultant",
    "micronized", "microfiltered", "ultrafiltered",
    "bio", "probiotic", "prebiotic", "synbiotic",
    "blended", "standardized",
}

GRADE_PART_WORDS: set[str] = {
    "whole", "fine", "coarse", "raw", "seeds", "seed", "leaves", "leaf",
    "rhizome", "kernel", "peel", "zest", "pulp", "pieces",
    "large", "small", "black", "green", "white", "red", "yellow",
    "brown", "dark", "light", "extra", "special", "premium",
    "grade", "quality", "type", "variety", "blend", "mixed",
    "primary", "secondary", "crude", "technical", "food-grade",
    "sea", "rock", "edible", "table", "iodized", "iodised",
    "sweet", "sour", "bitter", "mild", "hot", "spicy", "fresh",
    "full", "low", "skim", "skimmed", "toned", "double",
    "single", "split", "rolled", "broken", "cracked", "ground",
    "a2", "buffalo", "cow", "goat", "sheep", "camel",
    "bud", "tip", "top", "head", "pod", "cone", "berry", "berries",
    "bits", "chunk", "chunks", "slice", "slices", "segment",
    # Additional grade/part/variety terms
    "cane", "common", "loaded", "batter", "alkaline", "sodium",
    "arabica", "robusta", "bovine", "foxtail", "finger", "little",
    "puffed", "vital", "blossom", "stone", "cottage",
    "alphonso", "kashmiri", "kesar", "sonali",
    "bengal", "lobia", "chilka", "moth", "horse",
    "pistachio", "almond", "walnut", "cashew", "hazelnut",
    "inshell", "shelled", "hulled", "dehulled",
    "tangy", "french", "spanish", "italian", "american",
    "thai", "chinese", "japanese", "indian", "korean",
    "mackerel", "salmon", "tuna", "tilapia", "basa",
    "dairy", "plant", "animal", "marine",
    "himalayan", "pink", "grey", "purple", "blue",
    "ferrous", "ferric", "magnesium", "calcium", "potassium",
    "zinc", "copper", "manganese", "selenium", "chromium",
    "disodium", "monosodium", "dipotassium", "trisodium",
    "microbial", "bacterial", "fungal", "yeast",
    "tropical", "mediterranean", "himalayan",
    "husked", "wet", "aged", "mature", "young", "baby",
    "dew",
}

# Minimum variant length for edit-distance orthographic check
# (short strings have trivially low edit distances — avoid false positives)
MIN_EDIT_DIST_LEN = 5

KNOWN_ABBREVIATIONS: set[str] = {
    "snf", "wpc", "dha", "epa", "fos", "gos", "hvp", "tvp",
    "mpc", "mpg", "skim", "uht", "smp", "wmp", "shm", "lac",
    "msg", "kmc", "ins", "fnb", "rbd", "cpko", "cpo",
}

# Language tags considered non-English (signal)
NON_ENGLISH_LANG_TAGS: set[str] = {"fr", "de", "es", "vi", "hi", "ta", "te", "kn", "ml", "bn"}

# Noise vs signal classification
NOISE_CLASSES: set[str] = {"orthographic_noise", "redundant_variant", "compound_noise", "out_of_scope"}
SIGNAL_CLASSES: set[str] = {
    "linguistic_signal", "transliteration_signal", "form_signal",
    "process_signal", "grade_signal", "fortification_signal",
    "abbreviation_signal", "multi_source", "canonical_form",
}

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _is_ascii(s: str) -> bool:
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _normalise(s: str) -> str:
    """Lowercase, strip, collapse internal whitespace."""
    return " ".join(str(s).lower().strip().split())


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein distance, O(len(a)*len(b))."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1,
                            prev[j - 1] + (0 if ca == cb else 1)))
        prev = curr
    return prev[lb]


def _tokens(s: str) -> set[str]:
    return set(s.lower().split())

# ---------------------------------------------------------------------------
# Per-class detectors
# ---------------------------------------------------------------------------

def detect_orthographic_noise(row: pd.Series, grp: pd.DataFrame) -> bool:
    v = _normalise(row["variant"])

    # OCR swap dict hit
    if v in OCR_SWAPS:
        return True

    # No-space compound that matches a spaced sibling
    if " " not in v:
        spaced = " ".join(list(v))  # unlikely — skip; check direct concat
        # Check if removing spaces from another variant matches this one
        sibling_nospace = {_normalise(r).replace(" ", "") for r in grp["variant"] if _normalise(r) != v}
        if v in sibling_nospace:
            return True

    # Edit distance ≤ 2 to any sibling — only for strings long enough to matter
    if len(v) < MIN_EDIT_DIST_LEN:
        return False
    siblings = [_normalise(r) for r in grp["variant"] if _normalise(r) != v]
    return any(_edit_distance(v, s) <= 2 for s in siblings)


def detect_redundant_variant(row: pd.Series, grp: pd.DataFrame) -> bool:
    v = _normalise(row["variant"])
    # Exact duplicate within source group (same variant string)
    count = sum(1 for r in grp["variant"] if _normalise(r) == v)
    if count > 1:
        return True
    # Same facets signature as another row (if facets column present)
    if "label_facets" in grp.columns:
        fv = row.get("label_facets", None)
        if pd.notna(fv) and fv != "":
            sibling_facets = [
                r for r in grp["label_facets"]
                if pd.notna(r) and r == fv and _normalise(grp.loc[grp["label_facets"] == r].iloc[0]["variant"]) != v
            ]
            if sibling_facets:
                return True
    return False


def detect_compound_noise(row: pd.Series, _grp: pd.DataFrame) -> bool:
    v = _normalise(row["variant"])
    tokens = v.split()
    if len(tokens) < 3:
        return False
    # First token is a product-type word
    product_type_words = {
        "noodle", "biscuit", "cookie", "bread", "cake", "snack",
        "stabilizer", "emulsifier", "additive", "ingredient", "mix",
        "product", "preparation", "compound", "blend",
    }
    if tokens[0] in product_type_words:
        return True
    # Contains numeric code-like token (e.g. ns415 → brand adjacent)
    import re
    if any(re.search(r"\d{3,}", t) for t in tokens):
        return True
    return False


def detect_out_of_scope(row: pd.Series, _grp: pd.DataFrame) -> bool:
    if not row.get("question_tags", False):
        return False
    e_could = str(row.get("e_could_be", "") or "").lower()
    return any(w in e_could for w in ("bak", "extru", "fry", "cook"))


FOREIGN_INDICATORS: set[str] = {
    # French
    "beurre", "fondu", "crème", "creme", "huile", "lait", "farine", "sucre",
    "sel", "poivre", "extrait", "pâte", "pate", "purée", "puree", "jus",
    "noisettes", "turquie", "turchia", "nocciole",
    # German
    "schoten", "schote", "nuss", "nüsse", "nusse", "mehl", "öl", "ol",
    "zucker", "salz", "milch", "sahne", "rahm",
    "magermilchpulver", "vanilleschoten",
    # Italian
    "pasta", "olio", "burro", "zucchero", "farina", "latte",
    "cacao", "bacche", "vaniglia", "nocciole", "turchia",
    # Filipino/Southeast Asian
    "nata", "de", "coco",
    # Spanish
    "sal", "aceite", "harina", "azucar",
    # Latin/scientific indicators (2-word scientific names)
    "bacillus", "lactobacillus", "streptococcus", "aspergillus",
    "origanum", "majorana", "emblica", "officinalis", "tenuiflorum",
    "gratissimum", "sanctum", "coagulans", "casei", "bifidus",
}

def detect_linguistic_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    v = str(row["variant"])
    # Non-ASCII characters present
    if not _is_ascii(v):
        return True
    # language_tag is set and non-English
    lang = str(row.get("language_tag", "") or "").strip().lower()
    if lang and lang in NON_ENGLISH_LANG_TAGS and lang != "hi":
        return True
    # ASCII variant containing known non-English indicator words
    vtokens = _tokens(_normalise(v))
    if vtokens & FOREIGN_INDICATORS:
        return True
    return False


def detect_transliteration_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    v = _normalise(row["variant"])
    # Direct match in vocab
    if v in TRANSLITERATION_VOCAB:
        return True
    # Any token in vocab (e.g. "whole atta", "atta flour")
    tokens = _tokens(v)
    if tokens & TRANSLITERATION_VOCAB:
        return True
    # language_tag == hi → likely Hindi transliteration
    lang = str(row.get("language_tag", "") or "").strip().lower()
    if lang == "hi":
        return True
    return False


def detect_form_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    """Variant contains a form word — describes physical/chemical form of ingredient."""
    v = _normalise(row["variant"])
    return bool(_tokens(v) & FORM_WORDS)


def detect_process_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    """Variant contains a process word — describes how it was produced or treated."""
    v = _normalise(row["variant"])
    return bool(_tokens(v) & PROCESS_WORDS)


def detect_grade_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    """Variant contains a grade/part/qualifier word — describes physical part or grade."""
    v = _normalise(row["variant"])
    return bool(_tokens(v) & GRADE_PART_WORDS)


def detect_fortification_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    v = _normalise(row["variant"])
    fort_words = {"fortified", "enriched", "vitamin", "mineral", "iron", "zinc",
                  "iodized", "iodised", "folic", "folate", "riboflavin", "thiamine",
                  "niacin", "b12", "d3", "calcium", "selenium"}
    return bool(_tokens(v) & fort_words)


def detect_abbreviation_signal(row: pd.Series, _grp: pd.DataFrame) -> bool:
    v = _normalise(row["variant"])
    # Known abbreviations
    if v in KNOWN_ABBREVIATIONS:
        return True
    # Short, all-caps, or dot-separated
    stripped = v.replace(".", "").replace("-", "")
    if len(stripped) <= 6 and stripped == stripped.upper() and stripped.isalpha():
        return True
    return False


def detect_multi_source(row: pd.Series, _grp: pd.DataFrame) -> bool:
    return "|" in str(row.get("source", "") or "")


def detect_canonical_form(row: pd.Series, grp: pd.DataFrame) -> bool:
    """Variant is the plain English base name — no added form/process/grade info.

    Fires when:
    - variant == source (exact or after normalisation)
    - variant is within edit distance 1 of the primary source name (e.g. "oils" ↔ "oil")
    - variant is a short (≤ 4 char) single-token food word with no modifiers
    - plural/singular trivial variation of source name

    This catches the large set of simple English canonical names
    ("oat", "rice", "egg", "palm", "mint", …) that carry no additional
    facet information beyond naming the ingredient.
    """
    v = _normalise(row["variant"])
    src = _normalise(str(row.get("source", "") or ""))

    # Strip pipe-compound sources to first token for comparison
    src_primary = src.split("|")[0].strip()

    # Direct match or trivial plural/singular
    if v == src_primary:
        return True
    if v + "s" == src_primary or src_primary + "s" == v:
        return True

    # Edit distance 1 to source primary
    if len(v) >= 3 and _edit_distance(v, src_primary) <= 1:
        return True

    # Single-token variant, up to 15 chars, ASCII, no transliteration
    # Allows: single common food/chemical name (magnesium, aspartame, …)
    # Excludes: hyphenated compounds handled elsewhere, non-alpha (abbreviations)
    tokens = v.split()
    alpha_only = v.replace("-", "").replace(".", "").replace("'", "")
    if (
        len(tokens) == 1
        and len(v) <= 15
        and v not in TRANSLITERATION_VOCAB
        and _is_ascii(v)
        and alpha_only.isalpha()
    ):
        return True

    # Multi-word phrase where source is a substring or very close
    # Catches "alphonso mango" when source is "mango", "arabica beans" when source is "coffee"
    # (the source is a known ingredient; variant is a named variety or qualifier phrase)
    if len(tokens) >= 2 and src_primary in tokens:
        return True

    # Technical names with hyphens, dots, spaces + numeric (e.g. "l-theanine", "m.p. wheat", "acesulfame k")
    if len(tokens) <= 3 and (
        any(c in v for c in ("-", "."))
        or (len(tokens) == 2 and tokens[-1].isalpha() and len(tokens[-1]) == 1)
    ):
        return True

    return False

# ---------------------------------------------------------------------------
# Main classification
# ---------------------------------------------------------------------------

DETECTORS: list[tuple[str, callable]] = [
    ("orthographic_noise",    detect_orthographic_noise),
    ("redundant_variant",     detect_redundant_variant),
    ("compound_noise",        detect_compound_noise),
    ("out_of_scope",          detect_out_of_scope),
    ("linguistic_signal",     detect_linguistic_signal),
    ("transliteration_signal", detect_transliteration_signal),
    ("canonical_form",        detect_canonical_form),
    ("form_signal",           detect_form_signal),
    ("process_signal",        detect_process_signal),
    ("grade_signal",          detect_grade_signal),
    ("fortification_signal",  detect_fortification_signal),
    ("abbreviation_signal",   detect_abbreviation_signal),
    ("multi_source",          detect_multi_source),
]


def detect_classes(row: pd.Series, source_group: pd.DataFrame) -> list[str]:
    tags: list[str] = []
    for cls, fn in DETECTORS:
        try:
            if fn(row, source_group):
                tags.append(cls)
        except Exception:
            pass
    return tags if tags else ["unclassified"]


def noise_or_signal_label(tags: list[str]) -> str:
    tag_set = set(tags)
    if tag_set == {"unclassified"}:
        return "unclassified"
    has_signal = bool(tag_set & SIGNAL_CLASSES)
    has_noise = bool(tag_set & NOISE_CLASSES)
    if has_signal and has_noise:
        return "mixed"
    if has_signal:
        return "signal"
    return "noise"


def run_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Classify every row; return df with new variant_signal_class column."""
    # Build source groups — group by the exact source string
    groups: dict[str, pd.DataFrame] = {}
    for src, gdf in df.groupby("source", sort=False):
        groups[src] = gdf.reset_index(drop=True)

    tags_list: list[str] = []
    for idx, row in df.iterrows():
        src = str(row.get("source", "") or "")
        grp = groups.get(src, df.iloc[[idx]].reset_index(drop=True))
        tags = detect_classes(row, grp)
        tags_list.append(", ".join(tags))

    df = df.copy()
    df["variant_signal_class"] = tags_list
    return df

# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _parse_tags(series: pd.Series) -> pd.Series:
    """Explode comma-separated tags into a flat count series."""
    return series.str.split(", ").explode()


def _examples(df: pd.DataFrame, cls: str, n: int = 3) -> str:
    mask = df["variant_signal_class"].str.contains(cls, regex=False)
    variants = df.loc[mask, "variant"].head(n).tolist()
    return " · ".join(str(v) for v in variants)


def render_report(df: pd.DataFrame, console: Console) -> None:
    all_tags = _parse_tags(df["variant_signal_class"])
    tag_counts = all_tags.value_counts()
    total = len(df)

    # ── Headline ────────────────────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold]IFID Variant Signal/Noise Analysis[/bold]"))
    console.print(f"  Corpus: [bold]{total:,}[/bold] variants   "
                  f"Unique sources: [bold]{df['source'].nunique()}[/bold]")
    console.print()

    # Noise vs signal totals
    nos = df["variant_signal_class"].apply(
        lambda s: noise_or_signal_label(s.split(", "))
    )
    sig_count = (nos == "signal").sum()
    noise_count = (nos == "noise").sum()
    mixed_count = (nos == "mixed").sum()
    uncls_count = (nos == "unclassified").sum()

    console.print(f"  [green]Signal[/green]:        {sig_count:5,}  ({sig_count/total*100:.1f}%)")
    console.print(f"  [red]Noise[/red]:         {noise_count:5,}  ({noise_count/total*100:.1f}%)")
    console.print(f"  [yellow]Mixed[/yellow]:         {mixed_count:5,}  ({mixed_count/total*100:.1f}%)")
    console.print(f"  [dim]Unclassified[/dim]:  {uncls_count:5,}  ({uncls_count/total*100:.1f}%)")
    console.print()

    # ── Class breakdown table ────────────────────────────────────────────────
    console.print(Rule("Class Breakdown"))
    tbl = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    tbl.add_column("Class", style="dim", min_width=24)
    tbl.add_column("Type", min_width=7)
    tbl.add_column("Count", justify="right")
    tbl.add_column("%", justify="right")
    tbl.add_column("Examples", max_width=60)

    all_classes = [c for c, _ in DETECTORS] + ["unclassified"]  # includes canonical_form
    for cls in all_classes:
        cnt = tag_counts.get(cls, 0)
        pct = cnt / total * 100
        is_noise = cls in NOISE_CLASSES
        is_signal = cls in SIGNAL_CLASSES
        typ = "[red]noise[/red]" if is_noise else ("[green]signal[/green]" if is_signal else "[dim]?[/dim]")
        ex = _examples(df, cls)
        tbl.add_row(cls, typ, f"{cnt:,}", f"{pct:.1f}%", ex)

    console.print(tbl)

    # ── Per-source breakdown (top sources) ──────────────────────────────────
    console.print(Rule("Per-Source Breakdown (top sources)"))
    target_sources = ["milk", "wheat", "sugarcane", "palm", "rice",
                      "soybean", "corn", "mineral", "synthetic"]

    src_tbl = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    src_tbl.add_column("Source", min_width=12)
    src_tbl.add_column("Rows", justify="right")
    src_tbl.add_column("Signal %", justify="right")
    src_tbl.add_column("Noise %", justify="right")
    src_tbl.add_column("Top class", min_width=24)

    for src in target_sources:
        sdf = df[df["source"] == src]
        if sdf.empty:
            continue
        s_tags = _parse_tags(sdf["variant_signal_class"])
        s_counts = s_tags.value_counts()
        s_total = len(sdf)
        s_nos = sdf["variant_signal_class"].apply(
            lambda s: noise_or_signal_label(s.split(", "))
        )
        s_sig = (s_nos.isin(["signal", "mixed"])).sum() / s_total * 100
        s_noise = (s_nos == "noise").sum() / s_total * 100
        top_cls = s_counts.index[0] if len(s_counts) else "—"
        src_tbl.add_row(src, str(s_total), f"{s_sig:.0f}%", f"{s_noise:.0f}%", top_cls)

    console.print(src_tbl)

    # ── Linguistic signal inventory ──────────────────────────────────────────
    console.print(Rule("Linguistic Signal Inventory"))
    ling = df[df["variant_signal_class"].str.contains("linguistic_signal", regex=False)].copy()
    if ling.empty:
        console.print("  (none detected)")
    else:
        ling_tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        ling_tbl.add_column("Variant", min_width=30)
        ling_tbl.add_column("Source", min_width=14)
        ling_tbl.add_column("Lang tag")
        ling_tbl.add_column("Classes")
        for _, r in ling.iterrows():
            ling_tbl.add_row(
                str(r["variant"]),
                str(r["source"]),
                str(r.get("language_tag", "") or ""),
                str(r["variant_signal_class"]),
            )
        console.print(ling_tbl)

    # ── Transliteration inventory ────────────────────────────────────────────
    console.print(Rule("Transliteration Signal Inventory"))
    trans = df[df["variant_signal_class"].str.contains("transliteration_signal", regex=False)].copy()
    if trans.empty:
        console.print("  (none detected)")
    else:
        t_tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        t_tbl.add_column("Variant", min_width=25)
        t_tbl.add_column("Source", min_width=14)
        t_tbl.add_column("Classes")
        t_tbl.add_column("v1 candidate?")
        for _, r in trans.iterrows():
            cls_str = str(r["variant_signal_class"])
            # v1 candidate if transliteration is the primary form (in vocab, short, no other signal classes)
            v = _normalise(str(r["variant"]))
            v1_cand = "YES" if v in TRANSLITERATION_VOCAB else "maybe"
            t_tbl.add_row(str(r["variant"]), str(r["source"]), cls_str, v1_cand)
        console.print(t_tbl)

    # ── Unclassified rows ────────────────────────────────────────────────────
    console.print(Rule("Unclassified Rows"))
    uncls = df[df["variant_signal_class"] == "unclassified"]
    if uncls.empty:
        console.print("  [green]None — all rows classified.[/green]")
    else:
        console.print(f"  [yellow]{len(uncls)} unclassified rows[/yellow] "
                      f"({len(uncls)/total*100:.1f}% of corpus):")
        u_tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        u_tbl.add_column("Variant", min_width=30)
        u_tbl.add_column("Source", min_width=14)
        for _, r in uncls.head(30).iterrows():
            u_tbl.add_row(str(r["variant"]), str(r["source"]))
        console.print(u_tbl)
        if len(uncls) > 30:
            console.print(f"  ... and {len(uncls)-30} more (see variant_class_report.csv)")

    console.print()
    console.print(Rule("[bold]Done[/bold]"))
    console.print()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    console = Console()

    # ── Primary corpus ───────────────────────────────────────────────────────
    console.print(f"\n[cyan]Loading[/cyan] {PRIMARY_CSV.name} …")
    df = pd.read_csv(PRIMARY_CSV, dtype=str)
    df["question_tags"] = df["question_tags"].str.lower().str.strip() == "true"

    df_classified = run_analysis(df)

    # Save updated primary CSV
    df_classified.to_csv(PRIMARY_CSV, index=False)
    console.print(f"[green]Saved[/green] {PRIMARY_CSV.name} (with variant_signal_class column)")

    # ── Report CSV ──────────────────────────────────────────────────────────
    report_df = df_classified[["variant", "source", "variant_signal_class"]].copy()
    report_df["class_count"] = report_df["variant_signal_class"].str.split(", ").apply(len)
    report_df["noise_or_signal"] = report_df["variant_signal_class"].apply(
        lambda s: noise_or_signal_label(s.split(", "))
    )
    report_df.to_csv(REPORT_CSV, index=False)
    console.print(f"[green]Saved[/green] {REPORT_CSV.name}")

    # ── Render terminal report ───────────────────────────────────────────────
    render_report(df_classified, console)

    # ── Comparison corpora ──────────────────────────────────────────────────
    for label, path in [("fortification_agent", FORTIFICATION_CSV), ("wheat", WHEAT_CSV)]:
        if not path.exists():
            console.print(f"[yellow]Skipping[/yellow] {label} — file not found: {path}")
            continue
        console.print(Rule(f"Comparison: {label}"))
        cdf = pd.read_csv(path, dtype=str)
        if "question_tags" in cdf.columns:
            cdf["question_tags"] = cdf["question_tags"].str.lower().str.strip() == "true"
        else:
            cdf["question_tags"] = False
        c_classified = run_analysis(cdf)
        c_nos = c_classified["variant_signal_class"].apply(
            lambda s: noise_or_signal_label(s.split(", "))
        )
        total_c = len(c_classified)
        console.print(f"  {label}: {total_c} rows | "
                      f"signal {(c_nos.isin(['signal','mixed'])).sum()/total_c*100:.0f}% | "
                      f"noise {(c_nos=='noise').sum()/total_c*100:.0f}%")


if __name__ == "__main__":
    main()
