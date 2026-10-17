"""Tests for skills/recipe-to-table/scripts/render.py.

Usage: python3 -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SKILL = os.path.join(ROOT, "skills", "recipe-to-table")
RENDER = os.path.join(SKILL, "scripts", "render.py")
EXAMPLES = os.path.join(SKILL, "examples")


def run(recipe_path, *args):
    return subprocess.run([sys.executable, RENDER, recipe_path, *args], capture_output=True, text=True)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, recipe):
        path = os.path.join(self.tmp.name, "recipe.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(recipe, f)
        return path

    def test_examples_render(self):
        shapes = {
            "banana-nut-bread.json": "10 ingredient row(s) x 7 column(s)",
            "chocolate-chip-cookies.json": "10 ingredient row(s) x 7 column(s)",
            "spaghetti-carbonara.json": "8 ingredient row(s) x 4 column(s)",
        }
        for name, shape in shapes.items():
            with self.subTest(name):
                out = os.path.join(self.tmp.name, name.replace(".json", ".html"))
                r = run(os.path.join(EXAMPLES, name), "-o", out)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn(shape, r.stdout)
                self.assertNotIn("WARN", r.stdout)
                with open(out, encoding="utf-8") as f:
                    html = f.read()
                self.assertNotIn("__RECIPE_JSON__", html)

    def test_check_writes_nothing(self):
        path = self.write({"title": "t", "assembly": {"action": "a", "inputs": [{"ingredient": "x"}, {"ingredient": "y"}]}})
        r = run(path, "--check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertFalse(os.path.exists(path.replace(".json", ".html")))

    def test_invalid_recipes_fail(self):
        cases = {
            "missing title": {"assembly": {"action": "a", "inputs": [{"ingredient": "x"}]}},
            "leaf at root": {"title": "t", "assembly": {"ingredient": "x"}},
            "empty inputs": {"title": "t", "assembly": {"action": "a", "inputs": []}},
            "unknown node": {"title": "t", "assembly": {"action": "a", "inputs": [{"bogus": 1}]}},
            "extra key": {"title": "t", "assembly": {"action": "a", "inputs": [{"ingredient": "x", "qty": 1}]}},
            "bad before": {"title": "t", "before": "preheat", "assembly": {"action": "a", "inputs": [{"ingredient": "x"}]}},
        }
        for name, recipe in cases.items():
            with self.subTest(name):
                r = run(self.write(recipe), "--check")
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("FAIL", r.stdout)

    def test_single_bare_ingredient_step_warns(self):
        r = run(self.write({"title": "t", "assembly": {"action": "chop", "inputs": [{"ingredient": "x"}]}}), "--check")
        self.assertEqual(r.returncode, 0)
        self.assertIn("WARN", r.stdout)

    def test_script_close_tag_is_escaped(self):
        path = self.write({
            "title": "A <b> & C",
            "assembly": {"action": "mix", "inputs": [{"ingredient": "x </script> y"}, {"ingredient": "z"}]},
        })
        r = run(path)
        self.assertEqual(r.returncode, 0, r.stdout)
        with open(path.replace(".json", ".html"), encoding="utf-8") as f:
            html = f.read()
        self.assertIn("x <\\/script> y", html)
        self.assertIn("<title>A &lt;b&gt; &amp; C</title>", html)


class ReleaseTest(unittest.TestCase):
    def test_versions_agree(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as f:
            plugin = json.load(f)["version"]
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as f:
            listed = json.load(f)["plugins"][0]["version"]
        with open(os.path.join(ROOT, "CHANGELOG.md")) as f:
            latest = next(line for line in f if line.startswith("## ["))
        self.assertEqual(plugin, listed, "plugin.json and marketplace.json versions differ")
        self.assertTrue(latest.startswith(f"## [{plugin}]"), f"CHANGELOG's latest entry isn't {plugin}: {latest!r}")


if __name__ == "__main__":
    unittest.main()
