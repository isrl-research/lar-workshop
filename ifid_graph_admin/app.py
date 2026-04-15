from flask import Flask, render_template, request, redirect, url_for, flash
import typedb_client as db

app = Flask(__name__)
app.secret_key = "ifid-graph-admin-secret"

SOURCE_TYPES = ["plant", "dairy", "animal", "marine", "fungal", "microbial", "synthetic"]


def normalise_id(value):
    """Lowercase and replace spaces with hyphens."""
    return value.strip().lower().replace(" ", "-")


def warn_source_name(name):
    """Warn only when two words are given in likely-reversed order (specific family)."""
    # Single words (banana, mango) and 3+ words are fine — no warning.
    # Two words: remind about family-first ordering but don't block.
    return None


def warn_form_id(fid):
    if " " in fid:
        return f"form-id '{fid}' contains spaces — use hyphens (e.g. 'skim-milk-powder')"
    return None


@app.route("/")
def index():
    try:
        counts = db.get_dashboard_counts()
        error = None
    except Exception as e:
        counts = None
        error = str(e)
    return render_template("index.html", counts=counts, error=error, db_name=db.TYPEDB_DATABASE)


@app.route("/sources")
def sources_list():
    try:
        sources = db.get_all_sources()
        error = None
    except Exception as e:
        sources = []
        error = str(e)
    return render_template("sources_list.html", sources=sources, error=error)


@app.route("/sources/add", methods=["GET", "POST"])
def source_add():
    warnings = []
    if request.method == "POST":
        name = request.form.get("name", "").strip().lower()
        source_type = request.form.get("source_type", "").strip()
        is_allergen = request.form.get("is_allergen") == "true"
        is_declarable = request.form.get("is_declarable") == "true"

        w = warn_source_name(name)
        if w:
            warnings.append(w)

        if not name:
            flash("source-name is required.", "error")
        elif not source_type:
            flash("source-type is required.", "error")
        elif not warnings:
            try:
                db.insert_source(name, source_type, is_allergen, is_declarable)
                flash(f"Source '{name}' inserted.", "success")
                return redirect(url_for("sources_list"))
            except Exception as e:
                flash(f"Insert failed: {e}", "error")
        # Re-render with warnings if any

    return render_template("source_add.html",
                           source_types=SOURCE_TYPES,
                           warnings=warnings,
                           form=request.form)


@app.route("/forms")
def forms_list():
    try:
        forms = db.get_all_forms()
        error = None
    except Exception as e:
        forms = []
        error = str(e)
    return render_template("forms_list.html", forms=forms, error=error)


@app.route("/forms/add", methods=["GET", "POST"])
def form_add():
    warnings = []
    if request.method == "POST":
        form_id = normalise_id(request.form.get("form_id", ""))
        matter_state = request.form.get("matter_state", "").strip().lower() or None

        w = warn_form_id(form_id)
        if w:
            warnings.append(w)

        if not form_id:
            flash("form-id is required.", "error")
        elif not warnings:
            try:
                db.insert_form(form_id, matter_state)
                flash(f"Form '{form_id}' inserted.", "success")
                return redirect(url_for("forms_list"))
            except Exception as e:
                flash(f"Insert failed: {e}", "error")

    return render_template("form_add.html", warnings=warnings, form=request.form)


@app.route("/relations/form-of", methods=["GET", "POST"])
def relation_form_of():
    try:
        declarable_sources = db.get_declarable_sources()
        form_ids = db.get_all_form_ids()
        load_error = None
    except Exception as e:
        declarable_sources = []
        form_ids = []
        load_error = str(e)

    if request.method == "POST":
        origin = request.form.get("origin", "").strip()
        form_id = request.form.get("form_id", "").strip()
        processing_method = request.form.get("processing_method", "").strip().lower()
        processing_method = processing_method.replace(" ", "-") if processing_method else None

        if not origin or not form_id:
            flash("Both origin source and form are required.", "error")
        else:
            try:
                db.insert_form_of(origin, form_id, processing_method)
                flash(f"form-of ({origin} → {form_id}) inserted.", "success")
                return redirect(url_for("relation_form_of"))
            except Exception as e:
                flash(f"Insert failed: {e}", "error")

    return render_template("relation_form_of.html",
                           declarable_sources=declarable_sources,
                           form_ids=form_ids,
                           load_error=load_error,
                           form=request.form)


@app.route("/categories")
def categories_list():
    try:
        categories = db.get_all_categories()
        error = None
    except Exception as e:
        categories = []
        error = str(e)
    return render_template("categories_list.html", categories=categories, error=error)


@app.route("/categories/add", methods=["GET", "POST"])
def category_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip().lower()
        if not name:
            flash("category-name is required.", "error")
        else:
            try:
                db.insert_category(name)
                flash(f"Category '{name}' inserted.", "success")
                return redirect(url_for("categories_list"))
            except Exception as e:
                flash(f"Insert failed: {e}", "error")
    return render_template("category_add.html", form=request.form)


@app.route("/relations/belongs-to", methods=["GET", "POST"])
def relation_belongs_to():
    try:
        source_names = db.get_all_sources_names()
        category_names = db.get_all_category_names()
        load_error = None
    except Exception as e:
        source_names = []
        category_names = []
        load_error = str(e)

    if request.method == "POST":
        member = request.form.get("member", "").strip()
        category = request.form.get("category", "").strip()
        if not member or not category:
            flash("Both source and category are required.", "error")
        else:
            try:
                db.insert_belongs_to(member, category)
                flash(f"belongs-to ({member} → {category}) inserted.", "success")
                return redirect(url_for("relation_belongs_to"))
            except Exception as e:
                flash(f"Insert failed: {e}", "error")

    return render_template("relation_belongs_to.html",
                           source_names=source_names,
                           category_names=category_names,
                           load_error=load_error,
                           form=request.form)


@app.route("/relations/variety-of", methods=["GET", "POST"])
def relation_variety_of():
    try:
        source_names = db.get_all_sources_names()
        form_ids = db.get_all_form_ids()
        load_error = None
    except Exception as e:
        source_names = []
        form_ids = []
        load_error = str(e)

    if request.method == "POST":
        rel_kind = request.form.get("rel_kind", "source")
        if rel_kind == "source":
            base = request.form.get("source_base", "").strip()
            variety = request.form.get("source_variety", "").strip()
            if not base or not variety:
                flash("Both base and variety sources are required.", "error")
            elif base == variety:
                flash("Base and variety must be different.", "error")
            else:
                try:
                    db.insert_variety_of_sources(base, variety)
                    flash(f"variety-of (source: {variety} sub {base}) inserted.", "success")
                    return redirect(url_for("relation_variety_of"))
                except Exception as e:
                    flash(f"Insert failed: {e}", "error")
        else:
            base = request.form.get("form_base", "").strip()
            variety = request.form.get("form_variety", "").strip()
            if not base or not variety:
                flash("Both base and variety forms are required.", "error")
            elif base == variety:
                flash("Base and variety must be different.", "error")
            else:
                try:
                    db.insert_variety_of_forms(base, variety)
                    flash(f"variety-of (form: {variety} sub {base}) inserted.", "success")
                    return redirect(url_for("relation_variety_of"))
                except Exception as e:
                    flash(f"Insert failed: {e}", "error")

    return render_template("relation_variety_of.html",
                           source_names=source_names,
                           form_ids=form_ids,
                           load_error=load_error,
                           form=request.form)


if __name__ == "__main__":
    app.run(debug=True, port=5051)
