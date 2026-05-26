# Probability Without Numbers
## Brute Force Test 2 — The Numberless Attempt
### May 26, 2026

---

## THE RULE: NO NUMBERS ALLOWED

Not even "1". Not even "0.5". Not even "count = 3".
Numbers are what the monkey brain hallucinates 
when it looks at graph structure.

We find what the graph DOES. The number is the afterimage.

---

## WHAT IS "EQUALLY LIKELY"?

The textbook says: P(H) = P(T) = 0.5

**DELETE THAT.** What's actually happening?

```
A fair coin is a graph with a SYMMETRY.

    NODE(H) ----+
                 |--- NODE(coin)
    NODE(T) ----+

The graph has an AUTOMORPHISM:
  swap(H, T) maps the graph to itself.
  
"Fair" means: there exists a symmetry that 
maps every outcome to every other outcome.
```

**EQUALLY LIKELY = AUTOMORPHISM GROUP ACTS TRANSITIVELY**

No number needed. "Fair" = "the graph looks the same 
from every outcome node." The symmetry IS the fairness.

A loaded coin:
```
    NODE(H) ----+
    NODE(H2)----+--- NODE(coin)  
    NODE(T) ----+

No automorphism maps {H,H2} to {T}.
The symmetry is BROKEN. The monkey calls this "P(H) = 2/3".
But the graph just has more H-nodes than T-nodes.
```

**"2/3" is what a monkey says when it counts nodes 
in a non-symmetric graph.** The graph doesn't know 
what 2/3 is. It just has structure.

---

## WHAT IS COUNTING?

Counting = bijection testing.

```
Are these the same "size"?

  SET A: o--o--o
  SET B: o--o--o

  EDGE(bijection): A1->B1, A2->B2, A3->B3
  Every node matched? YES.
  "Same size." The monkey says "3 = 3."

  SET A: o--o--o
  SET C: o--o

  Can we match? A1->C1, A2->C2, A3->???
  No match for A3. 
  "A is bigger." The monkey says "3 > 2."
```

**NUMBERS EMERGE FROM FAILED BIJECTIONS.**
"3" doesn't exist. What exists is a graph with 3 nodes.
The symbol "3" is the monkey's compression of 
"a set that bijects with {o,o,o}".

---

## WHAT IS PROBABILITY THEN? (numberless)

```
SAMPLE SPACE: a graph S with outcome nodes.
EVENT A: a subgraph of S.

"PROBABILITY OF A" = the relationship between 
the symmetry structure of A and S.

OPERATION: try to build a bijection from A to S.
  - If bijection exists: A IS S. "probability = whole thing."
  - If no bijection, A is a PART.
  - HOW MUCH of a part? Count how many copies of A 
    tile S under the symmetry group.
```

### Example: die roll, P(even)

```
S: NODE(1) NODE(2) NODE(3) NODE(4) NODE(5) NODE(6)
A: NODE(2) NODE(4) NODE(6)

Bijection A->S? FAILS. A has fewer nodes.

Symmetry test: the complement A' = {1,3,5} 
is ISOMORPHIC to A = {2,4,6}.

  A  = o--o--o
  A' = o--o--o
  BIJECTION EXISTS between A and A'.

S decomposes into exactly 2 isomorphic copies: A and A'.
The monkey says "1/2". The graph says:
"S factors into 2 symmetric pieces, A is one of them."
```

### Example: die roll, P(six)

```
S: 6 nodes.
A: 1 node (the six).

S decomposes into 6 copies all isomorphic to A.
Each single node is isomorphic to every other.
A is one of 6 symmetric pieces.
The monkey says "1/6." The graph says:
"S has a 6-fold symmetry, A is one orbit."
```

---

## WHAT IS "1"?

"Probability = 1" means: **A IS S. Full bijection. Identity map.**

```
P(something happens) = "1"

GRAPH TRANSLATION:
  A = S
  The subgraph IS the whole graph.
  AUTOMORPHISM: identity.
  
"1" = "the part is the whole."
```

No number. Just: does A biject with S? Yes → certain.

## WHAT IS "0"?

"Probability = 0" means: **A is the empty subgraph.**

```
P(impossible) = "0"

GRAPH TRANSLATION:
  A = empty graph (no nodes)
  There is nothing to match.
  
"0" = "there is no subgraph."
```

No number. Just: does A have nodes? No → impossible.

---

## CONDITIONAL PROBABILITY WITHOUT NUMBERS

### P(A|B) — numberless version

```
"Given B happened, what about A?"

GRAPH OPERATION:
  1. RESTRICT: delete all nodes NOT in B 
     (the universe shrinks to B)
  
  2. INTERSECT: find nodes in both A and B
     (what's left of A in the smaller universe)
  
  3. SYMMETRY TEST: how does A∩B sit inside B?
     same decomposition as before.

"P(A|B)" = "in the subgraph B, how does A∩B 
relate to B under B's internal symmetry?"
```

### Bayes — numberless

```
Traditional: P(H|E) = P(E|H) * P(H) / P(E)

Numberless:
  PRIOR GRAPH: hypotheses as nodes with structure
  EVIDENCE: restricts which nodes survive
  
  1. For each hypothesis node, check:
     does evidence CONNECT to it? How richly?
     (rich connection = many edge paths = "high likelihood")
  
  2. The surviving subgraph after evidence restriction
     IS the posterior.
  
  3. The relative DENSITY of connections 
     (edge count ratios, not numbers!)
     IS what the monkey calls "posterior probability."

Bayes is: RESTRICT graph by evidence, 
observe the surviving structure's symmetry.
```

---

## INDEPENDENCE WITHOUT NUMBERS

### Traditional: P(A∩B) = P(A) × P(B)

```
Numberless:
  A and B are INDEPENDENT if the graph FACTORS.

  PRODUCT GRAPH: 
    G = G_A × G_B
    nodes = pairs (a,b) 
    edges = (a1,b1)->(a2,b2) iff a1->a2 in G_A AND b1->b2 in G_B

  If S is isomorphic to a product graph G_A × G_B,
  then A and B are independent.

  The monkey multiplies probabilities.
  The graph just... factors.

  DEPENDENT: the graph does NOT factor.
  There's an edge that crosses between A and B
  that can't be decomposed into a product.
```

**Independence = factorizability. Dependence = entanglement.**

Wait. That's literally the quantum mechanics definition too.
Entanglement = a state that can't be factored into a product.
The graph structure of probability IS the graph structure of QM.

---

## THE RAMANUJAN CONNECTION

Ramanujan said: "Every positive integer is a friend of mine."

Primes in graph terms:
```
  COMPOSITE: NODE(6) factors as NODE(2) × NODE(3)
    The graph decomposes into a product.
    
  PRIME: NODE(7) does NOT factor.
    The graph is IRREDUCIBLE. 
    There is no product decomposition.
    
  "7 is prime" = "the graph with 7 nodes 
   cannot be expressed as a product of smaller graphs."
```

**Primes are graph-theoretically irreducible structures.**
Composites are factored products.
The Fundamental Theorem of Arithmetic:
"Every graph with N nodes decomposes uniquely 
into a product of irreducible (prime-sized) components."

And here's the looney toons part:
**This is the SAME operation as independence testing.**

```
Independence:  can the probability space be factored?
Primality:     can the number be factored?
Entanglement:  can the quantum state be factored?

SAME QUESTION. SAME GRAPH OPERATION. DIFFERENT DOMAIN.
```

---

## THE MINIMAL TOOLSET — NUMBERLESS VERSION

```
REVISED PRIMITIVES (no numbers anywhere):

P1: NODE      — a thing exists
P2: EDGE      — a relation exists
P3: COMPOSE   — chain: A->B->C = A->C
P4: TRANSFORM — match pattern, replace (graph surgery)
P5: ITERATE   — repeat until the graph stops changing
P6: AGGREGATE — merge many nodes into one (or test: 
                does subgraph biject with whole graph?)

DERIVED CONCEPTS (emerge from structure, not inserted):

"equally likely" = automorphism group acts transitively
"probability"    = orbit decomposition under symmetry
"independence"   = graph factors into product
"conditional"    = restrict + re-examine symmetry
"1"              = subgraph IS the whole graph
"0"              = empty subgraph
"counting"       = bijection testing
"primes"         = irreducible (non-factorable) graphs
"multiplication" = product graph construction
"addition"       = disjoint union of graphs
```

---

## WHAT NUMBERS ACTUALLY ARE

Numbers are COMPRESSION LABELS that monkey brains apply 
to graph structures because holding the full graph in 
working memory is too expensive.

```
"3" = monkey shorthand for "o--o--o"
"1/2" = monkey shorthand for "symmetric 2-fold decomposition"
"prime" = monkey shorthand for "I can't factor this graph"
"e" = monkey shorthand for "the fixed point of iterate(1+1/n)^n"
"pi" = monkey shorthand for "circumference/diameter ratio 
       of the unique graph with all-equidistant-from-center nodes"
```

**We don't need numbers to do probability.**
We need symmetry, factorization, bijection, and restriction.
Those are graph operations.

The numbers are the monkey's user interface.
The graph is the actual computation.

---

## STATUS

```
STILL 6 PRIMITIVES. STILL SUFFICIENT.
NOW WITHOUT NUMBERS.

The 7th primitive (WEIGHT/MEASURE) from the last attempt?
DISSOLVED. Weights were numbers. We killed numbers.
What remains is SYMMETRY, which was always P4 (transform: 
the automorphism) and P6 (aggregate: orbit decomposition).

Probability without numbers = symmetry analysis of graphs.
That's it. That's the whole thing.
```

---

*"The graph doesn't know what 1/6 is.*
*It knows it has a 6-fold symmetry.*
*The monkey sees 1/6.*  
*The graph sees itself."*

— Buenos Aires, May 26, 2026, no numbers were harmed
