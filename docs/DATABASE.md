# THE DATABASE ? Smallest, Most Efficient, Good Good
*graphs + vectors + markdown + latex in one file*

---

## THE ANSWER: SQLite + sqlite-vec

**One file. Zero server. Ships with Python. Handles everything.**

---

## Why SQLite Wins (10 bullets)

1. **Already installed** ? `import sqlite3` is built into Python. No pip install. No server. No config. It's THERE.

2. **Single `.db` file** ? your entire database is ONE FILE on disk. Copy it, email it, git it, put it on a USB stick. Done.

3. **600KB** ? the entire SQLite library is 600KB. Your math tree v2.6 HTML is bigger.

4. **Handles our 4 types natively:**
   - **Graphs** ? `nodes` table + `edges` table (classic adjacency list)
   - **Vectors** ? `sqlite-vec` extension: `pip install sqlite-vec` ? KNN search, float arrays
   - **Markdown** ? TEXT columns. Just store the raw markdown string.
   - **LaTeX** ? TEXT columns. `"\\frac{\\sin x}{x}"` is just a string.

5. **Used by EVERYTHING** ? every iPhone, every Android, every Chrome browser, every Firefox, every Skype, every iTunes. Literally the most deployed database on Earth. ~1 trillion databases active.

6. **JSON support built in** ? `json_extract()`, `json_each()`. Store tree structures as JSON columns, query into them.

7. **Full text search** ? FTS5 extension. Search through markdown and LaTeX content: `WHERE content MATCH 'derivative'`.

8. **Transactions are atomic** ? write 1000 nodes at once, if anything fails, nothing changes. ACID compliant.

9. **sqlite-vec for vectors** ? Mozilla-sponsored extension. Store embeddings, do KNN nearest-neighbor search. `WHERE embedding MATCH '[0.5, 0.3, ...]' ORDER BY distance LIMIT 5`. Find similar equations by meaning.

10. **Plays with pandas** ? `pd.read_sql('SELECT * FROM nodes', conn)` ? DataFrame. `df.to_sql('nodes', conn)` ? back to SQLite. Round-trip in one line.

---

## Our Schema

```sql
-- THE MATH TREE DATABASE

-- Nodes: every equation/concept/challenge
CREATE TABLE nodes (
    id          TEXT PRIMARY KEY,     -- 'eq0', 't1', 't2r'
    tag         TEXT NOT NULL,        -- 'START', 'L'H?PITAL', 'DEAD END'
    type        TEXT NOT NULL,        -- 'root', 'tool', 'result', 'dead'
    latex       TEXT NOT NULL,        -- '\\frac{\\sin x}{x}'
    sub         TEXT,                 -- 'click to explore'
    cost        INTEGER DEFAULT 1,   -- token cost to unlock
    xp          INTEGER DEFAULT 5,   -- XP reward
    parent_id   TEXT,                 -- FK to parent node (NULL for root)
    depth       INTEGER DEFAULT 0,   -- tree depth level
    topic       TEXT,                 -- 'limits', 'derivatives', etc.
    markdown    TEXT,                 -- extended explanation in markdown
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Edges: connections between nodes
CREATE TABLE edges (
    from_id     TEXT NOT NULL,
    to_id       TEXT NOT NULL,
    label       TEXT,                 -- edge label if needed
    weight      REAL DEFAULT 1.0,    -- for graph algorithms
    PRIMARY KEY (from_id, to_id),
    FOREIGN KEY (from_id) REFERENCES nodes(id),
    FOREIGN KEY (to_id) REFERENCES nodes(id)
);

-- Vectors: equation embeddings for similarity search
-- (using sqlite-vec extension)
CREATE VIRTUAL TABLE vec_equations USING vec0(
    embedding float[384]             -- sentence-transformer dimensions
);

-- User progress: what has been explored
CREATE TABLE progress (
    node_id     TEXT NOT NULL,
    opened_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_spent INTEGER DEFAULT 0,
    xp_earned   INTEGER DEFAULT 0
);

-- Trees: multiple starting equations
CREATE TABLE trees (
    id          TEXT PRIMARY KEY,     -- 'sinx_over_x', 'epsilon_delta'
    title       TEXT NOT NULL,        -- 'lim sin(x)/x'
    root_id     TEXT NOT NULL,        -- FK to root node
    topic       TEXT,
    difficulty  INTEGER DEFAULT 1
);
```

---

## The Pipeline with SQLite

```
[CSV/Excel]
    ?  pd.read_csv() ? df.to_sql('nodes', conn)
[SQLite .db file]
    ?  pd.read_sql('SELECT * FROM nodes WHERE topic="limits"', conn)
[DataFrame]
    ?  df.to_json(orient='records') ? build nested tree
[JSON tree]
    ?  inject into HTML template
[math_tree_v2.6.html]
    ?  user clicks
[progress table]  ? track what they explored
```

---

## Alternatives Considered

| Database | Size | Vectors | Why Not |
|----------|------|---------|---------|
| **SQLite** | 600KB | via sqlite-vec | **WINNER** |
| DuckDB | 20MB | no native | overkill for our graph size |
| TinyDB | 50KB | no | no SQL, no joins, too simple |
| LanceDB | 5MB | native | vector-focused, not graph-focused |
| ChromaDB | 30MB | native | needs server, too heavy |
| PostgreSQL | 200MB+ | pgvector | needs server. we need ONE FILE |
| Neo4j | 500MB+ | no | graph-native but MASSIVE |

**SQLite + sqlite-vec = graphs + vectors + markdown + latex in one 600KB file.**
That's good good.

---

## Install (one line)

```bash
pip install sqlite-vec pandas
```

That's it. `sqlite3` is already in Python. We're ready.

---

*"Nothing NASA but good good"*
*? Vlad, Buenos Aires, still the same session*
