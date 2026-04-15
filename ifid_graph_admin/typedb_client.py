from typedb.driver import TypeDB, Credentials, DriverOptions, TransactionType

TYPEDB_ADDRESS = "localhost:1729"
TYPEDB_DATABASE = "ifi_v-0--0-2"
TYPEDB_USER = "admin"
TYPEDB_PASS = "password"


def get_driver():
    return TypeDB.driver(
        TYPEDB_ADDRESS,
        Credentials(TYPEDB_USER, TYPEDB_PASS),
        DriverOptions(is_tls_enabled=False),
    )


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def get_all_sources():
    """Return list of source attribute dicts, sorted by name."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            names_answer = tx.query(
                "match $s isa source, has source-name $n; select $n;"
            ).resolve()
            names = sorted([
                row.get("n").get_string()
                for row in names_answer.as_concept_rows()
            ])

            detailed = []
            for name in names:
                attrs_answer = tx.query(
                    f'match $s isa source, has source-name "{name}", '
                    f'has source-type $t, has is-allergen $a, has is-declarable $d; '
                    f'select $t, $a, $d;'
                ).resolve()
                source_type = "?"
                is_allergen = False
                is_declarable = True
                for row in attrs_answer.as_concept_rows():
                    source_type = row.get("t").get_string()
                    is_allergen = row.get("a").get_boolean()
                    is_declarable = row.get("d").get_boolean()
                detailed.append({
                    "name": name,
                    "source_type": source_type,
                    "is_allergen": is_allergen,
                    "is_declarable": is_declarable,
                })
            return detailed


def get_declarable_sources():
    """Return sorted list of source-name strings where is-declarable = true."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            answer = tx.query(
                "match $s isa source, has source-name $n, has is-declarable true; "
                "select $n;"
            ).resolve()
            return sorted([
                row.get("n").get_string()
                for row in answer.as_concept_rows()
            ])


def get_all_sources_names():
    """Return sorted list of all source-name strings."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            answer = tx.query(
                "match $s isa source, has source-name $n; select $n;"
            ).resolve()
            return sorted([
                row.get("n").get_string()
                for row in answer.as_concept_rows()
            ])


def get_all_forms():
    """Return list of form dicts with form_id and optional matter_state."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            ids_answer = tx.query(
                "match $f isa ingredient-form, has form-id $id; select $id;"
            ).resolve()
            ids = sorted([
                row.get("id").get_string()
                for row in ids_answer.as_concept_rows()
            ])

            detailed = []
            for fid in ids:
                ms_answer = tx.query(
                    f'match $f isa ingredient-form, has form-id "{fid}", '
                    f'has matter-state $ms; select $ms;'
                ).resolve()
                ms = None
                for row in ms_answer.as_concept_rows():
                    ms = row.get("ms").get_string()
                detailed.append({"form_id": fid, "matter_state": ms})
            return detailed


def get_all_form_ids():
    """Return sorted list of form-id strings."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            answer = tx.query(
                "match $f isa ingredient-form, has form-id $id; select $id;"
            ).resolve()
            return sorted([
                row.get("id").get_string()
                for row in answer.as_concept_rows()
            ])


def get_dashboard_counts():
    """Return dict of entity/relation counts."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:

            def count_query(q):
                answer = tx.query(q).resolve()
                for row in answer.as_concept_rows():
                    return row.get("c").get_integer()
                return 0

            return {
                "sources": count_query(
                    "match $s isa source; select $s; reduce $c = count;"
                ),
                "forms": count_query(
                    "match $f isa ingredient-form; select $f; reduce $c = count;"
                ),
                "form_of": count_query(
                    "match $r isa form-of; select $r; reduce $c = count;"
                ),
                "variety_of": count_query(
                    "match $r isa variety-of; select $r; reduce $c = count;"
                ),
                "categories": count_query(
                    "match $c isa category; select $c; reduce $c = count;"
                ),
                "belongs_to": count_query(
                    "match $r isa belongs-to; select $r; reduce $c = count;"
                ),
            }


def get_all_categories():
    """Return sorted list of category-name strings with member counts."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            names_answer = tx.query(
                "match $c isa category, has category-name $n; select $n;"
            ).resolve()
            names = sorted([
                row.get("n").get_string()
                for row in names_answer.as_concept_rows()
            ])
            detailed = []
            for name in names:
                count_answer = tx.query(
                    f'match $cat isa category, has category-name "{name}"; '
                    f'$r (category: $cat) isa belongs-to; select $r; reduce $cnt = count;'
                ).resolve()
                cnt = 0
                for row in count_answer.as_concept_rows():
                    cnt = row.get("cnt").get_integer()
                members_answer = tx.query(
                    f'match $s isa source, has source-name $n; '
                    f'$cat isa category, has category-name "{name}"; '
                    f'(member: $s, category: $cat) isa belongs-to; select $n;'
                ).resolve()
                members = sorted([
                    row.get("n").get_string()
                    for row in members_answer.as_concept_rows()
                ])
                detailed.append({"name": name, "member_count": cnt, "members": members})
            return detailed


def get_all_category_names():
    """Return sorted list of category-name strings."""
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.READ) as tx:
            answer = tx.query(
                "match $c isa category, has category-name $n; select $n;"
            ).resolve()
            return sorted([
                row.get("n").get_string()
                for row in answer.as_concept_rows()
            ])


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def insert_source(name, source_type, is_allergen, is_declarable):
    allergen_str = "true" if is_allergen else "false"
    declarable_str = "true" if is_declarable else "false"
    tql = (
        f'insert $s isa source, '
        f'has source-name "{name}", '
        f'has source-type "{source_type}", '
        f'has is-allergen {allergen_str}, '
        f'has is-declarable {declarable_str};'
    )
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()


def insert_form(form_id, matter_state=None):
    if matter_state:
        tql = (
            f'insert $f isa ingredient-form, '
            f'has form-id "{form_id}", '
            f'has matter-state "{matter_state}";'
        )
    else:
        tql = f'insert $f isa ingredient-form, has form-id "{form_id}";'
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()


def insert_form_of(origin_name, form_id, processing_method=None):
    if processing_method:
        tql = (
            f'match '
            f'$o isa source, has source-name "{origin_name}"; '
            f'$f isa ingredient-form, has form-id "{form_id}"; '
            f'insert (origin: $o, form: $f) isa form-of, '
            f'has processing-method "{processing_method}";'
        )
    else:
        tql = (
            f'match '
            f'$o isa source, has source-name "{origin_name}"; '
            f'$f isa ingredient-form, has form-id "{form_id}"; '
            f'insert (origin: $o, form: $f) isa form-of;'
        )
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()


def insert_category(name):
    tql = f'insert $c isa category, has category-name "{name}";'
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()


def insert_belongs_to(source_name, category_name):
    tql = (
        f'match '
        f'$s isa source, has source-name "{source_name}"; '
        f'$c isa category, has category-name "{category_name}"; '
        f'insert (member: $s, category: $c) isa belongs-to;'
    )
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()


def insert_variety_of_sources(base_name, variety_name):
    tql = (
        f'match '
        f'$b isa source, has source-name "{base_name}"; '
        f'$v isa source, has source-name "{variety_name}"; '
        f'insert (base: $b, variety: $v) isa variety-of;'
    )
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()


def insert_variety_of_forms(base_id, variety_id):
    tql = (
        f'match '
        f'$b isa ingredient-form, has form-id "{base_id}"; '
        f'$v isa ingredient-form, has form-id "{variety_id}"; '
        f'insert (base: $b, variety: $v) isa variety-of;'
    )
    with get_driver() as driver:
        with driver.transaction(TYPEDB_DATABASE, TransactionType.WRITE) as tx:
            tx.query(tql).resolve()
            tx.commit()
