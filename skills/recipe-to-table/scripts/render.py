#!/usr/bin/env python3
"""render.py — validate a recipe JSON file and render it as a tabular-recipe HTML page.

The layout itself is done by the JavaScript in ../assets/recipe-table.html (the
single renderer shared with the Claude.ai Project); this script checks the data
against the contract in ../references/method.md and embeds it in that template.

Usage:
    python3 render.py RECIPE.json [-o OUT.html]   # validate + render (default OUT: RECIPE.html)
    python3 render.py RECIPE.json --check         # validate only

Prints the ingredient roster (for the conservation check) and the table shape.
Exit 0 on success, 1 on validation errors, 2 on usage/IO errors. Stdlib only.
"""
import argparse
import json
import os
import sys

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "recipe-table.html")
PLACEHOLDER = "__RECIPE_JSON__"
TOP_KEYS = {"title", "yield", "before", "assembly", "notes", "source"}
LEAF_KEYS = {"ingredient", "prep"}
STEP_KEYS = {"action", "inputs"}


def nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


class Checker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.roster = []

    def node(self, n, path):
        """Validate one node; return (column, rows) per the layout rules, or None."""
        if not isinstance(n, dict):
            self.errors.append(f"{path}: must be an object")
            return None
        if "ingredient" in n:
            extra = set(n) - LEAF_KEYS
            if extra:
                self.errors.append(f"{path}: unexpected key(s) on ingredient: {sorted(extra)}")
            if not nonempty_str(n["ingredient"]):
                self.errors.append(f"{path}: 'ingredient' must be a non-empty string")
                return None
            if "prep" in n and not nonempty_str(n["prep"]):
                self.errors.append(f"{path}: 'prep' must be a non-empty string when present")
            self.roster.append(n["ingredient"])
            return (1 if n.get("prep") else 0), 1
        if "action" in n:
            extra = set(n) - STEP_KEYS
            if extra:
                self.errors.append(f"{path}: unexpected key(s) on step: {sorted(extra)}")
            if not nonempty_str(n["action"]):
                self.errors.append(f"{path}: 'action' must be a non-empty string")
            inputs = n.get("inputs")
            if not isinstance(inputs, list) or not inputs:
                self.errors.append(f"{path} ({n.get('action')!r}): 'inputs' must be a non-empty list")
                return None
            if len(inputs) == 1 and isinstance(inputs[0], dict) and "ingredient" in inputs[0] and "prep" not in inputs[0]:
                self.warnings.append(
                    f"{path} ({n.get('action')!r}): a step acting on one bare ingredient should usually be "
                    f"that ingredient's 'prep' instead")
            dims = [self.node(c, f"{path}.inputs[{i}]") for i, c in enumerate(inputs)]
            if any(d is None for d in dims):
                return None
            return 1 + max(d[0] for d in dims), sum(d[1] for d in dims)
        self.errors.append(f"{path}: must have either 'ingredient' or 'action'")
        return None

    def recipe(self, r):
        if not isinstance(r, dict):
            self.errors.append("top level must be an object")
            return None
        extra = set(r) - TOP_KEYS
        if extra:
            self.errors.append(f"unexpected top-level key(s): {sorted(extra)}")
        if not nonempty_str(r.get("title")):
            self.errors.append("'title' is required")
        if "yield" in r and not nonempty_str(r["yield"]):
            self.errors.append("'yield' must be a non-empty string when present")
        for key in ("before", "notes"):
            v = r.get(key, [])
            if not isinstance(v, list) or not all(nonempty_str(x) for x in v):
                self.errors.append(f"'{key}' must be a list of non-empty strings")
        if "source" in r and not nonempty_str(r["source"]):
            self.errors.append("'source' must be a non-empty string when present")
        a = r.get("assembly")
        if not isinstance(a, dict) or "action" not in a:
            self.errors.append("'assembly' is required and must be a step (an object with 'action' and 'inputs')")
            return None
        return self.node(a, "assembly")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe", help="recipe JSON file")
    ap.add_argument("-o", "--out", help="output HTML path (default: alongside the JSON, .html)")
    ap.add_argument("--check", action="store_true", help="validate only; do not write HTML")
    args = ap.parse_args()

    try:
        with open(args.recipe, encoding="utf-8") as f:
            recipe = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read {args.recipe}: {e}", file=sys.stderr)
        sys.exit(2)

    c = Checker()
    dims = c.recipe(recipe)
    for w in c.warnings:
        print(f"WARN  {w}")
    if c.errors:
        for e in c.errors:
            print(f"FAIL  {e}")
        sys.exit(1)

    cols, rows = dims
    print(f"OK    {recipe['title']}: {len(recipe.get('before', []))} before-row(s); "
          f"{rows} ingredient row(s) x {cols + 1} column(s)")
    print("Ingredient roster (check every source ingredient appears, exactly once or as split portions):")
    for item in c.roster:
        print(f"  - {item}")

    if args.check:
        return

    try:
        with open(TEMPLATE, encoding="utf-8") as f:
            template = f.read()
    except OSError as e:
        print(f"ERROR: cannot read template {TEMPLATE}: {e}", file=sys.stderr)
        sys.exit(2)
    # "</" would let a value close the <script> element early.
    payload = json.dumps(recipe, ensure_ascii=False, indent=2).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, payload).replace(
        "<title>Recipe</title>", f"<title>{escape(recipe['title'])}</title>", 1)

    out = args.out or os.path.splitext(args.recipe)[0] + ".html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out}")


def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
