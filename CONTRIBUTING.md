# Contributing

Issues and pull requests are welcome.

## Reporting a bad chart

The most useful report has three parts:

1. The source recipe, or a link to it.
2. The JSON that Claude produced. In Claude Code it's the `.json` file next to the HTML page. In Claude.ai, ask Claude to show it.
3. What you expected instead, and which rule in `references/method.md` you think it broke or failed to cover.

## Changing the rules or the renderer

- **The rules** live in `skills/recipe-to-table/references/method.md`. If you change one, add or update an example in `examples/` that exercises it.
- **The layout** is drawn only by the script in `skills/recipe-to-table/assets/recipe-table.html`, and `render.py` only checks and embeds the JSON. Keep it that way, so Claude Code and Claude.ai draw identical tables. If you change the layout, update the expected layout in `tests/test_layout.mjs`.
- **Run the tests** before opening a pull request:

  ```bash
  python3 -m unittest discover -s tests
  node tests/test_layout.mjs
  ```

- **Release-affecting changes** need a version bump in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, plus a `CHANGELOG.md` entry. A test checks that all three agree.
