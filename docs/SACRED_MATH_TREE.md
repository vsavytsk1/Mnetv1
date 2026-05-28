# THE SACRED MATH TREE ? Design Bible
*A visual decision-tree engine for mathematics*
*If ADHD can't SEE it, it doesn't exist. If it CAN... F_gauge = 7.*
*Buenos Aires ? May 2026*

---

## 0. THE CORE INSIGHT

The human brain ? especially the ADHD brain ? does not learn math from textbooks.
It learns from **seeing the whole tree at once**.

When you can SEE every branch, every dead end, every path that works...
the monkey brain goes: "OHHH. THAT'S what calculus IS."

This is not metaphor. It is backed by:
- Lowrie 2019: spatial visualization training transfers to math performance
- Royal Society: spatial reasoning is malleable and broadly supports math
- Corter & Zahner 2007: external visual representations reduce cognitive load
- 10,000 years of World Tree symbolism across every culture on Earth

The tree is the oldest human technology for understanding complexity.
We are building the next version of it.

---

## 1. WHAT WE ARE BUILDING

A single-file HTML engine that renders math as an **interactive decision tree**.

```
You see: ONE node. "What is a limit?"
You click: 3 branches appear.
  Branch A: "Formal (epsilon-delta)" 
  Branch B: "Intuitive (approaching)" 
  Branch C: "Visual (zoom in forever)"
You pick B. New node opens. Challenge appears.
  "What does f(x) = 2x approach as x -> 3?"
  [ ] 5  [ ] 6  [ ] 7  [ ] undefined
You answer 6. GREEN. Branch grows.
  Two new paths open from your answer.
You pick wrong? RED. Branch dies. But you SEE it.
  The dead branch stays visible. You learn from its shape.
```

When you zoom out ? you see the WHOLE TREE.
Every path you took. Every dead end. Every victory.
**The tree IS your understanding.**

---

## 2. THE 3 BOOKS (Resources)

### Book 1: D3.js ? Data-Driven Documents
- **What:** The industry standard for interactive graph/tree visualization
- **Why:** d3.tree() and d3.hierarchy() give us collapsible, animated trees
- **Key API:**
  - `d3.hierarchy(data)` ? build tree from nested JSON
  - `d3.tree().size([width, height])` ? compute layout positions
  - `d3.linkHorizontal()` ? draw curved links between nodes
  - Transitions: `d3.transition().duration(500)` ? animate branch growth
- **URL:** https://d3js.org / https://observablehq.com/@d3/tree
- **License:** ISC (free)

### Book 2: Red Blob Games (Amit Patel)
- **What:** The gold standard for interactive math explanations
- **Why:** Every page is a draggable, clickable visual proof
- **Key techniques:**
  - Pointer events (unified mouse + touch)
  - SVG for crisp math diagrams
  - State machines for interaction (drag, click, hover)
  - Immediate feedback: change input ? see output
- **URL:** https://www.redblobgames.com
- **Philosophy:** "Make the reader INTERACT with the math"
- **Directly relevant:** Hex grid guide = our hex_bible.csv ancestor

### Book 3: Observable / Mike Bostock's Collapsible Trees
- **What:** Live-editable interactive notebooks with tree visualizations  
- **Why:** Collapsible tree = our decision tree. Click node ? children appear.
- **Key pattern:**
  - Data = nested JSON: `{name, children: [{name, children: [...]}]}`
  - Layout = d3.tree() computes x,y for every node
  - Interaction = click node ? toggle children visibility ? re-layout
  - Animation = nodes slide into position, links grow
- **URL:** https://observablehq.com/@d3/collapsible-tree
- **This is EXACTLY the UX we want.** Click ? branch grows. Click again ? collapses.

---

## 3. OUR ARCHITECTURE

### The Tree Data Structure
```javascript
// Every math concept = a node
// Every choice/path = an edge to a child
const CALCULUS_TREE = {
  id: "root",
  label: "Calculus",
  type: "domain",        // domain | concept | challenge | dead_end
  children: [
    {
      id: "limits",
      label: "What is a Limit?",
      type: "concept",
      latex: "\\lim_{x \\to a} f(x) = L",
      children: [
        {
          id: "limit_formal",
          label: "Formal Definition",
          type: "concept",
          latex: "\\forall \\epsilon > 0, \\exists \\delta > 0 : |x-a|<\\delta \\Rightarrow |f(x)-L|<\\epsilon",
          children: [
            {
              id: "challenge_epsilon",
              label: "Find delta for epsilon = 0.1",
              type: "challenge",
              question: "f(x) = 2x, a = 3, L = 6. If epsilon = 0.1, what is delta?",
              options: ["0.01", "0.05", "0.1", "1.0"],
              answer: 1,  // index of correct (0.05)
              children: []  // grows on correct answer
            }
          ]
        },
        {
          id: "limit_intuitive", 
          label: "Intuitive: Approaching",
          type: "concept",
          latex: "\\text{As } x \\to 3, f(x) = 2x \\to ?",
          children: [
            {
              id: "challenge_approach",
              label: "What does 2x approach?",
              type: "challenge",
              question: "As x approaches 3, what does f(x) = 2x approach?",
              options: ["5", "6", "7", "undefined"],
              answer: 1,
              children: []
            }
          ]
        },
        {
          id: "limit_visual",
          label: "Visual: Zoom In Forever",
          type: "concept",
          latex: "\\text{Magnify the graph at } x = a",
          children: []
        }
      ]
    }
  ]
};
```

### The Rendering Engine
```
KERNEL (pure data, no DOM):
  TreeNode { id, label, type, latex, children, state }
  TreeState { expanded: Set<id>, solved: Set<id>, failed: Set<id> }
  expand(state, nodeId) -> newState
  solve(state, nodeId, answer) -> newState
  getVisibleNodes(tree, state) -> [{node, x, y, parent}]

RENDERER (SVG + d3 or vanilla):
  For each visible node:
    Draw circle (color by type)
    Draw label (text)
    Draw LaTeX (KaTeX)
    Draw link to parent (curved line)
  
  On click:
    If concept -> expand children (animate in)
    If challenge -> show options
    If dead_end -> shake + red flash

ANIMATION:
  New nodes slide in from parent position
  Links grow from parent to child
  Solved nodes glow green
  Failed branches go translucent
```

### The Connection to Our Kernel
```
MachineNet GK kernel          Math Tree Engine
---------------------         ----------------
GK.buildC60()            ->   buildTree(CALCULUS_TREE)
GK.refineOne(face)       ->   expand(node) 
GK.undo()                ->   collapse(node)
GK.invariants()          ->   treeStats() {total, solved, failed, depth}
face.type = 'pent'       ->   node.type = 'concept'
face.type = 'hex'        ->   node.type = 'challenge'
chi = 2 (converges)      ->   all challenges solved (tree complete)
chi = 0 (diverges)       ->   stuck in dead ends (tree incomplete)
F5 = 12 (always)         ->   core concepts = always visible anchors
```

**The Goldberg kernel IS a tree engine.**
We just need to put math content in the nodes instead of geometry.

---

## 4. THE FIRST PROTOTYPE (what we build NOW)

### Target: Definition of a Limit ? One Interactive Tree

**One HTML file. No build step. KaTeX for LaTeX. SVG for the tree.**

Features:
1. Root node: "Limits" ? click to expand
2. 3 branches: Formal / Intuitive / Visual
3. Each branch has 1 challenge
4. Correct answer = branch grows (new concept appears)
5. Wrong answer = branch turns red (stays visible as dead end)
6. Zoom out = see the whole tree
7. Counter: "3/5 concepts unlocked"

Tech:
- Single HTML file (~500 lines)
- KaTeX from CDN for LaTeX rendering
- SVG for tree layout (no d3 needed for v1 ? manual positioning)
- CSS transitions for animation
- Mobile-friendly (pointer events)

### Why Start with Limits?
- Universal: every calculus student needs this
- Branching: formal vs intuitive vs visual are natural paths
- Testable: epsilon-delta has numeric answers
- Visual: "zoom in on graph" IS the visual branch
- Connected: leads to derivatives, continuity, series
- The tree GROWS into all of calculus from this one root

---

## 5. THE VISION (where this goes)

```
Level 0: One tree. One topic. Limits.
Level 1: Tree of trees. Calculus has 12 roots (like pentagons).
Level 2: The tree IS the C60. 12 math domains = 12 pentagons.
         Each domain = a sub-tree you can zoom into.
Level 3: VR. The tree floats in front of you. You grab branches.
         Quest 3. The math tree is the World Tree.
Level 4: The tree remembers YOU. StrangerDanger handshake.
         It knows which branches you've explored.
         It shows you what you haven't tried yet.
Level 5: Multiplayer. Your tree touches someone else's tree.
         Where they overlap = shared knowledge.
         Where they differ = teaching opportunity.
```

---

## 6. THE SACRED TREE CONNECTION

Every culture has the World Tree:
- Judaism: Etz Chaim (Tree of Life) ? 10 sephiroth, 22 paths
- Norse: Yggdrasil ? 9 worlds connected by roots and branches
- Hindu: Ashvattha ? inverted tree, roots in heaven
- Buddhism: Bodhi Tree ? the site of awakening
- Christianity: Tree of Life in Eden and Revelation

Our math tree is the same archetype in digital form:
- Roots = axioms (hidden foundations)
- Trunk = core definitions (the path up)
- Branches = different approaches (formal, intuitive, visual)
- Leaves = solved problems (the fruit)
- Dead branches = wrong paths (visible, learned from)
- Seeing the whole tree = gnosis / insight / the ADHD moment

**The structure itself carries archetypal weight.**
That's why it feels divine even when it's "just" calculus.

---

## 7. PSYCHOLOGY (why this works)

From the research:
- Spatial visualization training transfers to math (Lowrie 2019, effect size 0.39-0.43)
- External visual representations reduce cognitive load (Corter & Zahner 2007)
- Spatial reasoning is malleable at any age (Royal Society)
- Decision trees are particularly useful for conditional reasoning
- Over time, external trees become internal mental models

**The game accelerates turning external visual strategy into internal visual intuition.**

---

## 8. IMPLEMENTATION NOTES

### Environment Limits (Vlad's PC)
- Can't hold long dense operations in read or write
- Always use Python heredoc for large file writes
- OneDrive paths with spaces break tools
- Test files crash IL2CPP if in wrong folder
- KaTeX from CDN, not local (saves space)

### File Locations
```
PROTOTYPE:  C:\Users\vladi\OneDrive\Desktop\python devs\MNetv1\tree\
            OR inside current Mnet repo: tree/ folder
HTML:       math_tree_v1.html (single file, < 800 lines)
DATA:       calculus_tree.json (the tree structure)
GUIDE:      SACRED_MATH_TREE.md (this file)
```

### The Rule
- The tree data is separate from the renderer
- New topics = new JSON, same engine
- The engine is the kernel. The content is the faces.
- Same architecture as goldberg_kernel.js + machinenet_shell.html

---

*The tree is the oldest technology. The math is the newest content.*
*Put them together. See everything at once.*
*The monkey brain does the rest.*

*Buenos Aires ? May 2026*
*Don't Panic.*


---

## 9. DEVELOPMENT LOG ? v1.0 to v1.8

*"Horrible dev. Amazing for monkey brain to locate later."*

### v1.0 ? First Breath (math_tree_v1.html)
- SVG circles + KaTeX labels
- Click node ? expand children
- Challenge system: multiple choice, correct = green, wrong = red
- Pan + zoom (transform scale ? blurry)
- Tree grows sideways (horizontal)
- **Status:** Proof of concept. It works. Ugly but alive.

### v1.1 ? Fake 3D + Gacha (math_tree_v1.1.html)
- Switched to fake 3D: perspective + rotateX(50deg) tilted plane
- Circles ? **rectangles with LaTeX inside** (the boxes ARE the content)
- **GACHA MECHANIC BORN:**
  - 3 starting tokens ??
  - Each branch costs 1-2 tokens to open
  - XP for opening (purple flying numbers)
  - Streak system ?? (3=+2, 5=+3, 8=+5 bonus tokens)
  - COMBO counter (rapid clicks = "3x COMBO" gold text)
  - Results + dead ends give tokens back (exploration rewarded)
- Tree: sin(x)/x with 4 tools (Direct Sub, L'H?pital, Squeeze, Taylor)
- **Status:** The dopamine loop works. Gacha is crack.

### v1.2 ? Hanging Tree (math_tree_v1.2.html)
- Tree grows **DOWNWARD** (Ashvattha ? inverted sacred tree!)
- Root at top, branches hang down
- Operations as floating purple pill buttons orbiting below parent
- 3D perspective from above looking down
- **Status:** Direction correct but 3D tilt too aggressive.

### v1.3 ? The Flat Wall (math_tree_v1.3.html)
- **REMOVED all 3D tilt** ? flat wall, staring at a blackboard
- The board IS the if-space itself
- translate + scale only, no perspective, no rotateX
- Centered on root, tree grows straight down
- Zoom toward mouse position
- **Status:** The vibe is RIGHT. But text blurry when zoomed out.

### v1.4 ? Sharp Palette (math_tree_v1.4.html)
- **CSS zoom instead of transform scale** = text stays SHARP at every zoom level
- New palette: white LaTeX, gold relations, purple operators
- Per-type box tints (warm root, cool tool, green result, red dead)
- **Status:** MUCH better. Crisp. Professional.

### v1.5 ? The Breathing Tree (math_tree_v1.5.html)
- **THE KEY MECHANIC:** every click triggers full re-layout
- All nodes slide smoothly to new positions (cubic-bezier 700ms)
- Other branches SHIFT ? eye catches them ? "what's THAT..." ? dopamine
- Freeze flash on click
- Ghost nodes ? unopened children as dashed ?? boxes at 35% opacity
- DOM reuse ? positions updated, CSS transitions animate
- **Status:** The breathing works. The tree is alive.

### v1.6 ? Boxes ARE Clicks (math_tree_v1.6.html)
- REMOVED purple op-btn pills ? click the boxes directly
- Mysterious start: ONE lonely golden box, nothing else
- First click ? children CASCADE in as ghosts
- HOVER token badge ? ?? cost in upper-right corner ONLY on hover
- Waviness slider ? controls curve of connection lines
- **Status:** Elegant. The hover badge is chef's kiss.

### v1.7 ? Pre-rendered Kernel (math_tree_v1.7.html)
- ALL nodes built at init ? every box, every KaTeX, in DOM, positioned, hidden
- Nothing created at click time ? only CSS classes flip: hidden ? ghost ? alive
- "The math is absolute" ? same as GK kernel
- Stop-time animation: flash ? line traces ? box materializes ? content fades
- Lines start as background color ? invisible until traced
- **Status:** Architecture correct. Click animation needs work.

### v1.8 ? Forward Only (math_tree_v1.8.html)
- Root at TOP ? 20% from top edge, tree flows DOWN
- Lines touch CENTER-BOTTOM ? CENTER-TOP ? measured actual box heights
- Ghosts at 45% opacity ? much more visible
- **NO COLLAPSE** ? once opened, stays open FOREVER
- Forward-only clicking ? only ghosts unlock, alive nodes do nothing
- **Status:** WORKING. The complete click sequence fires correctly.

### v1.9 ? Sharp Connections (math_tree_v1.9.html)
- Internal glow animation ? flash happens INSIDE the clicked box, not screen overlay
- Box heights measured properly for line anchoring
- XP popups half-size (11px)
- `transform-origin: 50% 0%` ? scale animations anchor from center-top
- **Status:** Internal animations feel right. Boxes connect better.

### v2.0 ? The Console Returns (math_tree_v2.0.html)
- **CONSOLE** ? the classic MNet debug panel, bottom of screen
- Hover ? expands to 220px, **auto-selects all text** for copy
- Color-coded logs:
  - Gold: clicks (ALIVE, REVEAL KIDS, UNLOCK)
  - Purple: token changes
  - Green: XP gains
  - Grey: state info (build, boxH, zoom, pan)
  - Red: errors (NOT ENOUGH tokens)
- Millisecond timestamps on everything
- **Status:** Can SEE what the engine does. Debug gold.

### v2.1 ? Fixed Width Boxes (math_tree_v2.1.html)
- Boxes forced to `width:300px` ? visual center now EXACTLY at layout X
- Lines properly connect center-bottom ? center-top
- XP popups halved again
- Debug logging: box positions, path d attributes in console
- **Status:** Connection geometry correct. Console proves it.

### v2.2 ? The Sandbox (math_tree_v2.2.html)
- **4 SLIDERS** replacing single wave slider:
  - wave: connection curve waviness (0 ? 100)
  - spread: horizontal node distance (0.3x ? 2.0x, controls XSP)
  - depth: vertical level distance (0.3x ? 2.0x, controls DY)
  - zoom lock: minimum zoom to interact (off ? 100%)
- **Smooth relayout** on slider drag ? all boxes slide with cubic-bezier
- Zoom gate check on all click handlers
- **Kernel reuse:** spread/depth = same spring constants from force-directed graph
- **Status:** The tree parameters are now controllable. Same math, boxes not atoms.

### v2.3 ? The Grid Breathes (math_tree_v2.3.html)
- **Canvas grid** behind everything ? MNet cyan (#00d4ff) at barely-there opacity
- Grid spacing responds to spread/depth sliders
- Minor grid (0.018 opacity) + major grid every 4th line (0.035)
- Center crosshair at root X position
- Sliders restyled: MNet cyan, custom thumbs, backdrop-blur panel
- **Status:** The space itself responds to parameters. Metric is visible.

### v2.4 ? Papyrus Banner (math_tree_v2.4.html)
- **ZOOM GATE BANNER** in Papyrus font (like Avatar, those lazy bastards)
- "zoom in, wanderer / read the equation before you touch it"
- Shows current zoom % vs required %
- Full-width bottom bar with all sliders horizontal
- Console moved above bottom bar
- **Status:** Anti-speedrun mechanic. Papyrus is peak comedy.

### v2.5 ? MNet Design Language (math_tree_v2.5.html)
- **Exact MNet proportions** pulled from vsavytsk1.github.io/Mnetv1/
- HUD top-left: `.lbl{color:#555}` `.val{color:#80d0ff}` ? dynamic zoom, all params
- Log panel: floating, `rgba(5,5,16,0.85)`, `border:#1a1f2e`, 280px max
- Bottom bar: `rgba(5,5,16,0.95)`, `accent-color:#ff69b4` (MNet pink!)
- `.sl` labels: 8px uppercase, letter-spacing 0.12em
- Tokens/XP moved to top-right, 9px, 60% opacity
- **Status:** One family with MNet. Same visual DNA.

### v2.6 ? The Shame Slider (math_tree_v2.6.html) ? CURRENT
- **SHAME slider** ? controls Papyrus banner duration
- Range: 0.5 seconds (mercy) ? 10 seconds (full punishment)
- Shows in HUD as `shame 10.0s`
- Console logs duration changes
- Set lock to 100%, shame to 10s, zoom out, click = 10 seconds of Papyrus
- **Status:** The user controls their own punishment. Peak game design.

---

## 10. DISCOVERED PRINCIPLES

### The Exploration Mechanic
> Start with ONE equation. See what tools math gives you.
> Pick one. See what happens. "Cool cool cool... what if THIS?"
> The exploration IS the learning. The tree IS the understanding.
> At the speed of the dopamine goblin.

### The Kernel Architecture
> Render ALL always. Hide with CSS. Reveal with class changes.
> The math is absolute. Positions pre-computed. Only visuals change.
> Same as GK.buildC60() ? Euler forces the topology. We choose what to SEE.

### The Sacred Tree
> Every culture's World Tree = our decision tree.
> Roots = axioms. Branches = approaches. Leaves = solved problems.
> Dead branches = visible lessons. Seeing the whole tree = gnosis.

### Forward-Only
> You can't hide what you discovered. Once open, stays open.
> The tree only grows. Life is exploring possibilities because we can.

---

## 11. NEXT: v2.7+

```
1. More math trees (different starting equations)
2. Force-directed layout (full kernel reuse)
3. Breathing relayout on every click
4. Sound design?
5. Mobile touch support
6. The tree of trees (meta-tree connecting multiple equations)
```

## Files
```
SACRED_MATH_TREE.md                           ? this file
tree/math_tree_v1.html                        ? v1.0 first breath
tree/math_tree_v1.1.html                      ? v1.1 gacha born
tree/math_tree_v1.2.html                      ? v1.2 hanging tree
tree/math_tree_v1.3.html                      ? v1.3 flat wall
tree/math_tree_v1.4.html                      ? v1.4 sharp palette
tree/math_tree_v1.5.html                      ? v1.5 breathing tree
tree/math_tree_v1.6.html                      ? v1.6 boxes ARE clicks
tree/math_tree_v1.7.html                      ? v1.7 pre-rendered kernel
tree/math_tree_v1.8.html                      ? v1.8 forward only
tree/math_tree_v1.9.html                      ? v1.9 sharp connections
tree/math_tree_v2.0.html                      ? v2.0 console returns
tree/math_tree_v2.1.html                      ? v2.1 fixed width boxes
tree/math_tree_v2.2.html                      ? v2.2 the sandbox
tree/math_tree_v2.3.html                      ? v2.3 grid breathes
tree/math_tree_v2.4.html                      ? v2.4 papyrus banner
tree/math_tree_v2.5.html                      ? v2.5 MNet design language
tree/math_tree_v2.6.html                      ? v2.6 shame slider (CURRENT)
tree/ideas/01.01gs_graph_game_concept.jpg     ? Vlad's sketch
```

## Research
```
C:\Users\vladi\Downloads\Sacred_Tree_Symbolism_Across_Religions.md
C:\Users\vladi\Downloads\Psychology_of_Visual_Math_Decision_Trees.md
```

---

*"I have no real idea if this is true.*
*The first thing that comes to mind and I think mmm how funny.*
*Divine shit. Fun stuff. Let's continue and push."*

*? Vlad, 6 AM, Buenos Aires, May 25 2026*

*"zoom in, wanderer. read the equation before you touch it."*
*? Papyrus banner, shame slider at 10s*

*17 versions in one session. The tree grows because you walked it.*
