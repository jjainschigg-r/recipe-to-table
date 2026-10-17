# Tabular recipe method

A conventional recipe (ingredient list + numbered prose steps) is rewritten as one table that shows **what to set up, what to combine, and in what order**, at a glance. Time runs top-to-bottom in the first region and left-to-right in the second.

## 1. The two regions

**Before (top).** Full-width rows, one per task, for everything that must happen before ingredients are worked: preheating, preparing pans (grease, flour, line), bringing a pot of water to the boil, softening butter or bringing eggs to room temperature, setting out equipment. These tasks are independent and can be done in any order, so each gets its own row spanning the whole table. List the longest lead time first (soften butter 1 hr → preheat → grease pan).

An ingredient whose listed state takes time to reach ("butter, softened", "eggs, at room temperature", "beans, soaked overnight", "frozen spinach, thawed") gets a Before row for reaching that state, with the time if the source gives one. The ingredient text still keeps the state as written.

**Assembly (bottom).** Ingredients in the left column, grouped by the phase in which they're used. Actions progress to the right, each action cell spanning the rows of every ingredient it acts on, until the rightmost column spans every row: the finished dish.

## 2. Classifying each step of the source recipe

For every sentence or clause in the method:

| The clause… | Goes to |
|---|---|
| sets up equipment or environment and works no listed ingredient (preheat, line pan, boil water) | a **Before** row |
| greases/dusts a pan with a listed ingredient ("butter and flour a loaf pan") | a **Before** row; the small amount is used up there and does not appear in the ingredient column |
| transforms one ingredient on its own (mash, melt, chop, toast, beat, sift) | that ingredient's **prep** |
| brings two or more things together (mix, whisk, fold, combine, toss), or works an already-combined mass | an **action** step whose inputs are those things |
| acts again on the same mass (bake, cool, slice, rest) | a further one-input action wrapping the previous one |
| adds an ingredient that needs no preparation of its own (vanilla into the wet mix) | that ingredient is a direct **input** of the step where it is added, with an empty prep cell |
| adds ingredients to a mass during one continuous operation: same bowl and tool, no other sub-assembly joining ("beat butter and sugars until creamy, then beat in eggs one at a time") | **one** action cell whose inputs include those ingredients, with the order in the text: "cream; beat in eggs one at a time" |
| moves the mass into a prepared vessel (pour into pan, drop onto sheets) | folded into the next cooking cell ("drop by rounded Tbs.; bake 375°F 9–11 min."), or left out when obvious (pour batter into the prepared pan) |
| is a doneness test, tip, substitution, storage or make-ahead advice | **notes** under the table |

Preparation already described in the ingredient list ("1/2 cup chopped walnuts", "1 onion, diced") stays in the ingredient text. So do qualifiers like "(optional)". The prep column is for things the *method* tells you to do.

## 3. Building the assembly tree

The assembly region is a tree. Leaves are ingredients, interior nodes are actions, and the root is the last thing you do.

1. **One leaf per ingredient line.** Copy amounts and units verbatim from the source, including any metric equivalents it gives. Do not convert units or rescale unless asked. This applies to temperatures in action cells too: the examples show "350°F (170°C)" only because their source gives both.
2. **Divided ingredients become several leaves.** If an ingredient is used in two phases, make one leaf per use with the portion stated: "3 Tbs. butter (of 6)", or "half the sugar" when the source doesn't quantify it.
3. **Group by phase.** Ingredients that are combined in the same action are siblings under that action, and so are adjacent rows. Independent sub-assemblies (wet mix, dry mix, sauce while pasta cooks) are sibling subtrees.
4. **Sequence is nesting.** "Mix, then bake, then cool" is cool(bake(mix(...))). Put parameters and cues into the cell text: "bake 350°F (170°C) 55 min.", "simmer until thickened".
   - **Start a new column** when another sub-assembly joins, or when the mass changes place or heat: bowl → oven → pan → rack. That's why bake, "cool 10 min. in pan" and "cool on wire rack" are three cells.
   - **Stay in the same cell** for additions within one continuous operation, and for transfers (see the §2 table).
   - Most recipes fit in about 7 columns. If yours is wider, look for steps that should merge under these rules before accepting the width.
5. **Late additions join where they're added.** An ingredient folded in at the end (nuts, garnish, salt to taste) is an input of that later step, not of an earlier group.
6. **Divided intermediates.** A tree cannot show a mass split in two. Reserve the portion as a leaf of the later step ("reserved 1/2 cup pasta water", "remaining glaze"), then explain in notes where it came from.
7. **Order rows** with the main sub-assembly first. That is the one the others are added into, the bowl that becomes the dish. For cookies, the dry mix is beaten into the creamed butter, so the creamed butter comes first. Then come the other sub-assemblies in source order, then late additions. Within a group, keep the source's ingredient order unless a different order makes the actions clearer.

### Cell text style

- Terse, lowercase imperatives: "mash", "lightly beat", "whisk", "fold", "cool on wire rack".
- Aim for no more than about six words, but critical numbers and doneness cues win over the word count. Shorten by dropping filler, never by rewording a cue: keep "until golden brown" if that's what the source says.
- Refer to Before-row equipment briefly: "onto prepared sheets".
- Anything longer belongs in notes.

## 4. Layout rules (deterministic)

These rules turn the tree into a grid. The bundled renderer implements them exactly. When rendering by hand, follow them literally.

1. A leaf with a prep is a one-input action wrapping the bare ingredient.
2. **Column** of an ingredient = 0. Column of an action = 1 + the largest column among its inputs. Every action therefore sits as far left as its inputs allow. A group of unprepared ingredients gets its group action in column 1 (e.g. "whisk").
3. **Rows**: one per ingredient leaf, in tree order (depth-first, inputs in order). An action cell spans exactly the rows of the leaves beneath it, so its rows are contiguous.
4. **Gaps**: when an input sits in column *c* and its parent action in column *p* > *c* + 1, the input's rows get **blank** cells in columns *c*+1 … *p*−1. In each such column, blanks of *adjacent* inputs of the same parent merge into one tall blank cell. A cell is never stretched sideways to fill a gap.
5. Total columns = root column + 1. Before-rows span all of them.
6. The root cell spans all ingredient rows. So does each action in the final chain (bake, cool, serve).

Worked check: the banana nut bread example (examples/banana-nut-bread.json) yields 10 rows × 7 columns. Vanilla has a blank cell in column 1. "whisk" sits in column 1. Walnuts have their own blank in column 1, plus one blank in column 2 that merges with the whisk group's blank (6 rows tall).

## 5. Data format

```json
{
  "title": "Banana Nut Bread",
  "yield": "about 10 servings",
  "before": ["Butter and flour a loaf pan", "Preheat oven to 350°F (170°C)"],
  "assembly": {
    "action": "cool on wire rack",
    "inputs": [
      { "action": "...", "inputs": [
          { "ingredient": "2 large (250 g) ripe bananas", "prep": "mash" },
          { "ingredient": "1 tsp. (5 mL) vanilla extract" }
      ] }
    ]
  },
  "notes": ["Done when a toothpick inserted in the center comes out clean."],
  "source": "optional attribution or URL"
}
```

- Required: `title`, `assembly` (must be an action at the root).
- Optional: `yield`, `before` (strings), `notes` (strings), `source`.
- Node = either `{"ingredient": str, "prep"?: str}` or `{"action": str, "inputs": [node, ...]}` with at least one input. No other keys.
- A one-input action whose input is a bare ingredient should be expressed as that ingredient's `prep` instead.

## 6. Conservation checklist (do this before presenting)

- [ ] Every ingredient in the source list appears exactly once as a leaf, or as split portions that add up to the whole, or is named in a Before row (pan greasing).
- [ ] Every step of the source method is represented by a cell or a note. Nothing is silently dropped.
- [ ] No Before row works an ingredient that should be in the tree.
- [ ] Amounts match the source verbatim.
- [ ] The rightmost column spans all ingredient rows.
- [ ] Ambiguities *in the source* that you resolved are stated in notes (e.g. "source doesn't say when to add salt; added with dry ingredients"). Structural choices such as row order or merging don't go in notes. Mention those when you report back.
- [ ] Notes contain only information from the source, plus those resolutions. Never add tips or claims of your own.
