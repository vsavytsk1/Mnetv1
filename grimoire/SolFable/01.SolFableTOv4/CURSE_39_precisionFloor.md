## CURSE 39 -- The Float Ceiling (precisionFloor)

WHAT BIT US (EML LUCA SPIRAL v0.2, the golden lane, panel V.c):
  The panel measures how fast the lattice angle converges onto the golden ray. The law is
  exact: the deviation alternates and contracts by `-phi^-2 = -0.381966011`. The panel
  reports `dev / prev_dev` beside that target, live, at whatever n the unwind slider is on.
  At n = 33 it printed:

      dev / prev dev   -0.356643357
      target -phi^-2   -0.381966011

  A 7% miss. The law looked BROKEN. It was not. At n = 33 the deviation itself is
  3.2e-13 degrees -- the numerator and the denominator are each a handful of ulps. The
  ratio of two dusts is dust. We were not measuring the mathematics any more; we were
  measuring the last bits of the mantissa.

  Ran the full ladder headless to see the shape of the rot:

      n    dev (rad)      dev/prev        verdict
      12   -3.5670e-6    -0.381967284     5 good digits
      16   -7.5929e-8    -0.381966041     7 good digits  <- the peak
      20   -1.6162e-9    -0.381966111     7 good digits
      24   -3.4404e-11   -0.381970445     5 good digits
      28   -7.3258e-13   -0.382167265     3 good digits
      32   -1.5876e-14   -0.391780822     1 good digit
      36   -6.6613e-16   -1.090909091     GARBAGE -- off by 3x

  Read that column downward. The accuracy PEAKS at n ~ 16-20 and then DEGRADES. Iterating
  further made the answer worse. Every instinct says "more terms = more accurate"; past the
  floor the instinct is exactly inverted.

THE ROOT PROBLEM:
  Every convergent quantity computed in floating point has a FLOOR, and the floor is not
  where the mathematics stops -- it is where the instrument stops. float64 carries a 53-bit
  mantissa, `eps = 2.220446049250313e-16`, about 15.65 decimal digits. For a quantity of
  scale S, the smallest difference you can honestly resolve is about `eps * S`. Here
  `S = |theta_phi| = 0.388`, so the floor is `8.62e-17` rad. Below it there is no signal.

  Two ways this bites, and the second is the dangerous one:

    1. FALSE FAILURE. A correct law prints a wrong-looking number and you go hunting a bug
       that is not there. Cheap: you waste a day, the code was always right.
    2. FALSE LOCK. The error underflows to exactly 0.0, the HUD prints `err = 0.000000000`
       and lights `LOCKED`, and you publish "converged to machine precision" when what
       actually happened is that you ran out of digits. This is Curse 26 (lockLie) arriving
       through the back door -- not by printing the target as the result, but by the
       instrument manufacturing a perfect result out of nothing.

  A DIFFERENCE amplifies this and a RATIO OF DIFFERENCES amplifies it twice. Catastrophic
  cancellation eats the leading digits of `a - b`; then dividing one cancelled quantity by
  another cancelled quantity divides the surviving noise by more noise. The contraction-rate
  diagnostic -- the standard way to verify a convergence law -- is the single most
  floor-sensitive number you can print.

  The same file got this RIGHT in one lane and WRONG in another, which is the whole lesson:

      k, l, T, V, E, F, P, H   ->  BigInt        exact at any n, no floor
      k/l, theta, dev, ratio   ->  float64       floor at eps*S, rots past it

  The integer lane was chosen deliberately (THEA Pattern A: "do not certify an integer
  invariant with a float tolerance"). The float lane inherited no such guard, and the guard
  is exactly as necessary there.

THE x86 / x64 SEAM (the wider ceiling, for the curious reader):
  - float64: 53-bit mantissa, eps 2.22e-16, ~15.65 digits.
  - float32: 24-bit, eps 1.19e-7, ~7.2 digits. A GPU shader lane is usually THIS. Any
    kernel ported from CPU to a fragment shader loses half its digits silently.
  - x87 80-bit extended: 64-bit mantissa, eps 1.08e-19. The classic x86 trap is that the
    x87 stack computes at 80 bits and rounds to 64 ON STORE -- so the identical expression
    yields different results depending on whether the compiler kept it in a register or
    spilled it to memory. Same source, same machine, two answers.
  - JS `Number` is always float64, but ECMA-262 requires correct rounding ONLY for
    `+ - * /` and `Math.sqrt`. `pow, exp, log, sin, cos, tan, asin, acos, atan, atan2,
    sinh, cbrt, hypot` are implementation-APPROXIMATED. V8, SpiderMonkey and JavaScriptCore
    are each free to differ in the last ulp, and they do.
  - MEASURED, this session: three algebraically identical routes to the same angle,
    one engine, one machine --

        atan(sqrt15 - 2*sqrt3)    0.38813951537018903659
        atan(sqrt3/(2*phi+1))     0.38813951537018870352
        atan2(sqrt3, 2*phi+1)     0.38813951537018870352

    spread 3.33e-16 rad = 3.86 ulp.

  So a "computed live in this browser" page that prints 9+ decimals of a transcendental is
  making a claim about V8, not only about mathematics. A reader on a different engine may
  see different last digits and correctly conclude the page is unreproducible.

HOW WE FOUND IT (proof by kernel):
  Ran the golden lane headless with a stubbed DOM before trusting the render, and printed
  every panel's actual output string. The n = 33 ratio read -0.356643357 against a target of
  -0.381966011. Instead of assuming the law was wrong OR assuming it was fine, computed the
  floor -- `eps * |theta_phi| = 8.62e-17` -- and compared it against the measured deviation
  `3.2e-13 rad`. Ratio ~3700, i.e. roughly 3 significant bits left in the numerator. Verdict:
  the instrument, not the mathematics. Same run also caught the sibling case in panel V.b.

HOW TO FIX:
  - DECLARE THE FLOOR BEFORE THE LOOP, not after the surprise. For a difference at scale S
    in float64 the floor is `eps * S`; write it down as a constant next to the target.
  - SUPPRESS, DO NOT PRINT, below the floor. Not a silent NaN and not a zero -- a sentence:

        dev / prev dev    at the float floor -- not reported
        target -phi^-2    -0.381966011

    The reader learns the instrument ran out, which is a true fact, instead of learning a
    false one. Use a guard an order or two above the raw floor (this shell uses 1e-12 rad
    against a floor of 8.6e-17) so you cut before the digits are visibly rotten, not after.
  - NEVER let `err == 0.0` earn a lock badge on its own. Zero error at the floor and zero
    error from convergence are indistinguishable in the number and opposite in meaning.
    Require `err <= tol` AND `tol > floor` AND K stable frames, and print the floor in the
    HUD so a stranger can check your tolerance is even representable.
  - REPORT ONLY THE DIGITS THE INSTRUMENT RESOLVES. A sweep on a 3000-point grid does not
    know its argmax to 6 decimals; print 3 and say "+/- the grid".
  - IF YOU NEED MORE, CHANGE INSTRUMENT, do not iterate harder. BigInt / Fraction /
    exact rationals / SymPy for the integer and algebraic lanes. Iterating past the floor
    does not buy digits, it spends them (see the table above -- n = 36 is worse than n = 16).
  - REARRANGE TO AVOID THE CANCELLATION when you can. `F_{n+1}/F_n - phi = (-phi^-1)^n / F_n`
    is exact and never cancels; the subtraction form cancels and dies at n ~ 36. The closed
    form is a different instrument for the same quantity, with no floor at all.
  - CROSS-ENGINE CHECK before publishing a 9-decimal transcendental. Compute it two
    algebraically distinct ways in one run and print the spread in ulp. If the spread is
    3.86 ulp, you have 15 honest digits, not 17.

THE RULE:
  Every float number has a ceiling and every convergent process has a floor, and the two are
  the same wall seen from opposite sides. Compute the wall FIRST -- `eps * scale` -- and put
  it in the HUD beside the target. Past the wall, more iterations make the answer WORSE, a
  ratio of differences is noise divided by noise, and an error of exactly zero is the
  instrument lying, not the mathematics arriving. Suppress below the floor and say so.
  Change instrument, do not iterate harder. Know the ceiling before you read the meter.
  Always.

FAMILY:
  Sibling of Curse 26 (lockLie -- there the HUD showed the target as the result; here the
  MACHINE manufactures a perfect result out of exhausted digits, which is worse because
  nobody typed it). Cousin of Curse 24 (staleServe -- you debug a bug that is not there) and
  of Curse 35 (noCeiling -- predict the cost of the next step before allocating; this is the
  same discipline pointed at PRECISION instead of MEMORY). Counter-hex: Path III (target,
  current, err side by side -- and now FLOOR as a fourth column) and Path IV (incomplete is
  fine, fake is not -- "at the float floor" is incomplete and true; "-0.356643357" was
  complete and false).

Curse count: 39. A contraction law printed -0.3566 against a target of -0.3820 and looked
broken; it was not, the deviation had fallen to 3.2e-13 against a float64 floor of 8.6e-17
and the ratio was dust over dust. Accuracy PEAKS mid-run and degrades after -- n=16 gave 7
good digits, n=36 gave none. Compute `eps * scale` before the loop, print it in the HUD,
suppress below it, never let err==0.0 earn a lock, and change instrument rather than iterate
harder. Three algebraically identical routes to one angle differed by 3.86 ulp on one engine.
Know the ceiling before you read the meter. Always.
