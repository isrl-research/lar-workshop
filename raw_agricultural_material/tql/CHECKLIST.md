# Schema Insertion Checklist

This checklist exists because the most common error is not a wrong fact — it is a
silent assumption that resolves an ambiguity without surfacing it. At 5 rows this
gets caught. At 500 rows it becomes structural debt.

The rule: **if something doesn't fit cleanly, flag it. Do not resolve silently.**

---

## Before placing anything in a subtype

Ask all three. If any answer is uncertain, stop and surface the question.

1. **Does this entry have the subtype's defining attribute with a value that is
   genuinely its own — not invented to make the entry fit?**
   If you are creating a new attribute value whose name is just the ingredient's
   own name, that is a forced fit. Flag it.

2. **Does the subtype's categorical depth apply to this entry?**
   `flour-form` has milling-grade depth (whole / refined / fortified).
   If the entry has no meaningful grade, it does not belong in flour-form —
   even if flour is the closest available subtype.

3. **Is there a closer subtype, or should this be a new one?**
   If the entry fits `ingredient-form` directly with `matter-state` and
   `processing-method`, that is a valid and complete encoding. Do not reach
   for a subtype just because one exists.

---

## When no subtype fits cleanly

Do not pick the most plausible subtype. Instead, surface the decision:

> "This entry doesn't cleanly fit any existing subtype. Options:
> (a) `ingredient-form` directly with matter-state + processing-method
> (b) new subtype if this is the first of a class with its own depth
> (c) defer if the entry itself is ambiguous
> Which do you want?"

The decision of whether to create a subtype belongs to the researcher, not to
the model. Creating a subtype is a schema-level commitment.

---

## Controlled vocabulary

Before adding a new value for any controlled attribute, check if it already exists.
If it doesn't, flag before adding — don't invent values silently.

| Attribute | Valid values |
|---|---|
| `milling-grade` | whole, refined, fortified |
| `matter-state` | flour, coarse grits, flakes, grain, concentrate, oil, extract |
| `processing-method` | milling, refining, rolling, malting, fermentation, roasting, extraction |
| `source-type` | natural, animal, mineral, synthetic |

Any value not in this table requires an explicit decision before use.

---

## After any batch insert

Run these verification queries before committing. Each should return 0 rows.

```typeql
# flour-form entries missing matter-state
match $f isa flour-form; not { $f has matter-state $m; };

# ingredient-form entries (non-flour) missing matter-state
match $f isa ingredient-form; not { $f isa flour-form; }; not { $f has matter-state $m; };

# derived-from relations missing processing-method
match $r isa derived-from; not { $r has processing-method $p; };

# flour-form entries with milling-grade not in controlled vocab
match $f isa flour-form, has milling-grade $g;
not { { $g = "whole"; } or { $g = "refined"; } or { $g = "fortified"; }; };
```
