# Gsndbx3testClrsMath — Graph Sandbox Coloring & Math Test

## What's Here

| File | Description |
|------|-------------|
| `v3_0_centroid_fan.html` | Film strategy: findTriangles + centroid fan fallback |
| `v3_1_face_walker.html` | Film strategy: planar face walker (angular half-edge) |
| `v3_2_cmd.html` | v3.1 + command interface (`cmd()`, `batch()`, `state()`) |
| `run.py` | Python launcher + benchmark sequences |

## Quick Test

```powershell
cd Gsndbx3testClrsMath
python run.py            # opens sandbox, prints console commands
python run.py --bench    # prints face walker benchmark to paste in DevTools
python run.py --demo     # all demo sequences
```

## Console API (F12 → Console)

```js
cmd('HEX')                                      // single command → {ok, time_ms, nodes, edges}
cmd('FRACTALIZE')                                // subdivide
batch(['HEX','FRACTALIZE','FRACTALIZE','GRAB'])  // chain → {total_ms, results[]}
state()                                          // full state dump
findFaces(graphs.A)                              // raw face walker access
```

## Commands

| Category | Commands |
|----------|----------|
| Graph | `A`, `B` |
| Tools | `NODE`, `EDGE`, `MOVE`, `GRAB`, `DELETE` |
| Shapes | `PENT`, `HEX`, `C60`, `POLY 7`, `RANDOM` |
| Math | `ALGEBRA`, `MANDELBROT` |
| Ops | `FRACTALIZE`, `MOBIUSIFY`, `UNION`, `INTERSECT`, `PRODUCT`, `DIFF`, `ITERATE` |
| Util | `CLEAR`, `RESET`, `PLANE`, `SNAP` |

## The Experiment (for later)

Compare v3.0 (centroid fan) vs v3.1 (face walker):
1. Open v3_0 and v3_1 side by side
2. Run identical sequences
3. Compare: face count, timing, visual quality
4. Log everything via `cmd()` return values
