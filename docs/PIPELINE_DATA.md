# THE PIPELINE ? Python ? LaTeX ? Tree
*"What THE FUCK is LaTeX" ? "What THE FUCK is pandas" ? now what?*
*Buenos Aires ? May 25 2026, same session as v1.0 to v2.6*

---

## 1. PANDAS ? What It Is

1. **Spreadsheet in Python** ? Excel but code. `pd.read_csv()` ? table in memory.
2. **DataFrame** ? 2D table, rows ? columns. The core object.
3. **Series** ? single column. DataFrame = dict of Series.
4. **Reads ANYTHING** ? CSV, JSON, Excel, SQL, HTML. One function.
5. **Filtering** ? `df[df['x'] > 5]` = one line SQL WHERE.
6. **GroupBy** ? `df.groupby('type').mean()` = SQL GROUP BY in one line.
7. **Apply/Map** ? `df['x'].apply(func)` runs any function on every value.
8. **Joins** ? `pd.merge(df1, df2, on='id')` = SQL JOIN.
9. **Exports ANYTHING** ? `.to_csv()`, `.to_json()`, `.to_html()`, `.to_dict()`.
10. **WHY FOR US** ? tree data (nodes, edges, types, costs, latex) = a table.
    One CSV ? infinite math trees.

---

## 2. LATEX ? What It Is

1. **Typing language for math** ? `\frac{sin x}{x}` ? beautiful fraction.
2. **Donald Knuth, 1978** ? got pissed at ugly typesetting, built TeX. 10 years.
3. **Not a word processor** ? markup language, like HTML but for math.
4. **Every scientific paper** ? physics, math, CS. If it has equations, it's LaTeX.
5. **KaTeX** ? LaTeX for the web. Same syntax, renders in browser. Our tree uses it.
6. **Backslash commands** ? `\sin`, `\frac{}{}`, `\sqrt{}`, `\int`, `\sum`, `\lim`.
7. **Curly braces group** ? `\frac{a+b}{c+d}` = whole expressions top/bottom.
8. **Plain text** ? `.tex` is just text. Diffable, greppable, storable in JSON.
9. **WHY FOR US** ? tree nodes store LaTeX strings. KaTeX renders them.
   Math = data. Rendering = automatic. Separation of concerns.
10. **20 commands** ? `\frac`, `\sqrt`, `\sum`, `\int`, `\lim`, `\to`, `\infty`,
    `\leq`, `\geq`, `\approx`, `\boxed`, `^{}`, `_{}`, `\text{}`. That's LaTeX.

---

## 3. CALCULUS ? PANDAS ? The Map (38 entries)

Saved as: `tree/calculus_pandas_map.csv` (opens in Excel)
Also as: `tree/calculus_pandas_map.txt` (quick reference)

### Categories:
| Category | # Entries | Key pandas functions |
|----------|-----------|---------------------|
| Limits | 5 | `.iloc[-1]`, `.interpolate()`, `.cumsum().diff()` |
| Derivatives | 6 | `.diff()`, `.pct_change()`, boolean masks |
| Integrals | 5 | `.cumsum()`, `np.trapz()`, `.rolling().mean()` |
| Series | 5 | `.cumsum()`, `.dot()`, list comprehensions |
| DiffEq | 3 | `.shift()`, meshgrid DataFrames |
| Stats | 6 | `.mean()`, `.var()`, `.corr()`, `.rank(pct=True)` |
| Transform | 5 | `.apply(np.log)`, `.apply(np.sin)`, chained |
| Multi | 3 | `.diff()` matrix, `.pivot_table()`, parametric index |

### The Pattern:
```
Calculus operation     ?  pandas one-liner
f'(x)                 ?  df['y'].diff() / df['x'].diff()
?f(x)dx               ?  df['y'].cumsum() * dx
lim f(x)              ?  df.interpolate()
? a?                  ?  s.cumsum()
f(g(x))               ?  df['x'].apply(g).apply(f)
```

---

## 4. THE DILEMMA ? The Full Pipeline

```
                    THE DREAM
                    =========

  [Python + pandas]     ?    does the MATH
        ?
  [LaTeX strings]       ?    formats the DISPLAY
        ?  
  [JSON tree]           ?    structures the EXPLORATION
        ?
  [HTML engine v2.6]    ?    renders the EXPERIENCE
        ?
  [User clicks]         ?    discovers the UNDERSTANDING
```

### What we have:
- ? HTML tree engine (v2.6, 17 versions, battle-tested)
- ? KaTeX rendering (LaTeX ? browser)
- ? JSON tree structure (nodes, children, types, costs, latex)
- ? Calculus ? pandas map (38 operations)
- ? MNet design language
- ? Console/debug/sandbox

### What we need:
- ?? Python script that GENERATES tree JSON from a starting equation
- ?? Pandas reads a CSV of math topics ? builds tree automatically
- ?? LaTeX strings generated programmatically (not hand-typed)
- ?? The FUNNY ROUTE (TBD ? Vlad has a plan)

---

## 5. FILES

```
SACRED_MATH_TREE.md                              ? main guide + dev log
tree/calculus_pandas_map.csv                      ? 38 calculus?pandas entries
tree/calculus_pandas_map.txt                      ? quick text reference
tree/math_tree_v1.html through v2.6.html          ? 17 versions
tree/ideas/01.01gs_graph_game_concept.jpg          ? original sketch
```

---

*"There is our dilemma... full port python latex"*
*"We will take the FUNNY route"*

*? Vlad, still the same session, Buenos Aires, May 25 2026*
*The pipeline is clear. The route is funny. Let's go.*
