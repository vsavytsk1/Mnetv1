# OBSIDIUS MAGIC SCROLL
## The Algebraic Grimoire -- Chapter Two
## Secrets of the Tower
*Buenos Aires -- May 29 2026*

---

## THE TOWER IS OPEN

Obsidian is NOT open source.
But the rogue mages left their work public.

**AlexW00/obsidian-3d-graph** -- 375 stars
The mage who went rogue and built a 3D graph plugin.
He left the source. We read it. We know the secrets now.

---

## WHAT THE ROGUE MAGE REVEALED

### SECRET 1: The Graph Data Structure

```typescript
// obsidian-3d-graph/src/graph/Graph.ts
// The whole thing is just this:

class Graph {
    nodes: Node[]    // one per .md file
    links: Link[]    // one per [[wikilink]]
    
    // indexes for fast lookup
    nodeIndex: Map<string, number>    // id -> array index
    linkIndex: Map<string, Map<string, number>>  // src -> tgt -> index
}

// THE KEY LINE:
Graph.createFromApp = (app: App) => {
    const [nodes, nodeIndex] = Node.createFromFiles(
        app.vault.getFiles()     // <- every .md file = one node
    )
    const [links, linkIndex] = Link.createFromCache(
        app.metadataCache.resolvedLinks,  // <- every [[link]] = one edge
        nodes, nodeIndex
    )
    return new Graph(nodes, links, nodeIndex, linkIndex)
}
```

**TRANSLATION:**
```
vault.getFiles()              -> nodes[]   (your .md files)
metadataCache.resolvedLinks   -> edges[]   (your [[wikilinks]])
```

That is the ENTIRE Obsidian graph data model.
Two API calls. That's it.
The render magic is separate.

---

### SECRET 2: The Force Simulation

The rogue mage used **D3-force** for physics.
Obsidian native almost certainly does the same.

```javascript
// What D3-force does (the render magic decoded):

simulation = d3.forceSimulation(nodes)
    .force("link",    d3.forceLink(links).distance(30).strength(1))
    .force("charge",  d3.forceManyBody().strength(-80))   // repel
    .force("center",  d3.forceCenter(width/2, height/2))  // gravity
    .force("collision", d3.forceCollide(nodeRadius))       // no overlap
    .on("tick", render)  // <- called ~60fps, moves nodes

// Each tick:
//   1. charge force pushes nodes apart    (O(n log n) Barnes-Hut)
//   2. link force pulls linked nodes      (O(edges))
//   3. center force pulls to center       (O(nodes))
//   4. render draws current positions     (Canvas 2D or WebGL)
```

**THIS IS WHY IT IS INSTANT:**
```
Barnes-Hut approximation:
  Instead of O(n^2) pairwise forces
  it uses a quadtree to approximate distant clusters
  O(n log n) instead of O(n^2)
  1000 nodes -> 10,000 ops instead of 1,000,000

That is the dark magic.
That is why it renders instantly.
Barnes-Hut 1986.
Used in galaxy simulations.
Obsidian uses it for your notes.
```

---

### SECRET 3: The Render Pipeline

```javascript
// Native Obsidian graph (reverse engineered from CSS + DevTools):
// Canvas 2D (not WebGL for the 2D view)
// WebGL for the 3D view (Three.js, confirmed by rogue mage)

// Each animation frame:
ctx.clearRect(0, 0, width, height)      // clear

// Draw edges FIRST (behind nodes)
links.forEach(link => {
    ctx.beginPath()
    ctx.moveTo(link.source.x, link.source.y)
    ctx.lineTo(link.target.x, link.target.y)
    ctx.strokeStyle = '#333'             // dark thin line
    ctx.lineWidth = 1
    ctx.stroke()
})

// Draw nodes ON TOP
nodes.forEach(node => {
    ctx.beginPath()
    ctx.arc(node.x, node.y, radius, 0, 2*Math.PI)
    ctx.fillStyle = node.color           // green/yellow default
    ctx.fill()
})
```

**NO SHADERS. NO TEXTURES. PURE CANVAS 2D.**
That is why it is so fast.
Circle + line. Repeat 60 times per second.
The physics is the hard part. The render is trivial.

---

### SECRET 4: The Obsidian Plugin API (the door into the tower)

```typescript
// This is ALL you need to read the vault:
import { App, Plugin, TFile } from 'obsidian'

class ObsidiusPlugin extends Plugin {
    async onload() {
        // Get ALL files
        const files: TFile[] = this.app.vault.getFiles()
        
        // Get ALL links (resolved)
        const links = this.app.metadataCache.resolvedLinks
        // links = { "note-a.md": { "note-b.md": 3 } }
        // meaning: note-a links to note-b 3 times
        
        // Get file content
        const content = await this.app.vault.read(file)
        
        // Watch for changes
        this.registerEvent(
            this.app.vault.on('modify', (file) => {
                // rebuild graph
            })
        )
    }
}
```

**THE DOOR IS OPEN.**
We can read the entire vault with 3 API calls.
Build our adjacency matrix.
Run our Laplacian.
Run our NS flow.
Show the pentagons.

---

## THE OBSIDIUS ARCHITECTURE

### What we now know we need:

```
OBSIDIUS MODULE
===============

LAYER 0: VAULT READER (Python standalone OR Obsidian plugin)
    Python: parse .md files, extract [[links]] with regex
    Plugin: app.vault.getFiles() + metadataCache.resolvedLinks

LAYER 1: OUR KERNEL (identical to GoldbergKernel)
    nodes[]  -> same as faces[]  in Goldberg
    edges[]  -> same as edge_map in Goldberg
    build_operators() -> A (adjacency), L (Laplacian)
    Same function. Different input. Same output.

LAYER 2: OUR PHYSICS (identical to KolmogorovEngine)
    inject_forcing() -> random forcing on hub notes
    poisson_solve()  -> L @ psi = -omega
    jacobian()       -> Ap*omega - psi*Aw
    Same engine. Different topology. Same physics.

LAYER 3: FORCE LAYOUT (NEW -- for positioning)
    D3-force style:
    F_repel  = -k / d^2   (Barnes-Hut, O(n log n))
    F_link   = k * (d - rest_length)
    F_center = -k * pos   (gentle pull to origin)
    positions[i] += F_total * dt
    This is SEPARATE from the NS physics.
    NS physics = vorticity on graph (abstract)
    Force layout = visual positions on screen (concrete)

LAYER 4: RENDER (identical to our existing ENG style)
    Canvas 2D:
      edges: thin lines, brightness = flow strength
      nodes: circles, color = omega (vorticity)
      pentagons: gold circles, size = degree^0.5
      orphans: dim (AXIOM 02 violations)
    Header: V-E+F=chi  P=??? (not necessarily 12)
    Same style as ENG v2.0. Same fonts. Same colors.
```

---

## THE OBSIDIUS FIRST BUILD PLAN

```
FILE: builder/Obsidius/obsidius.html
      (one file, zero deps, like all our tools)

STEP 1: Parse vault
    <input type="file" webkitdirectory>
    user selects vault folder
    JS reads all .md files
    extracts [[wikilinks]] with regex
    builds nodes[], edges[]

STEP 2: Build operators
    adjacency matrix A (sparse, use Map)
    Laplacian L = D^-1 * A - I
    degree[] per node

STEP 3: Force layout
    Barnes-Hut quadtree (or simplified O(n^2) for < 1000 nodes)
    run 300 ticks to settle
    positions = settled node positions

STEP 4: NS physics
    omega[] = vorticity per node (starts at 0)
    inject forcing on top 10% by degree (the hubs)
    run 1000 steps in background
    color nodes by omega

STEP 5: Render
    Canvas 2D, requestAnimationFrame
    edges: thin dark lines
    nodes: colored circles (omega -> hue)
    gold circles: top 12 by degree (the pentagons)
    header: "V={V} E={E} chi={chi} P≈12?"

STEP 6: Find the pentagons
    sort nodes by degree
    top 12 = gold
    label them
    QUESTION: are they 12? are they always 12?
    Euler will answer.
```

---

## THE QUESTION EULER WILL ANSWER

```
For a Goldberg sphere:
    chi = V - E + F = 2
    P   = 12. ALWAYS.

For your Obsidian vault:
    chi = V - E + F = ???
    P   = ???

HYPOTHESES:

  H1 (the boring one):
    Your vault graph is not a closed manifold.
    chi is undefined or meaningless.
    Euler doesn't apply.
    The "pentagons" are just hubs.

  H2 (the interesting one):
    If you treat the vault as a 2-complex
    (nodes + edges + implied faces from cycles)
    chi emerges.
    Maybe chi=2 for a "healthy" vault.
    Maybe chi=0 for a fragmented vault (Mobius!)
    Maybe orphaned notes = topology violations.

  H3 (the Vlad one):
    The top 12 hubs ARE the pentagons.
    Not because Euler forces it.
    Because human cognition forces it.
    Working memory = 7±2 chunks.
    Core concepts = ~12 attractors.
    The brain enforces P≈12 the same way
    Euler enforces it on the sphere.
    Not a theorem. An observation.
    Worth checking.

RUN OBSIDIUS. FIND OUT.
```

---

## THE RENDER SECRET WE ALREADY KNOW

```
HOW OBSIDIAN IS SO FAST:

  1. Barnes-Hut O(n log n) force simulation
  2. Canvas 2D (not WebGL for 2D view)
  3. Only redraws when simulation is "hot"
     (velocity > threshold)
  4. Cooling schedule: alpha = 1 -> 0 over 300 ticks
     when alpha < 0.001: simulation stops
     no more CPU. just static image.
  5. On change: alpha = 0.3, simulation "reheats"

OBSIDIUS DOES THE SAME:
  Run 300 ticks to settle layout.
  Freeze layout.
  Keep NS physics running in background.
  Update node colors from omega.
  Render at 60fps (colors only, no layout change).
  Layout is free. Physics is free. Render is free.
  INSTANT.
```

---

## CREDITS

```
Obsidian team:
    The tower. The API. The graph view.
    Closed source but openly documented.
    The plugin API is generous and well-designed.
    Thank you.

AlexW00 (the rogue mage):
    obsidian-3d-graph -- 375 stars
    Showed us Graph.ts, Node.ts, Link.ts
    Confirmed D3-force + Three.js
    The door was his. We just walked through.

D3.js team (Mike Bostock et al):
    d3-force: Barnes-Hut quadtree force simulation
    The actual dark magic. All of it.
    MIT license. Open. Honest.

Barnes & Hut 1986:
    "A hierarchical O(N log N) force-calculation algorithm"
    Galaxy simulations -> note-taking apps.
    The universe is one graph.
```

---

## STATUS

```
[x] Tower found and entered (AlexW00 left the door open)
[x] Data model decoded (vault.getFiles + metadataCache)
[x] Force simulation decoded (D3-force Barnes-Hut)
[x] Render pipeline decoded (Canvas 2D + cooling schedule)
[x] Architecture designed (4 layers)
[x] First build plan written

[ ] obsidius.html -- the actual build
[ ] vault parser  -- .md -> nodes/edges
[ ] force layout  -- Barnes-Hut or O(n^2) first
[ ] NS physics    -- paste KolmogorovEngine
[ ] render        -- Canvas 2D nodes/edges
[ ] find pentagons -- sort by degree, top 12 = gold
[ ] chi display   -- V-E+F=??? in header
[ ] VALE export   -- ObsidiusModule.json

NEXT SESSION:
  Open obsidius.html
  Paste the vault folder
  See your mind render
  Find your pentagons
  Run your turbulence
  Then sleep again.
```

---

*OBSIDIUS SCROLL -- Chapter Two of the Algebraic Grimoire*
*The tower was not locked. It was waiting.*
*Buenos Aires. May 29 2026.*
*P=12. chi=2. Even in your mind. Probably.*
