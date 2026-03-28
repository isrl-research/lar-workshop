import json
import uuid
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = "ifid-proto-secret-key"
DB = Path(__file__).parent / "db"

# Sources that trigger flags
ALLERGEN_SOURCES = {
    'wheat', 'wheat gluten', 'barley malt',
    'soybean', 'egg yolk', 'fish',
}
ANIMAL_SOURCES = {
    'lard', 'tallow', 'animal pancreas',
    'fish', 'egg yolk', 'beeswax', 'lac beetle secretion',
}


def load_taxonomy():
    with open(DB / "additives_taxonomy.json") as f:
        return json.load(f)["additives"]

def load_products():
    with open(DB / "products.json") as f:
        return json.load(f)

def save_products(products):
    with open(DB / "products.json", "w") as f:
        json.dump(products, f, indent=2)

def source_flags(sources):
    """Given a list of source strings, return which flags apply."""
    allergens = [s for s in sources if s in ALLERGEN_SOURCES]
    is_animal  = any(s in ANIMAL_SOURCES for s in sources)
    return {"non_veg": is_animal, "allergens": allergens}

def requires_source_declaration(entry):
    """True when the brand must pick a source — multiple sources and at least one is animal or allergen."""
    sources = entry.get("sources", [])
    if len(sources) <= 1:
        return False
    flags = source_flags(sources)
    return flags["non_veg"] or bool(flags["allergens"])


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
        declared_source = request.form.get("declared_source", "").strip() or None

        entry = taxonomy.get(ins_number)

        # genuine break: not in taxonomy
        if not entry:
            sku["breaks"].append({
                "ingredient_order": len(sku["ingredients"]) + 1,
                "type": "NOT_IN_TAXONOMY",
                "detail": f"'{ins_number}' not found in verified INS additives taxonomy"
            })
            save_products(products)
            return redirect(url_for("sku_view", sku_id=sku_id))

        # resolve flags from declared source if given, else from all sources
        source_for_flags = [declared_source] if declared_source else entry.get("sources", [])
        flags = source_flags(source_for_flags)

        ing = {
            "order": len(sku["ingredients"]) + 1,
            "ins_number": ins_number,
            "declared_functional_class": declared_class or entry["functional_classes"][0],
            "declared_source": declared_source,
            "flags": flags,
        }
        sku["ingredients"].append(ing)
        save_products(products)
        flash("Ingredient added.")
        return redirect(url_for("sku_view", sku_id=sku_id))

    # pass taxonomy as JSON for client-side search
    taxonomy_json = json.dumps(taxonomy)
    return render_template("ingredient_add.html",
                           sku_id=sku_id, sku=sku,
                           taxonomy_json=taxonomy_json,
                           allergen_sources=json.dumps(list(ALLERGEN_SOURCES)),
                           animal_sources=json.dumps(list(ANIMAL_SOURCES)))


@app.route("/sku/<sku_id>/ingredient/<int:order>/delete", methods=["POST"])
def ingredient_delete(sku_id, order):
    products = load_products()
    sku = products.get(sku_id)
    if not sku:
        return "SKU not found", 404
    sku["ingredients"] = [i for i in sku["ingredients"] if i.get("order") != order]
    # re-number remaining ingredients in existing order
    for idx, ing in enumerate(sku["ingredients"], start=1):
        ing["order"] = idx
    save_products(products)
    return redirect(url_for("sku_view", sku_id=sku_id))


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
        fc  = ing.get("declared_functional_class", "")
        entry = taxonomy.get(ins, {})
        name = entry.get("official_name", ins)
        parts.append(f"{fc.title()} ({name} - INS {ins})" if fc else f"{name} (INS {ins})")

    label_text = ", ".join(parts)
    return render_template("label.html", sku_id=sku_id, sku=sku, label_text=label_text)


@app.route("/breaks")
def breaks_view():
    products = load_products()
    all_breaks = []
    for sku_id, sku in products.items():
        for b in sku.get("breaks", []):
            all_breaks.append({"sku_id": sku_id, "sku_name": sku["name"], **b})
    grouped = {}
    for b in all_breaks:
        grouped.setdefault(b["type"], []).append(b)
    return render_template("breaks.html", grouped=grouped)


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
