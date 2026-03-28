import json
import uuid
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB = Path(__file__).parent / "db"

# --- data loading ---

def load_taxonomy():
    with open(DB / "additives_taxonomy.json") as f:
        return json.load(f)["additives"]

def load_products():
    with open(DB / "products.json") as f:
        return json.load(f)

def save_products(products):
    with open(DB / "products.json", "w") as f:
        json.dump(products, f, indent=2)

# --- break detection ---

BREAK_TYPES = {
    "AMBIGUOUS_FUNCTIONAL_CLASS": "Additive has multiple functional classes — brand must pick one but form doesn't enforce it yet",
    "ANIMAL_DERIVED_NO_FLAG":     "Animal-derived additive — no dietary/allergen flag field in current schema",
    "CLASS_ONLY_DECLARATION":     "Brand declared a functional class without specifying INS — taxonomy can't anchor this",
    "NOT_IN_TAXONOMY":            "Ingredient string submitted but no matching INS entry found",
    "MULTI_INS_SINGLE_CLASS":     "Brand wants to group multiple INS numbers under one functional class declaration",
}

def detect_breaks(ins_number, declared_class, taxonomy):
    breaks = []
    entry = taxonomy.get(ins_number)

    if not entry:
        breaks.append({
            "type": "NOT_IN_TAXONOMY",
            "detail": f"INS {ins_number} not found in verified additives taxonomy"
        })
        return breaks

    if len(entry["functional_classes"]) > 1 and not declared_class:
        breaks.append({
            "type": "AMBIGUOUS_FUNCTIONAL_CLASS",
            "detail": f"INS {ins_number} has classes: {', '.join(entry['functional_classes'])} — none declared"
        })

    if entry.get("source_type") == "animal":
        breaks.append({
            "type": "ANIMAL_DERIVED_NO_FLAG",
            "detail": f"INS {ins_number} ({entry['official_name']}) is animal-derived — no dietary flag field exists in schema"
        })

    return breaks

# --- routes ---

@app.route("/")
def index():
    products = load_products()
    taxonomy = load_taxonomy()
    return render_template("index.html", products=products, taxonomy_count=len(taxonomy))


@app.route("/sku/new", methods=["GET", "POST"])
def sku_new():
    if request.method == "POST":
        products = load_products()
        sku_id = "sku_" + uuid.uuid4().hex[:6]
        products[sku_id] = {
            "name": request.form["name"].strip(),
            "brand": request.form["brand"].strip(),
            "ingredients": [],
            "breaks": []
        }
        save_products(products)
        return redirect(url_for("sku_view", sku_id=sku_id))
    return render_template("sku_new.html")


@app.route("/sku/<sku_id>")
def sku_view(sku_id):
    products = load_products()
    sku = products.get(sku_id)
    if not sku:
        return "SKU not found", 404
    taxonomy = load_taxonomy()
    # enrich ingredients with taxonomy data for display
    enriched = []
    for ing in sku["ingredients"]:
        entry = taxonomy.get(ing.get("ins_number", ""), {})
        enriched.append({**ing, "taxonomy": entry})
    return render_template("sku.html", sku_id=sku_id, sku=sku, ingredients=enriched)


@app.route("/sku/<sku_id>/add", methods=["GET", "POST"])
def ingredient_add(sku_id):
    products = load_products()
    sku = products.get(sku_id)
    if not sku:
        return "SKU not found", 404

    taxonomy = load_taxonomy()

    if request.method == "POST":
        ins_number = request.form.get("ins_number", "").strip()
        declared_class = request.form.get("declared_class", "").strip()
        class_only = request.form.get("class_only", "")   # brand declares class, no INS
        multi_ins = request.form.get("multi_ins", "")     # e.g. "319,320"

        # class-only declaration path
        if class_only:
            ing = {
                "order": len(sku["ingredients"]) + 1,
                "type": "additive",
                "ins_number": None,
                "declared_functional_class": class_only,
                "declaration_note": "class-only"
            }
            sku["ingredients"].append(ing)
            sku["breaks"].append({
                "ingredient_order": ing["order"],
                "type": "CLASS_ONLY_DECLARATION",
                "detail": f"Declared class '{class_only}' with no INS number — cannot anchor to taxonomy"
            })
            save_products(products)
            return redirect(url_for("sku_view", sku_id=sku_id))

        # multi-INS under one class declaration
        if multi_ins:
            ins_list = [x.strip() for x in multi_ins.split(",") if x.strip()]
            ing = {
                "order": len(sku["ingredients"]) + 1,
                "type": "additive",
                "ins_number": ins_list,
                "declared_functional_class": declared_class or None,
                "declaration_note": "multi-ins"
            }
            sku["ingredients"].append(ing)
            sku["breaks"].append({
                "ingredient_order": ing["order"],
                "type": "MULTI_INS_SINGLE_CLASS",
                "detail": f"Group declaration: INS {', '.join(ins_list)} under class '{declared_class}'"
            })
            save_products(products)
            return redirect(url_for("sku_view", sku_id=sku_id))

        # standard single-INS path
        breaks = detect_breaks(ins_number, declared_class, taxonomy)
        entry = taxonomy.get(ins_number, {})

        ing = {
            "order": len(sku["ingredients"]) + 1,
            "type": "additive",
            "ins_number": ins_number,
            "declared_functional_class": declared_class or (entry.get("functional_classes", [None])[0]),
            "declaration_note": "standard"
        }
        sku["ingredients"].append(ing)
        for b in breaks:
            sku["breaks"].append({"ingredient_order": ing["order"], **b})

        save_products(products)
        return redirect(url_for("sku_view", sku_id=sku_id))

    # GET — build sorted additive list for dropdown
    additives_sorted = sorted(
        taxonomy.items(),
        key=lambda x: x[1]["official_name"]
    )
    return render_template("ingredient_add.html", sku_id=sku_id, sku=sku,
                           additives=additives_sorted, taxonomy=taxonomy)


@app.route("/sku/<sku_id>/label")
def label_generate(sku_id):
    products = load_products()
    sku = products.get(sku_id)
    if not sku:
        return "SKU not found", 404
    taxonomy = load_taxonomy()

    parts = []
    for ing in sorted(sku["ingredients"], key=lambda x: x["order"]):
        ins = ing.get("ins_number")
        fc = ing.get("declared_functional_class", "")
        note = ing.get("declaration_note", "")

        if note == "class-only":
            parts.append(fc.title())
        elif note == "multi-ins":
            ins_list = ins if isinstance(ins, list) else [ins]
            ins_str = ", ".join(f"INS {n}" for n in ins_list)
            parts.append(f"{fc.title()} ({ins_str})" if fc else f"({ins_str})")
        elif ins and ins in taxonomy:
            entry = taxonomy[ins]
            name = entry["official_name"]
            parts.append(f"{fc.title()} ({name} - INS {ins})" if fc else f"{name} (INS {ins})")
        elif ins:
            parts.append(f"INS {ins} [NOT IN TAXONOMY]")

    label_text = ", ".join(parts)
    return render_template("label.html", sku_id=sku_id, sku=sku, label_text=label_text)


@app.route("/breaks")
def breaks_view():
    products = load_products()
    all_breaks = []
    for sku_id, sku in products.items():
        for b in sku.get("breaks", []):
            all_breaks.append({"sku_id": sku_id, "sku_name": sku["name"], **b})
    # group by type
    grouped = {}
    for b in all_breaks:
        grouped.setdefault(b["type"], []).append(b)
    return render_template("breaks.html", grouped=grouped, break_types=BREAK_TYPES)


@app.route("/taxonomy")
def taxonomy_view():
    taxonomy = load_taxonomy()
    by_class = {}
    for ins, entry in taxonomy.items():
        for fc in entry.get("functional_classes", ["unknown"]):
            by_class.setdefault(fc, []).append(entry)
    by_class = dict(sorted(by_class.items()))
    return render_template("taxonomy.html", by_class=by_class, total=len(taxonomy))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
