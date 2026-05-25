# MNet Logs

Each subfolder = one version. Dump all JSON logs here.

## Structure
`
logs/
  v5.0_sandbox/    ← graph_sandbox_v5.0 NS flow logs
  v5.1_cage/       ← graph_sandbox_v5.1 cage flow logs
  v1.0_sim/        ← mnet_sim.html flight recorder logs
`

## Log format (JSON)
`json
{
  "version": "mnet_sim_1.0",
  "recorded": "ISO timestamp",
  "Re": 100,
  "totalEntries": N,
  "data": [
    {"t": ms, "fn": "P|M|I|P_DONE|M_DONE|I_DONE", "d": {...}}
  ]
}
`

## Entry types
- P  — pressure per node: div, pOld, pNew
- M  — momentum per node: pos, vel, p, gradP, visc, conv, dv, energy
- I  — integrate per node: delta-pos, speed, clamped
- P_DONE / M_DONE / I_DONE — timing per pass
