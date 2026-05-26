# Probability as Graph Theory
## The Careful Attempt — May 26, 2026

### The honest question
Can we represent ALL of probability using only:
P1:NODE  P2:EDGE  P3:COMPOSE  P4:TRANSFORM  P5:ITERATE  P6:AGGREGATE?

Or do we need a 7th primitive?

---

## LAYER 1: Discrete Probability (easy, obviously works)

### A coin flip
```
GRAPH:
  NODE(H)  --weight:0.5-->  NODE(prob)
  NODE(T)  --weight:0.5-->  NODE(prob)
  
  AGGREGATE(weights) = 1.0   <-- this MUST hold
```

### A die roll  
```
  NODE(1) --1/6--> NODE(p)
  NODE(2) --1/6--> NODE(p)
  ...
  NODE(6) --1/6--> NODE(p)
  
  P(even) = AGGREGATE(nodes {2,4,6}) = 3/6 = 0.5
```

Fine. Probability = weighted graph. Each outcome is a node.
Weight = labeled edge. AGGREGATE gives us probability of events.

**But wait.** We just smuggled something in: the WEIGHT.
The weight is a real number on an edge. Where does that come from?
Answer: it's just a labeled edge. Labels are data ON edges.
We already have labeled edges in our tree (cost, xp, type).
A weight is just another label. OK, no new primitive needed.

**But ALSO wait.** There's a CONSTRAINT: weights must sum to 1.
Where does normalization live in our 6 primitives?

---

## THE NORMALIZATION PROBLEM

This is the first real issue. In pure graph theory:
- You can put any number on any edge
- Nothing forces them to sum to 1
- But probability REQUIRES this

### Option A: Normalization as TRANSFORM (P4)
```
RULE: after any graph modification, apply:
  TRANSFORM(weight_i -> weight_i / AGGREGATE(all weights))
```
This is a rewrite rule that fires after every change.
It's a P4 that uses P6 internally. No new primitive.

### Option B: Normalization as CONSTRAINT (new primitive?)
```
P7?: CONSTRAINT — an invariant that must hold after every operation
  CONSTRAINT(AGGREGATE(all weights in partition) = 1)
```

**Verdict:** Option A works. A constraint IS a transform rule that 
auto-fires. We don't need P7. But it's ugly. Keep this tension.

---

## LAYER 2: Conditional Probability (this is where it gets good)

### P(A|B) = P(A and B) / P(B)

```
START GRAPH:
  NODE(w1: rain,    umbrella)  weight: 0.3
  NODE(w2: rain,    no umbrella) weight: 0.1  
  NODE(w3: no rain, umbrella)  weight: 0.2
  NODE(w4: no rain, no umbrella) weight: 0.4

QUESTION: P(umbrella | rain)?

STEP 1 — TRANSFORM: delete all nodes where rain=false
  Remove NODE(w3), NODE(w4)
  Remaining: NODE(w1)=0.3, NODE(w2)=0.1

STEP 2 — TRANSFORM: renormalize
  total = AGGREGATE(0.3 + 0.1) = 0.4
  TRANSFORM(0.3 -> 0.3/0.4 = 0.75)
  TRANSFORM(0.1 -> 0.1/0.4 = 0.25)

ANSWER: P(umbrella | rain) = 0.75
```

**CONDITIONING IS GRAPH SURGERY.**
- Delete nodes that don't match condition (TRANSFORM)
- Renormalize remaining weights (AGGREGATE + TRANSFORM)
- That's it. Two graph operations.

---

## LAYER 3: Bayes' Theorem (pure graph composition)

### P(H|E) = P(E|H) * P(H) / P(E)

```
PRIOR GRAPH (what we believe before evidence):
  NODE(sick)    weight: 0.01
  NODE(healthy) weight: 0.99

LIKELIHOOD EDGES (how evidence relates to hypotheses):
  EDGE(test+|sick)    = 0.95   "test positive given sick"
  EDGE(test+|healthy) = 0.05   "false positive rate"

BAYES UPDATE — 3 transforms:
  1. TRANSFORM: multiply each prior by its likelihood
     sick:    0.01 * 0.95 = 0.0095
     healthy: 0.99 * 0.05 = 0.0495

  2. AGGREGATE: P(E) = 0.0095 + 0.0495 = 0.059

  3. TRANSFORM: normalize
     P(sick|test+)    = 0.0095/0.059 = 0.161 (16.1%!)
     P(healthy|test+) = 0.0495/0.059 = 0.839 (83.9%)
```

**Bayes IS:**
```
COMPOSE(prior_graph, likelihood_edges) 
  -> TRANSFORM(multiply) 
  -> AGGREGATE(marginal) 
  -> TRANSFORM(normalize)
```

P3 + P4 + P6 + P4. Four primitives. No magic.

The famous "base rate neglect" is literally failing to do step 2 (AGGREGATE).
The human brain skips P6 and goes straight to the likelihood.

---

## LAYER 4: Random Variables (edges to value space)

### X: omega -> R  "a random variable"

```
A random variable is just an EDGE from outcome nodes to value nodes.

GRAPH:
  NODE(HH) --X=2--> NODE(val:2)    P=0.25
  NODE(HT) --X=1--> NODE(val:1)    P=0.25
  NODE(TH) --X=1--> NODE(val:1)    P=0.25
  NODE(TT) --X=0--> NODE(val:0)    P=0.25

E[X] = AGGREGATE(value * weight for each node)
     = 2*0.25 + 1*0.25 + 1*0.25 + 0*0.25
     = 1.0
```

Expectation = P6 (aggregate). Variance = P6 applied twice.
Random variable = P2 (edge to value space).

**Functions of random variables:**
g(X) = COMPOSE(X_edge, g_edge)  -- P3!

E[g(X)] = AGGREGATE(g(value) * weight) -- P6

---

## LAYER 5: Markov Chains (probability IS a graph already)

```
This is the punchline. Markov chains ARE weighted directed graphs.

STATES: NODE(sunny), NODE(rainy), NODE(cloudy)

TRANSITIONS (edges with weights):
  sunny  --0.7--> sunny     (stays sunny)
  sunny  --0.2--> cloudy
  sunny  --0.1--> rainy
  rainy  --0.3--> rainy
  rainy  --0.4--> cloudy
  rainy  --0.3--> sunny
  cloudy --0.3--> sunny
  cloudy --0.4--> cloudy
  cloudy --0.3--> rainy

CONSTRAINT: outgoing weights from each node sum to 1

Stationary distribution:
  ITERATE(multiply state vector by transition matrix)   -- P5!
  until fixed point: pi = pi * T

PageRank is literally this. Google's $2 trillion algorithm
is ITERATE on a weighted directed graph until fixed point.
```

**Markov chains need ZERO new primitives.** They ARE the primitives.

---

## LAYER 6: Continuous Probability (the hard case)

### The Gaussian: P(x) = (1/sqrt(2*pi)) * e^(-x^2/2)

Problem: uncountably infinite outcomes. Can't have a node per outcome.

### Option A: Discretize (the computer way)
```
Approximate with N bins:
  NODE(x=-3.0) weight: 0.004
  NODE(x=-2.5) weight: 0.018
  NODE(x=-2.0) weight: 0.054
  ...
  NODE(x=+3.0) weight: 0.004

ITERATE: N -> infinity, bin width -> 0    -- P5
LIMIT of discrete graphs = continuous distribution
```

This is what EVERY computer does. Monte Carlo, histograms, 
numerical integration — it's all "discretize then iterate."

### Option B: The density as a RULE (the math way)
```
Instead of one node per outcome, store the RULE that generates weights:

NODE(gaussian) with TRANSFORM RULE:
  "given x, output (1/sqrt(2pi)) * e^(-x^2/2)"

This is a P4 (transform) that takes a query node and returns a weight.
The continuous distribution is a LAZY GRAPH — it generates nodes on demand.
```

### Option C: Measure Theory (the rigorous way)
```
Sigma-algebra = a GRAPH of sets with operations:
  NODE(empty_set)
  NODE(omega)  -- full sample space
  EDGE(subset, A, omega) for each measurable set A
  TRANSFORM: complement(A) -> omega\A
  TRANSFORM: union(A,B) -> A cup B  
  TRANSFORM: intersect(A,B) -> A cap B
  CONSTRAINT: closed under complement and countable union

Measure mu:
  EDGE(mu, measurable_set, value_in_[0,1])
  CONSTRAINT: mu(omega) = 1
  CONSTRAINT: mu(disjoint union) = sum of mu (countable additivity)

Countable additivity = ITERATE(sum) over AGGREGATE(disjoint pieces)
```

**Measure theory in 6 primitives:**
```
  Sigma-algebra = P1(nodes=sets) + P4(transform=set operations)
  Measure       = P2(edge=assignment) + P6(aggregate=additivity)  
  Integration   = P5(iterate=partition refinement) + P6(aggregate=sum)
  Convergence   = P5(iterate) with fixed-point detection
```

No new primitive needed. But it's DENSE. This is where "brute force 
the mapping" from the handbook kicks in — it's not elegant, but it works.

---

## LAYER 7: Independence (the subtle one)

### P(A and B) = P(A) * P(B)  iff A,B independent

```
In graph terms:
  Two subgraphs are INDEPENDENT if there is NO path between them.

  DEPENDENT:    NODE(A) --edge--> NODE(B)     path exists
  INDEPENDENT:  NODE(A)           NODE(B)     disconnected components

But wait — in probability, independence is about the WEIGHTS,
not the graph structure. Two events can be in the same sample space
(connected) but still independent.

RESOLUTION: independence = a PROPERTY of the weight labeling.
  Check: weight(A and B) == weight(A) * weight(B)
  This is a CONSTRAINT (auto-firing TRANSFORM).

Or: independence = the graph FACTORS into a product graph.
  GRAPH(A x B) has nodes = pairs (a,b)
  weights = weight(a) * weight(b)  
  The product graph structure IS independence.
```

**Independence = graph factorization.** 
When a probability graph factors into disconnected product components,
those components are independent. This is actually a theorem in 
algebraic graph theory.

---

## VERDICT ON PROBABILITY

```
CONCEPT               PRIMITIVE(S) USED         NATURAL?
────────────────────────────────────────────────────────
Sample space           P1 (nodes)               trivial
Events                 P1 (subset of nodes)     trivial  
Probability            P2 (weighted edge)       natural
Conditioning           P4 (delete+renorm)       beautiful
Bayes theorem          P3+P4+P6                 elegant
Random variable        P2 (edge to values)      natural
Expectation            P6 (aggregate)           perfect
Markov chains          P1+P2+P5 (THE GRAPH)     IT IS GRAPHS
Continuous dist        P5 (iterate to limit)    standard
Measure theory         P4+P6 (transform+aggr)   dense but works
Independence           factored product graph   deep
Convergence theorems   P5 (iterate+fixpoint)    standard
────────────────────────────────────────────────────────
```

### DO WE NEED A 7TH PRIMITIVE?

**The candidate: WEIGHT / MEASURE**
- A number assigned to a node or edge
- Subject to normalization constraint

**The argument FOR P7:**
Weights with constraints are so fundamental to probability
that pretending they're "just labeled edges" hides the structure.
Normalization (sum=1) is not a transform — it's a LAW.

**The argument AGAINST P7:**
Weights are labels. Labels are data on edges. We already have 
labeled edges. Normalization is a transform rule that auto-fires.
Adding P7 is like adding "color" as a primitive to geometry —
it's useful but not irreducible.

**FINAL ANSWER: 6 primitives are SUFFICIENT but not comfortable.**
Probability works in our framework. But it works like assembly language —
correct but painful. A "sugar" layer (P7: WEIGHT/MEASURE) makes it 
human-readable without adding computational power.

Same conclusion as before: minimal for humans = 6.
Minimal for machines = 4. 
Comfortable for probability = 7.

The choice depends on what you're building.
We're building for humans. Keep 6. Note the tension. Move on.

---

*"The machine IS the equation materialized.*
*The weight IS the edge labeled.*  
*The normalization IS the transform that never stops firing."*

— Buenos Aires, May 26, 2026
