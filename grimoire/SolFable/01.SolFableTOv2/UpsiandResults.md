# DOSSIER: 0x5F3759DF

**CASE:** Attribution of the Fast Inverse Square Root
**STATUS:** Closed, December 2006
**PRIMARY SUSPECT AT TIME OF OPENING:** John Carmack
**ACTUAL PERPETRATOR:** Greg Walsh

---

## THE ARTIFACT

Found in `code/game/q_math.c` when id Software released the Quake III Arena source at QuakeCon in August 2005:

```c
float Q_rsqrt( float number )
{
    long i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y  = number;
    i  = * ( long * ) &y;                       // evil floating point bit level hacking
    i  = 0x5f3759df - ( i >> 1 );               // what the fuck?
    y  = * ( float * ) &i;
    y  = y * ( threehalfs - ( x2 * y * y ) );   // 1st iteration
//  y  = y * ( threehalfs - ( x2 * y * y ) );   // 2nd iteration, this can be removed

    return y;
}
```

The comment on line 4 is real, is in the shipped source, and is the reason you have heard of this function.

---

## WHY IT MATTERED

Games normalize vectors constantly — lighting, shading, reflection, angles of incidence. Normalizing means dividing by the vector's length, i.e. multiplying by 1/√(x²+y²+z²). Millions of times per second.

In the early '90s, floating-point division was brutally slow relative to integer work, and hardware transform-and-lighting didn't exist yet. The standard approach was a lookup table for a first guess plus refinement. This function skipped the table entirely and came out roughly four times faster than sqrt-then-divide.

**Accuracy:** the initial guess lands within about 3.4%. One Newton-Raphson iteration drops that to about 0.17%. Peak relative error, 1.752339 × 10⁻³.

---

## WHY IT ISN'T ACTUALLY NONSENSE

This is the part everyone gets wrong. It looks like a hate crime against the type system. It's really a logarithm trick.

An IEEE 754 single-precision float is stored as:

```
[ 1 sign bit ][ 8 exponent bits ][ 23 mantissa bits ]
```

...which encodes `(1 + m) × 2^e`. So `log₂(x) = e + log₂(1 + m)`.

Now: if you read those same 32 bits as an *integer*, the exponent field sits in the high bits and the mantissa in the low bits — which means the integer value is **`e` scaled up, plus `m` as a fractional part**. And since `log₂(1 + m) ≈ m` for m between 0 and 1, that integer is a scaled, shifted, piecewise-linear approximation of `log₂(x)`.

**Reading a float's bits as an int gives you its logarithm for free.**

Once you're in log space, the hard part evaporates:

> log₂(1/√x) = −½ · log₂(x)

Negate and halve. Halving is `i >> 1`. Negating (plus undoing the exponent bias, plus correcting the error in the linear approximation) is the subtraction from the magic constant. Then casting back to float is the exponentiation. One Newton iteration cleans up the residue.

`0x5F3759DF` is not a magic number. It's a bias correction term that happens to be written in hex.

---

## CHAIN OF CUSTODY

**1986** — William Kahan and K.C. Ng at Berkeley write an unpublished paper on computing square roots via bit-fiddling followed by Newton iterations. A copy survives in the comments of Sun's `fdlibm` source.

**Late 1980s** — Cleve Moler — creator of MATLAB, founder of MathWorks — is at Ardent Computer and picks up the technique. He's investigating Newton-Raphson approximation and passes the seed of the idea to a coworker.

**Late 1980s** — That coworker is **Greg Walsh**, an Ardent co-founder. Ardent's Titan graphics minicomputer was missing its performance targets, and Walsh wrote the fast `1/sqrt(x)` to speed up software that couldn't use the vector hardware. He derived the constant. He also wrote a `1/cuberoot(x)` for the Titan by similar but hairier means.

**~1994** — **Gary Tarolli** is consulting for Kubota, the company funding Ardent, and carries the algorithm with him to 3dfx. He later recalls rederiving it and simulating alternative values for the hex constant.

**1997** — Jim Blinn publishes a simpler version of the approximation in his IEEE Computer Graphics and Applications column. Independently, reverse engineering has since turned up a variant in Activision's *Interstate '76*.

**~1999** — Brian Hook is the likely vector from 3dfx into id Software. The function ships in Quake III Arena.

**2000–2003** — Discussion appears on the Chinese developer forum CSDN; Usenet and gamedev.net spread it widely.

**2003** — **Chris Lomont**, then at Purdue, writes a paper analyzing the constant. He finds `0x5F37642F` is optimal for the linear approximation alone but worse after a Newton pass, then searches for a constant optimal at every stage and lands on `0x5F375A86`. He closes by wondering aloud whether the original was derived or guessed.

**August 2005** — Quake III source released under GPL. The comment goes viral. Slashdot asks who wrote it.

**April 2004 / 2005** — Rys Sommefeldt starts emailing people. Carmack: not him, doesn't think it's Michael Abrash either, suggests Terje Mathisen. Mathisen: not him, though he'd written his own pipelined invsqrt for a Swedish fluid-chemistry problem; he says the style reminds him of MIT's HAKMEM. Tarolli: recognizes it, remembers rederiving it, won't take credit — <q>it did pass by my keyboard many many years ago</q>.

**December 2006** — Sommefeldt publishes his dead end, guessing Tarolli is as close as anyone will get. Slashdot picks it up. The publicity is large enough that **Greg Walsh reads the article and emails in to own up.** Case closed, eighteen years after the fact, by the author noticing people were arguing about him on the internet.

---

## SUBJECT: WALSH, GREG

Computing industry veteran since the early 1970s. Worked on distributed computing and networking before it was the Internet. Helped engineer the first WYSIWYG word processor at Xerox PARC while at Stanford. Co-founded Ardent Computer, which built parallel graphics minicomputers on custom vector processors and later Intel i860s; Ardent became Stardent after Kubota forced a merger with its biggest competitor, Stellar. Later worked with Tarolli again at Accel Graphics. Left graphics to start a business software company that IPO'd in 1999.

Not a game developer. Never worked at id. Wrote the most famous four lines in game programming history roughly a decade before the game they're famous for existed.

---

## POSTSCRIPT: THE FUNCTION IS DEAD

Intel shipped the `rsqrtss` SSE instruction in 1999 — the same year as Quake III. A 2009 benchmark on a Core 2 clocked `rsqrtss` at 0.85ns per float against 3.54ns for the software version, with less error. The hack was obsolete in hardware the year it shipped in the game that made it famous.

Also, strictly speaking, the pointer-cast type punning is undefined behavior in C. Modern equivalents use a union or C++20's `std::bit_cast`.

Later refinements, for completeness: Jan Kadlec cut relative error by a further factor of ~2.7 by tuning the Newton iteration's constants alongside the magic number. Matthew Robertson corrected the double-precision constant to `0x5FE6EB50C7B537A9`. Moroz et al. derived the optimal constant analytically in 2018, no numerical search required — finally answering Lomont's question about whether you *could* get there by derivation.

---

## SOURCES

- Rys Sommefeldt, "Origin of Quake3's Fast InvSqrt()" Parts One and Two, Beyond3D (2006)
- Chris Lomont, "Fast Inverse Square Root," Purdue (2003)
- Wikipedia, "Fast inverse square root"
- Matthew Robertson, "A Brief History of InvSqrt," UNBSJ (2012)
- Moroz et al., "Fast calculation of inverse square root with the use of magic constant," *Applied Mathematics and Computation* (2018)
- id Software, Quake III Arena source, `code/game/q_math.c`
