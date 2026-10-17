// Runs the renderer embedded in assets/recipe-table.html against a minimal fake
// DOM and checks the grid it produces. The banana nut bread expectation is the
// reference chart the notation was specified from (docs/banana-nut-bread.png).
//
// Usage: node tests/test_layout.mjs
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import assert from "node:assert/strict";
import vm from "node:vm";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const skill = join(root, "skills", "recipe-to-table");
const template = readFileSync(join(skill, "assets", "recipe-table.html"), "utf8");
const renderer = template.match(/<script>([\s\S]*?)<\/script>/)[1];

class FakeElement {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.className = "";
    this.textContent = "";
    this.rowSpan = 1;
    this.colSpan = 1;
  }
  appendChild(child) { this.children.push(child); return child; }
}

function render(recipe) {
  const out = new FakeElement("main");
  const data = { textContent: JSON.stringify(recipe) };
  const document = {
    title: "",
    createElement: (tag) => new FakeElement(tag),
    createTextNode: (text) => ({ tag: "#text", textContent: text, children: [] }),
    getElementById: (id) => (id === "out" ? out : data),
  };
  vm.runInNewContext(renderer, { document });
  const error = out.children.find((c) => c.className === "error");
  if (error) throw new Error(error.textContent);
  const table = out.children.find((c) => c.className === "scroll").children[0];
  return { document, rows: table.children[0].children };
}

// Each row as "kind:text[:rowspan]" strings, with colspan noted for before-rows.
function describe(rows) {
  return rows.map((tr) =>
    tr.children.map((td) => {
      let s = `${td.className}:${td.textContent}`;
      if (td.rowSpan > 1) s += `:${td.rowSpan}`;
      if (td.colSpan > 1) s += `:colspan=${td.colSpan}`;
      return s;
    }),
  );
}

function example(name) {
  return JSON.parse(readFileSync(join(skill, "examples", `${name}.json`), "utf8"));
}

const tests = {
  "banana nut bread matches the reference chart"() {
    const { document, rows } = render(example("banana-nut-bread"));
    assert.equal(document.title, "Banana Nut Bread");
    assert.deepEqual(describe(rows), [
      ["before:Butter and flour a loaf pan:colspan=7"],
      ["before:Preheat oven to 350°F (170°C):colspan=7"],
      [
        "ingredient:2 large (250 g) ripe bananas", "action:mash", "action:mash until smooth:4",
        "action:fold:10", "action:bake 350°F (170°C) 55 min.:10", "action:cool 10 min. in pan:10",
        "action:cool on wire rack:10",
      ],
      ["ingredient:6 Tbs. (90 mL) butter", "action:melt"],
      ["ingredient:1 tsp. (5 mL) vanilla extract", "blank:"],
      ["ingredient:2 large eggs", "action:lightly beat"],
      ["ingredient:1-1/3 cups (167 g) all-purpose flour", "action:whisk:5", "blank::6"],
      ["ingredient:2/3 cup (130 g) sugar"],
      ["ingredient:1/2 tsp. (2.3 g) baking soda"],
      ["ingredient:1/4 tsp. (1.2 g) baking powder"],
      ["ingredient:1/2 tsp. (3 g) salt"],
      ["ingredient:1/2 cup (70 g) chopped walnuts", "blank:"],
    ]);
  },

  "every row of every example fills the full width"() {
    for (const name of ["banana-nut-bread", "chocolate-chip-cookies", "spaghetti-carbonara"]) {
      const { rows } = render(example(name));
      const ncols = rows[0].children[0].colSpan;
      // Walk the grid, tracking cells still occupied by rowspans from above.
      const carry = new Array(ncols).fill(0);
      rows.forEach((tr, r) => {
        if (tr.children[0].className === "before") return;
        let col = 0;
        for (const td of tr.children) {
          while (carry[col] > 0) col++;
          carry[col] = td.rowSpan;
          col++;
        }
        while (col < ncols && carry[col] > 0) col++;
        assert.equal(col, ncols, `${name}: row ${r} covers ${col} of ${ncols} columns`);
        for (let c = 0; c < ncols; c++) carry[c] = Math.max(0, carry[c] - 1);
      });
    }
  },

  "a leaf with prep sits in column 1; gaps merge only between adjacent inputs"() {
    const { rows } = render({
      title: "t",
      assembly: {
        action: "finish",
        inputs: [
          { ingredient: "a" },
          { action: "pair", inputs: [{ ingredient: "b", prep: "chop" }, { ingredient: "c" }] },
          { ingredient: "d" },
        ],
      },
    });
    assert.deepEqual(describe(rows), [
      ["ingredient:a", "blank:", "blank:", "action:finish:4"],
      ["ingredient:b", "action:chop", "action:pair:2"],
      ["ingredient:c", "blank:"],
      ["ingredient:d", "blank:", "blank:"],
    ]);
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try {
    fn();
    console.log(`ok    ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL  ${name}\n${err.message}`);
  }
}
process.exit(failed ? 1 : 0);
