---
name: recipe-to-table
description: Rewrites a conventional recipe (ingredient list + prose method) as a tabular recipe chart — setup tasks as full-width rows on top, then ingredients grouped by phase on the left with actions progressing left-to-right in merged cells until the final step spans every row. Use when the user pastes, links, or names a recipe and asks to rewrite, tabulate, chart, diagram, or "convert" it, or mentions Cooking-for-Engineers-style recipe tables.
---

# Recipe to table

Turn a standard recipe into a tabular recipe chart, rendered as a self-contained HTML page.

All paths below are relative to this skill's directory. The rules live in `references/method.md`. Read it in full before your first rewrite in a session. This file covers only the workflow.

## Step 1 — Get the recipe

Accept pasted text, an uploaded or local file, or a URL. For a URL, fetch the page and pull out the ingredient list and method, ignoring everything else on it. If the user didn't supply a recipe, ask for one. If the source has no ingredient list or no method, say what's missing instead of inventing it.

## Step 2 — Build the recipe JSON

Following method.md:

1. Sort every method clause into Before, prep, action, or note (§2).
2. Build the assembly tree (§3). Copy amounts verbatim.
3. Write the JSON (§5) to `<slug>.json`, where `<slug>` is the title in kebab-case. Put it in the current directory, or wherever the user asked. If that file already exists and isn't the recipe you're revising, add a numeric suffix (`-2`) instead of overwriting it.

`examples/banana-nut-bread.json` is the reference shape. `examples/chocolate-chip-cookies.json` shows lead-time Before rows, additions within one continuous operation, and a transfer folded into the bake cell. `examples/spaghetti-carbonara.json` shows divided ingredients, parallel sub-assemblies, and a reserved intermediate.

## Step 3 — Render and validate

If you can run Python 3, render with the bundled script:

```bash
python3 <skill-dir>/scripts/render.py <slug>.json
```

It writes `<slug>.html` beside the JSON and prints the ingredient roster. Fix every `FAIL` and re-run. Treat each `WARN` as a prompt to reconsider; fix it unless you have a reason not to.

If you can't run Python, build the page yourself from `assets/recipe-table.html`. Copy it exactly, with two changes:

- Replace `__RECIPE_JSON__` with the JSON. Write any `</` inside a string as `<\/`.
- Replace `<title>Recipe</title>` with the recipe's title.

Don't alter the template's CSS or JavaScript. Its script lays out the table, so never write table HTML by hand. Check the JSON against the node rules in method.md §5 yourself, since the script isn't there to do it. Present the page as an HTML artifact or file.

Either way, walk the conservation checklist (method.md §6) against the source recipe. Fix any missing, duplicated, or altered ingredient, and any dropped step, then render again.

## Step 4 — Report

Say where the HTML page is, and give a short list of the judgement calls you made: ambiguities resolved, divided ingredients, steps merged, row order chosen, anything moved to notes. If you're working on the user's own machine, offer to open the page in their browser.

If the user asks for changes (different grouping, terser cells, metric amounts), edit the JSON and render again. Never hand-edit the table.
