#!/usr/bin/env node
// WITNESS 5 -- JavaScript. V8's JIT chooses everything.
//
// chi(T) = 20T - 30T + (10T + 2) = 2, for every T.
//
// NOTE, and it matters: JavaScript has NO INTEGER TYPE. Every number here is
// an IEEE-754 binary64. This witness agrees with the others only because all
// intermediate values stay below 2^53 = 9007199254740992, where binary64
// represents every integer exactly. The largest intermediate is 30T; at our
// biggest probe T = 1e6 that is 3e7, comfortably inside.
//
// The wall is at T > 2^53/30 ~ 3.0e14. Past it this witness would drift while
// Rust's i64 and Python's bignum kept going. That is not a bug in this script
// -- it is the float wall (RUSTIUM RULE 0) showing up in the one witness that
// has no choice about it.
const PROBES = [0, 1, 2, 3, 21, 147, 1029, 7203, 50421, 1000000];
const chi = (t) => { const v = 20 * t, e = 30 * t, f = 10 * t + 2; return v - e + f; };
console.log("javascript|" + PROBES.map((t) => `${t}:${chi(t)}`).join("|"));
