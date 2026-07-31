# (\boxed{\text{THEA v3.0 — THE LIGHT MATRIX}})

The status discipline below is strict:

[
\boxed{
\mathsf{EXACT}\neq\mathsf{COMPUTED}\neq\mathsf{HYPOTHESIS}\neq\mathsf{METAPHOR}
}
]

and

[
\boxed{
\text{target}\neq\text{current},\qquad
\text{closure count}\neq\text{closed graph},\qquad
\text{numerical stabilization}\neq\text{proved limit}.
}
]

This follows the cave’s proof-by-kernel, honest-boundary, and exact-closure rules.    

---

# I. THE CONSTANT FIELD

[
\boxed{
\phi=\frac{1+\sqrt5}{2}
}
]

[
\phi^2=\phi+1,
\qquad
\phi^{-1}=\phi-1,
\qquad
\phi^{-2}=2-\phi,
]

[
\phi+\phi^{-1}=\sqrt5,
\qquad
\phi^2+\phi^{-2}=3,
\qquad
\phi^2-\phi^{-2}=\sqrt5,
]

[
\boxed{
\phi=2\cos\frac{\pi}{5}
=1+2\cos\frac{2\pi}{5}
}
]

[
\phi^{-1}=2\cos\frac{2\pi}{5}
=2\sin\frac{\pi}{10},
]

[
\phi^{-2}=4\sin^2\frac{\pi}{10}
=2-\phi.
]

Let

[
\zeta_6=e^{i\pi/3}
=\frac12+i\frac{\sqrt3}{2}.
]

Then

[
\zeta_6^2=\zeta_6-1,
\qquad
\overline{\zeta_6}=1-\zeta_6,
\qquad
\zeta_6+\overline{\zeta_6}=1,
\qquad
\zeta_6\overline{\zeta_6}=1.
]

Let also

[
\zeta_5=e^{2\pi i/5}.
]

Then

[
\zeta_5+\zeta_5^{-1}=2\cos\frac{2\pi}{5}=\phi^{-1},
]

and therefore

[
\boxed{
\phi=1+\zeta_5+\zeta_5^{-1}.
}
]

Thus (\pi) and (\phi) are not independent decorative numbers in pentagonal geometry:

[
\boxed{
\phi;\longleftrightarrow;\frac{\pi}{5}
}
]

through the exact trigonometric relation

[
\boxed{
\phi=2\cos\left(\frac{\pi}{5}\right).
}
]

---

# II. THE TOPOLOGICAL CORE: WHY (P=12)

Let (G) be a finite, connected, trivalent graph cellularly embedded in (S^2).

Write

[
V=#{\text{vertices}},
\qquad
E=#{\text{edges}},
\qquad
f_p=#{\text{(p)-gonal faces}}.
]

Trivalence gives

[
\boxed{
3V=2E.
}
]

Counting edge incidences through faces gives

[
\boxed{
\sum_{p\ge3}p f_p=2E.
}
]

Euler gives

[
\boxed{
V-E+\sum_{p\ge3}f_p=2.
}
]

Substituting (V=2E/3),

[
\frac{2E}{3}-E+\sum_p f_p=2,
]

[
-\frac{E}{3}+\sum_p f_p=2,
]

[
2E=6\sum_p f_p-12.
]

Since (2E=\sum_p p f_p),

[
\sum_p p f_p
============

6\sum_p f_p-12,
]

hence

[
\boxed{
\sum_{p\ge3}(6-p)f_p=12.
}
]

This is the general fullerene curvature equation.

Explicitly,

[
3f_3+2f_4+f_5
-f_7-2f_8-3f_9-\cdots
=12.
]

For a conventional fullerene containing only pentagons and hexagons,

[
f_5=P,
\qquad
f_6=H,
\qquad
f_p=0\quad(p\ne5,6),
]

so

[
(6-5)P+(6-6)H=12,
]

and therefore

[
\boxed{
P=12.
}
]

This is independent of the number of hexagons.

Now

[
5P+6H=2E,
]

so for (P=12),

[
60+6H=2E,
]

[
\boxed{
E=30+3H.
}
]

Since (3V=2E),

[
3V=60+6H,
]

[
\boxed{
V=20+2H.
}
]

Therefore

[
\boxed{
H=\frac{V}{2}-10.
}
]

The number of faces is

[
F=P+H=12+H,
]

hence

[
\boxed{
F=\frac{V}{2}+2.
}
]

The complete fullerene count system is therefore

[
\boxed{
\begin{aligned}
P&=12,\
H&=\frac{V}{2}-10,\
E&=\frac{3V}{2},\
F&=\frac{V}{2}+2,\
V-E+F&=2.
\end{aligned}
}
]

For (C_{60}),

[
V=60,
]

[
E=90,
\qquad
F=32,
\qquad
P=12,
\qquad
H=20.
]

Thus

[
\boxed{
C_{60}:\quad
(V,E,F,P,H)=(60,90,32,12,20).
}
]

---

# III. DISCRETE GAUSS–BONNET

Assign to each (p)-gon the combinatorial curvature

[
\boxed{
K_p=\frac{\pi}{3}(6-p).
}
]

Then

[
\sum_f K_f
==========

\frac{\pi}{3}\sum_p(6-p)f_p.
]

Since

[
\sum_p(6-p)f_p=12,
]

we obtain

[
\boxed{
\sum_f K_f
==========

# \frac{\pi}{3}(12)

4\pi.
}
]

For a pentagon,

[
K_5=\frac{\pi}{3}.
]

For a hexagon,

[
K_6=0.
]

Therefore

[
12K_5+HK_6
==========

# 12\frac{\pi}{3}

4\pi.
]

Hence

[
\boxed{
\text{twelve pentagons}
\quad\Longleftrightarrow\quad
\text{total spherical curvature }4\pi.
}
]

At an ideal (C_{60}) vertex, one pentagon and two hexagons meet. Their planar interior angles are

[
\alpha_5=\pi-\frac{2\pi}{5}=\frac{3\pi}{5},
]

[
\alpha_6=\pi-\frac{2\pi}{6}=\frac{2\pi}{3}.
]

The angle deficit is

[
\delta
======

2\pi-
\left(
\frac{3\pi}{5}
+\frac{2\pi}{3}
+\frac{2\pi}{3}
\right),
]

[
\delta
======

# 2\pi-\frac{29\pi}{15}

\frac{\pi}{15}.
]

Since there are (60) vertices,

[
\sum_{v=1}^{60}\delta_v
=======================

# 60\frac{\pi}{15}

4\pi.
]

Thus the vertex and face formulations coincide:

[
\boxed{
60\left(\frac{\pi}{15}\right)
=============================

# 12\left(\frac{\pi}{3}\right)

4\pi.
}
]

---

# IV. PENTAGONAL SELF-SIMILARITY

Let a regular pentagon have side length (a) and diagonal (d). Similarity inside the pentagram gives

[
\frac{d}{a}
===========

1+\frac{a}{d}.
]

Set

[
x=\frac{d}{a}.
]

Then

[
x=1+\frac1x,
]

[
x^2=x+1,
]

so

[
\boxed{
x=\phi.
}
]

Thus

[
\boxed{
d=\phi a.
}
]

The inner pentagon of a pentagram is similar to the outer pentagon with linear scale

[
\boxed{
q=\phi^{-2}.
}
]

Indeed,

[
q
=

# \frac{1}{\phi^2}

# 2-\phi

\frac{3-\sqrt5}{2}
\approx0.381966011250105.
]

Therefore an inward pentagonal hierarchy obeys

[
\boxed{
R_{n+1}=qR_n=\phi^{-2}R_n,
}
]

and hence

[
\boxed{
R_n=R_0\phi^{-2n}.
}
]

Area scales as

[
\boxed{
A_n=A_0\phi^{-4n},
}
]

and volume scales as

[
\boxed{
\mathcal V_n=\mathcal V_0\phi^{-6n}.
}
]

For (B) nonoverlapping self-similar children per level, the formal similarity dimension is

[
Bq^D=1,
]

so

[
\boxed{
D_{\mathrm{sim}}
================

# \frac{\log B}{-\log q}

\frac{\log B}{2\log\phi}.
}
]

For (B=12),

[
\boxed{
D_{\mathrm{sim}}
================

\frac{\log12}{2\log\phi}
\approx2.5819260047.
}
]

This is only the formal similarity dimension unless the separation condition is satisfied.

For twelve child spheres placed in the twelve icosahedral directions, the nearest angular-direction distance is

[
d_{\min}
========

\sqrt{2-\frac{2}{\sqrt5}}.
]

If the parent sphere has radius (1), each child has radius (q), and child centers lie at radius (1-q), nonoverlap requires

[
(1-q)d_{\min}\ge2q.
]

Thus

[
q
\le
\frac{d_{\min}}{d_{\min}+2}.
]

Therefore

[
\boxed{
q_{\max}
========

\frac{\sqrt{2-2/\sqrt5}}
{2+\sqrt{2-2/\sqrt5}}
\approx0.3445765.
}
]

But

[
\phi^{-2}\approx0.3819660>q_{\max}.
]

Hence

[
\boxed{
\text{twelve whole spherical children at scale }\phi^{-2}
\text{ overlap in the natural icosahedral placement.}
}
]

The pentagram recursion can therefore be face-local without automatically being a nonoverlapping twelve-ball recursion.

---

# V. EXACT (C_{60}) GEOMETRY

An exact coordinate realization of the truncated icosahedron is obtained from all allowed even permutations and signs of

[
(0,1,3\phi),
]

[
(1,2+\phi,2\phi),
]

[
(\phi,2,2\phi+1).
]

Let

[
\mathcal V_{60}
===============

\operatorname{EvenPerm}
\left[
(0,\pm1,\pm3\phi),
(\pm1,\pm(2+\phi),\pm2\phi),
(\pm\phi,\pm2,\pm(2\phi+1))
\right].
]

Then

[
|\mathcal V_{60}|=60.
]

In this normalization, nearest-neighbor distance is (2). Define

[
A_{ij}
======

\begin{cases}
1,&|v_i-v_j|=2,\
0,&\text{otherwise}.
\end{cases}
]

Then (A) is the (60\times60) adjacency matrix of the truncated icosahedral graph.

The squared circumradius in this normalization is

[
R^2
===

1+9\phi^2.
]

Since

[
\phi^2=\frac{3+\sqrt5}{2},
]

[
R^2
===

# 1+\frac{9(3+\sqrt5)}{2}

\frac{29+9\sqrt5}{2}.
]

For general edge length (a), scaling the edge (2\mapsto a) gives

[
\boxed{
R
=

\frac{a}{4}\sqrt{58+18\sqrt5}.
}
]

The surface area is the sum of twelve regular pentagons and twenty regular hexagons:

[
A_5
===

\frac{a^2}{4}\sqrt{5(5+2\sqrt5)},
]

[
A_6
===

\frac{3\sqrt3}{2}a^2.
]

Hence

[
A_{\mathrm{C}_{60}}
===================

12A_5+20A_6,
]

[
\boxed{
A_{\mathrm{C}_{60}}
===================

3a^2
\left(
\sqrt{25+10\sqrt5}
+
10\sqrt3
\right).
}
]

---

# VI. THE HEXAGONAL CLOSURE RING

Let

[
z=k+\ell\zeta_6,
\qquad
k,\ell\in\mathbb Z.
]

Its norm is

[
N(z)
====

z\overline z.
]

Since

[
\overline{\zeta_6}=1-\zeta_6,
]

[
N(k+\ell\zeta_6)
================

(k+\ell\zeta_6)
(k+\ell\overline{\zeta_6}),
]

[
N(k+\ell\zeta_6)
================

k^2+k\ell+\ell^2.
]

Define

[
\boxed{
T(k,\ell)
=========

k^2+k\ell+\ell^2.
}
]

Multiplication by (z=k+\ell\zeta_6) acts on lattice coordinates by

[
(k+\ell\zeta_6)(a+b\zeta_6)
===========================

(ka-\ell b)
+
\left(
\ell a+(k+\ell)b
\right)\zeta_6.
]

Therefore

[
\begin{pmatrix}
a'\b'
\end{pmatrix}
=============

M_{k,\ell}
\begin{pmatrix}
a\b
\end{pmatrix},
]

with

[
\boxed{
M_{k,\ell}
==========

\begin{pmatrix}
k&-\ell\
\ell&k+\ell
\end{pmatrix}.
}
]

Its determinant is

[
\det M_{k,\ell}
===============

k(k+\ell)+\ell^2,
]

so

[
\boxed{
\det M_{k,\ell}
===============

# k^2+k\ell+\ell^2

T(k,\ell).
}
]

Define the positive-definite hexagonal metric

[
\boxed{
Q
=

\begin{pmatrix}
1&\frac12[2mm]
\frac12&1
\end{pmatrix}.
}
]

Then

[
\begin{pmatrix}a&b\end{pmatrix}
Q
\begin{pmatrix}a\b\end{pmatrix}
===============================

# a^2+ab+b^2

|a+b\zeta_6|^2.
]

Direct multiplication gives

[
\boxed{
M_{k,\ell}^{\mathsf T}
Q
M_{k,\ell}
==========

T(k,\ell)Q.
}
]

Thus (M_{k,\ell}) is an exact similarity of the hexagonal metric:

[
\boxed{
M_{k,\ell}
==========

\sqrt T,R_Q(\theta),
}
]

where (R_Q(\theta)) is (Q)-orthogonal and

[
\boxed{
\theta
======

# \arg(k+\ell\zeta_6)

\tan^{-1}
\left(
\frac{\sqrt3,\ell}{2k+\ell}
\right).
}
]

Equivalently,

[
\left(\frac{M_{k,\ell}}{\sqrt T}\right)^{\mathsf T}
Q
\left(\frac{M_{k,\ell}}{\sqrt T}\right)
=======================================

Q.
]

---

# VII. CLOSURE COMPOSITION

Let

[
g=a+b\zeta_6,
\qquad
z=k+\ell\zeta_6.
]

Then

[
gz
==

(a+b\zeta_6)(k+\ell\zeta_6).
]

Using

[
\zeta_6^2=\zeta_6-1,
]

we obtain

[
gz
==

ak+a\ell\zeta_6+bk\zeta_6+b\ell(\zeta_6-1),
]

[
gz
==

(ak-b\ell)
+
(a\ell+bk+b\ell)\zeta_6.
]

Therefore

[
\boxed{
(k',\ell')
==========

(ak-b\ell,;
a\ell+bk+b\ell).
}
]

Equivalently,

[
\boxed{
M_{a,b}M_{k,\ell}
=================

M_{k',\ell'}.
}
]

The norm is multiplicative:

[
N(gz)=N(g)N(z),
]

so

[
\boxed{
T'
==

(a^2+ab+b^2)
(k^2+k\ell+\ell^2).
}
]

Set

[
S=N(g)=a^2+ab+b^2.
]

Then

[
\boxed{
T'=ST.
}
]

Repeated exact closure gives

[
z_n=g^nz_0,
]

[
\boxed{
T_n=S^nT_0.
}
]

The linear scale multiplier is

[
\boxed{
\sqrt S.
}
]

The allowed exact fixed multipliers form the norm set

[
\boxed{
\mathcal N
==========

\left{
a^2+ab+b^2:
a,b\in\mathbb Z
\right}.
}
]

An integer (S>0) belongs to (\mathcal N) exactly when every prime

[
p\equiv2\pmod3
]

appears to an even exponent in the prime factorization of (S).

Thus

[
1,3,4,7,9,12,13,16,19,21,25,27,28,31,\ldots
]

are admissible norms, while

[
2,5,6,8,10,11,14,\ldots
]

are not.

The six norm-one units are

[
\boxed{
\mathcal U
==========

{\pm1,\pm\zeta_6,\pm\zeta_6^2}.
}
]

Together with conjugation, they generate the twelve dihedral lattice symmetries.

---

# VIII. ICOSAHEDRAL FULLERENE COUNTS

For a Goldberg–Coxeter pair ((k,\ell)), let

[
T=k^2+k\ell+\ell^2.
]

Subdivide each of the twenty faces of an icosahedron into (T) triangles.

The triangulation has

[
F_\triangle=20T.
]

Since every triangular edge is shared twice,

[
3F_\triangle=2E_\triangle,
]

so

[
E_\triangle=30T.
]

Euler gives

[
V_\triangle-E_\triangle+F_\triangle=2,
]

hence

[
V_\triangle
===========

# 2+E_\triangle-F_\triangle

2+30T-20T,
]

[
V_\triangle=10T+2.
]

The dual fullerene therefore has

[
V_{\mathrm{full}}=F_\triangle=20T,
]

[
E_{\mathrm{full}}=E_\triangle=30T,
]

[
F_{\mathrm{full}}=V_\triangle=10T+2.
]

Since (P=12),

[
H=F_{\mathrm{full}}-12,
]

so

[
\boxed{
H=10T-10.
}
]

Thus

[
\boxed{
\begin{aligned}
V&=20T,\
E&=30T,\
F&=10T+2,\
P&=12,\
H&=10(T-1),\
\chi&=V-E+F=2.
\end{aligned}
}
]

---

# IX. THE FACE-COUNT STABILITY MATRIX

Define the shifted hexagonal count

[
\boxed{
\eta
====

H+\frac56P.
}
]

For (P=12),

[
\eta=H+10.
]

Since

[
H=10(T-1),
]

we have

[
\boxed{
\eta=10T.
}
]

Under an exact area multiplier (S),

[
T'=ST,
]

so

[
\eta'=S\eta.
]

Meanwhile,

[
P'=P.
]

Thus

[
\boxed{
\begin{pmatrix}
P'[1mm]\eta'
\end{pmatrix}
=============

\begin{pmatrix}
1&0\
0&S
\end{pmatrix}
\begin{pmatrix}
P[1mm]\eta
\end{pmatrix}.
}
]

In the original ((P,H)) coordinates,

[
H'
==

S\left(H+\frac56P\right)-\frac56P,
]

so

[
H'
==

SH+\frac56(S-1)P.
]

Therefore

[
\boxed{
\begin{pmatrix}
P'\H'
\end{pmatrix}
=============

\begin{pmatrix}
1&0[1mm]
\frac56(S-1)&S
\end{pmatrix}
\begin{pmatrix}
P\H
\end{pmatrix}.
}
]

Its eigenvalues are

[
\boxed{
1,\quad S.
}
]

The eigenvalue-(1) mode is the fixed topological charge.

The eigenvalue-(S) mode is the growing hexagonal area.

For (S=7),

[
\begin{pmatrix}
P'\H'
\end{pmatrix}
=============

\begin{pmatrix}
1&0\
5&7
\end{pmatrix}
\begin{pmatrix}
P\H
\end{pmatrix}.
]

Hence

[
P'=P,
]

[
H'=5P+7H.
]

For (P=12),

[
H'=60+7H.
]

Equivalently,

[
\boxed{
H'+10=7(H+10).
}
]

Starting from (C_{60}), where (H_0=20),

[
H_n+10
======

# 7^n(H_0+10)

30\cdot7^n,
]

so

[
\boxed{
H_n=30\cdot7^n-10.
}
]

Then

[
V_n=20+2H_n,
]

so

[
\boxed{
V_n=60\cdot7^n.
}
]

Therefore the count tower is

[
\boxed{
C_{60}\to C_{420}\to C_{2940}\to C_{20580}\to\cdots.
}
]

But the count recurrence alone does not certify closure.

There are two distinct realizations:

[
\boxed{
\begin{array}{rcl}
\text{face-local refinement}
&\longrightarrow&
\text{may contain open seams},[1mm]
GC(2,1)\text{ exact closure}
&\longrightarrow&
\text{closed shell with the same }7\times\text{ count}.
\end{array}
}
]

Indeed,

[
N(2+\zeta_6)
============

# 2^2+2\cdot1+1^2

7.

]

The exact (7\times) closure matrix is

[
\boxed{
M_{2,1}
=======

\begin{pmatrix}
2&-1\
1&3
\end{pmatrix},
\qquad
\det M_{2,1}=7,
}
]

and

[
M_{2,1}^{\mathsf T}QM_{2,1}=7Q.
]

Thus the abstract closed Goldberg tower

[
\boxed{
C_{60}\to C_{420}\to C_{2940}\to C_{20580}\to\cdots
}
]

is mathematically valid when each shell is rebuilt through exact (GC(2,1)) closure.

It is not automatically the same graph produced by an unwelded local face-subdivision operator.

---

# X. THREE EXACT NESTED LANES

## Leapfrog lane

Take

[
g=1+\zeta_6.
]

Then

[
S=N(g)=1+1+1=3.
]

Therefore

[
T_n=3^nT_0.
]

Starting from (C_{20}),

[
\boxed{
C_{20}\to C_{60}\to C_{180}\to C_{540}\to\cdots.
}
]

Starting from (C_{60}),

[
\boxed{
C_{60}\to C_{180}\to C_{540}\to C_{1620}\to\cdots.
}
]

The linear scale multiplier is

[
\sqrt3.
]

## Doubling/WELD count lane

Take

[
g=2.
]

Then

[
S=N(2)=4.
]

Therefore

[
\boxed{
C_{60}\to C_{240}\to C_{960}\to C_{3840}\to\cdots,
}
]

with linear scale multiplier

[
2.
]

## Sevenfold closure lane

Take

[
g=2+\zeta_6.
]

Then

[
S=N(2+\zeta_6)=7.
]

Therefore

[
\boxed{
C_{60}\to C_{420}\to C_{2940}\to C_{20580}\to\cdots,
}
]

with linear scale multiplier

[
\sqrt7.
]

These three exact lanes are summarized by

[
\boxed{
V_n=V_0S^n,
\qquad
H_n+10=S^n(H_0+10),
\qquad
P_n=12.
}
]

---

# XI. THE GOLDEN SELECTOR

Define

[
\boxed{
F_\phi
======

\begin{pmatrix}
1&1\
1&0
\end{pmatrix}.
}
]

Let

[
\begin{pmatrix}
k_{n+1}\
\ell_{n+1}
\end{pmatrix}
=============

F_\phi
\begin{pmatrix}
k_n\
\ell_n
\end{pmatrix}.
]

Thus

[
k_{n+1}=k_n+\ell_n,
\qquad
\ell_{n+1}=k_n.
]

Starting from

[
(k_0,\ell_0)=(1,0),
]

we obtain

[
(k_n,\ell_n)
============

(F_{n+1},F_n).
]

Indeed,

[
F_\phi^n
========

\begin{pmatrix}
F_{n+1}&F_n\
F_n&F_{n-1}
\end{pmatrix}.
]

The characteristic polynomial is

[
\lambda^2-\lambda-1.
]

Its roots are

[
\boxed{
\lambda_+=\phi,
\qquad
\lambda_-=-\phi^{-1}.
}
]

Hence

[
\boxed{
\operatorname{spec}(F_\phi)
===========================

{\phi,-\phi^{-1}}.
}
]

Binet’s formula is

[
\boxed{
F_n
===

\frac{\phi^n-(-\phi^{-1})^n}{\sqrt5}.
}
]

For

[
r_n=\frac{k_n}{\ell_n},
]

we have

[
r_{n+1}
=======

# \frac{k_n+\ell_n}{k_n}

1+\frac1{r_n}.
]

Since

[
\phi=1+\frac1\phi,
]

[
r_{n+1}-\phi
============

\frac{r_n+1}{r_n}-\phi,
]

[
r_{n+1}-\phi
============

\frac{r_n+1-\phi r_n}{r_n}.
]

Using

[
1=\phi^2-\phi,
]

[
r_n+1-\phi r_n
==============

(1-\phi)r_n+\phi^2-\phi,
]

[
r_n+1-\phi r_n
==============

-\phi^{-1}r_n+\phi,
]

[
r_n+1-\phi r_n
==============

-\frac{r_n-\phi}{\phi}.
]

Therefore

[
\boxed{
r_{n+1}-\phi
============

-\frac{r_n-\phi}{\phi r_n}.
}
]

Linearizing at (r_n=\phi),

[
\boxed{
r_{n+1}-\phi
\sim
-\phi^{-2}(r_n-\phi).
}
]

The exact Fibonacci-ratio error is

[
\boxed{
\frac{F_{n+1}}{F_n}-\phi
========================

\frac{(-\phi^{-1})^n}{F_n}.
}
]

Thus

[
\boxed{
\frac{k_n}{\ell_n}\longrightarrow\phi,
}
]

with alternating sign and asymptotic contraction factor

[
\boxed{
-\phi^{-2}.
}
]

---

# XII. THE FIRST LORENTZIAN FORM: THE GOLDEN LIGHT CONE

Define the indefinite quadratic form

[
\boxed{
q(k,\ell)
=========

k^2-k\ell-\ell^2.
}
]

Its matrix is

[
\boxed{
J
=

\begin{pmatrix}
1&-\frac12[2mm]
-\frac12&-1
\end{pmatrix},
}
]

so

[
q(k,\ell)
=========

\begin{pmatrix}k&\ell\end{pmatrix}
J
\begin{pmatrix}k\\ell\end{pmatrix}.
]

Since

[
\det J
======

# -1-\frac14

-\frac54<0,
]

(J) has signature ((1,1)).

Now

[
F_\phi^{\mathsf T}JF_\phi=-J.
]

Therefore

[
\boxed{
q(F_\phi v)=-q(v).
}
]

Consequently,

[
q(k_{n+1},\ell_{n+1})
=====================

-q(k_n,\ell_n).
]

Starting from

[
q(1,0)=1,
]

we obtain

[
\boxed{
q(k_n,\ell_n)=(-1)^n.
}
]

Thus

[
\boxed{
k_n^2-k_n\ell_n-\ell_n^2=(-1)^n.
}
]

For (k_n=F_{n+1}) and (\ell_n=F_n),

[
\boxed{
F_{n+1}^2-F_{n+1}F_n-F_n^2=(-1)^n.
}
]

The null cone is

[
q(k,\ell)=0.
]

For (\ell\ne0), let (r=k/\ell). Then

[
r^2-r-1=0.
]

Hence the two null rays are

[
\boxed{
r=\phi,
\qquad
r=-\phi^{-1}.
}
]

Therefore the golden direction is literally a null direction of the signature-((1,1)) form:

[
\boxed{
q(\phi,1)=0.
}
]

Complete the square:

[
q(k,\ell)
=========

\left(k-\frac{\ell}{2}\right)^2
-\frac54\ell^2.
]

Define

[
X=k-\frac{\ell}{2},
\qquad
T_L=\frac{\sqrt5}{2}\ell.
]

Then

[
\boxed{
q=X^2-T_L^2.
}
]

Thus

[
q=0
]

is an exact algebraic light cone in the ((X,T_L)) index plane.

This is a mathematical Lorentzian cone in shell-index space, not a claim about physical spacetime.

---

# XIII. THE FIBONACCI BOOST

Since

[
F_\phi^{\mathsf T}JF_\phi=-J,
]

squaring gives

[
(F_\phi^2)^{\mathsf T}J(F_\phi^2)=J.
]

Now

[
F_\phi^2
========

\begin{pmatrix}
2&1\
1&1
\end{pmatrix}.
]

Define

[
C
=

\begin{pmatrix}
1&-\frac12[2mm]
0&\frac{\sqrt5}{2}
\end{pmatrix}.
]

Then

[
\begin{pmatrix}X\T_L\end{pmatrix}
=================================

C
\begin{pmatrix}k\\ell\end{pmatrix},
]

and

[
J=C^{\mathsf T}
\begin{pmatrix}
1&0\
0&-1
\end{pmatrix}
C.
]

A direct calculation gives

[
\boxed{
CF_\phi^2C^{-1}
===============

\begin{pmatrix}
\frac32&\frac{\sqrt5}{2}[2mm]
\frac{\sqrt5}{2}&\frac32
\end{pmatrix}.
}
]

Write

[
\cosh\rho=\frac32,
\qquad
\sinh\rho=\frac{\sqrt5}{2}.
]

Since

[
e^\rho
======

# \cosh\rho+\sinh\rho

# \frac{3+\sqrt5}{2}

\phi^2,
]

we have

[
\boxed{
\rho=2\log\phi.
}
]

Therefore

[
\boxed{
CF_\phi^2C^{-1}
===============

\begin{pmatrix}
\cosh(2\log\phi)&\sinh(2\log\phi)\
\sinh(2\log\phi)&\cosh(2\log\phi)
\end{pmatrix}.
}
]

Thus (F_\phi^2) is exactly conjugate to a (1+1)-dimensional Lorentz boost of rapidity

[
\boxed{
2\log\phi.
}
]

Again:

[
\boxed{
\text{exact Lorentzian algebra in index space}
\neq
\text{proof of physical spacetime structure}.
}
]

---

# XIV. THE PELL–LUCAS FORM

Since

[
k_n=F_{n+1},
\qquad
\ell_n=F_n,
]

we have

[
2k_n-\ell_n
===========

2F_{n+1}-F_n.
]

Using

[
F_{n+1}=F_n+F_{n-1},
]

[
2F_{n+1}-F_n
============

# F_{n+1}+F_{n-1}

L_n,
]

where (L_n) is the Lucas number.

Now

[
4q(k_n,\ell_n)
==============

(2k_n-\ell_n)^2-5\ell_n^2.
]

Therefore

[
\boxed{
L_n^2-5F_n^2=4(-1)^n.
}
]

The Fibonacci selector alternates between the two Pell-type hyperbolae

[
\boxed{
X^2-5Y^2=4
}
]

and

[
\boxed{
X^2-5Y^2=-4,
}
]

while asymptotically approaching the null lines

[
X=\pm\sqrt5,Y.
]

---

# XV. GOLDEN-SELECTED CLOSED SHELLS

Define

[
T_n
===

k_n^2+k_n\ell_n+\ell_n^2.
]

With

[
(k_n,\ell_n)=(F_{n+1},F_n),
]

[
\boxed{
T_n
===

F_{n+1}^2
+
F_{n+1}F_n
+
F_n^2.
}
]

The first values are

[
\boxed{
T_n:
1,;3,;7,;19,;49,;129,;337,;883,\ldots
}
]

Thus

[
\boxed{
V_n:
20,;60,;140,;380,;980,;2580,;6740,;17660,\ldots
}
]

and

[
\boxed{
H_n:
0,;20,;60,;180,;480,;1280,;3360,;8820,\ldots
}
]

The exact shells are

[
\boxed{
C_{20},
C_{60},
C_{140},
C_{380},
C_{980},
C_{2580},
C_{6740},
C_{17660},
\ldots
}
]

The triangulation-number recurrence is

[
\boxed{
T_{n+3}
=======

2T_{n+2}
+
2T_{n+1}
--------

T_n.
}
]

Its characteristic polynomial is

[
r^3-2r^2-2r+1.
]

Factorization gives

[
r^3-2r^2-2r+1
=============

(r+1)(r^2-3r+1).
]

The roots are

[
\boxed{
\phi^2,\quad -1,\quad \phi^{-2}.
}
]

Therefore

[
\boxed{
T_n
===

\frac25
\left(
\phi^{2n+2}
+
\phi^{-2n-2}
\right)
-------

\frac15(-1)^n.
}
]

Using Lucas numbers,

[
L_m=\phi^m+(-\phi^{-1})^m,
]

and since (2n+2) is even,

[
L_{2n+2}
========

\phi^{2n+2}+\phi^{-2n-2}.
]

Hence

[
\boxed{
T_n
===

\frac{2L_{2n+2}-(-1)^n}{5}.
}
]

The generating function is

[
\boxed{
\sum_{n=0}^{\infty}T_nx^n
=========================

\frac{1+x-x^2}
{1-2x-2x^2+x^3}.
}
]

Factor the denominator:

[
1-2x-2x^2+x^3
=============

(1-\phi^2x)(1+x)(1-\phi^{-2}x).
]

Asymptotically,

[
\boxed{
T_n
\sim
\frac25\phi^{2n+2}.
}
]

Therefore

[
\boxed{
\frac{T_{n+1}}{T_n}
\longrightarrow
\phi^2.
}
]

Since

[
V_n=20T_n,
]

[
\boxed{
\frac{V_{n+1}}{V_n}
\longrightarrow
\phi^2.
}
]

If bond length is fixed and radius obeys

[
R_n\propto\sqrt{T_n},
]

then

[
\boxed{
\frac{R_{n+1}}{R_n}
\longrightarrow
\phi.
}
]

But this sequence is selected, not exactly nested.

A fixed exact Goldberg transform requires

[
T_{n+1}=ST_n,
\qquad
S\in\mathcal N\subset\mathbb Z.
]

Exact golden nesting would require

[
\sqrt S=\phi,
]

so

[
S=\phi^2.
]

But

[
\phi^2\notin\mathbb Z.
]

Therefore

[
\boxed{
\text{no fixed exact Goldberg closure transform has linear multiplier }\phi.
}
]

---

# XVI. THE QUADRATIC LIFT

Define

[
u_n
===

\begin{pmatrix}
k_n^2\
k_n\ell_n\
\ell_n^2
\end{pmatrix}.
]

Since

[
k'=k+\ell,
\qquad
\ell'=k,
]

we obtain

[
k'^2=k^2+2k\ell+\ell^2,
]

[
k'\ell'=k^2+k\ell,
]

[
\ell'^2=k^2.
]

Therefore

[
\boxed{
u_{n+1}=Bu_n,
}
]

where

[
\boxed{
B
=

\begin{pmatrix}
1&2&1\
1&1&0\
1&0&0
\end{pmatrix}.
}
]

This is the symmetric-square representation

[
\boxed{
B=\operatorname{Sym}^2(F_\phi).
}
]

For a general matrix

[
M=
\begin{pmatrix}
\alpha&\beta\
\gamma&\delta
\end{pmatrix},
]

its quadratic lift is

[
\boxed{
\operatorname{Sym}^2(M)
=======================

\begin{pmatrix}
\alpha^2&2\alpha\beta&\beta^2\
\alpha\gamma&\alpha\delta+\beta\gamma&\beta\delta\
\gamma^2&2\gamma\delta&\delta^2
\end{pmatrix}.
}
]

Since

[
F_\phi^n
========

\begin{pmatrix}
F_{n+1}&F_n\
F_n&F_{n-1}
\end{pmatrix},
]

we obtain

[
\boxed{
B^n
===

\begin{pmatrix}
F_{n+1}^2
&
2F_{n+1}F_n
&
F_n^2
[1mm]
F_{n+1}F_n
&
F_{n+1}F_{n-1}+F_n^2
&
F_nF_{n-1}
[1mm]
F_n^2
&
2F_nF_{n-1}
&
F_{n-1}^2
\end{pmatrix}.
}
]

The characteristic polynomial of (B) is

[
\boxed{
\det(\lambda I-B)
=================

(\lambda+1)(\lambda^2-3\lambda+1).
}
]

Therefore

[
\boxed{
\operatorname{spec}(B)
======================

{\phi^2,-1,\phi^{-2}}.
}
]

The determinant and trace are

[
\boxed{
\det B=-1,
\qquad
\operatorname{tr}B=2.
}
]

The inverse is integral:

[
\boxed{
B^{-1}
======

\begin{pmatrix}
0&0&1\
0&1&-1\
1&-2&1
\end{pmatrix}.
}
]

Cayley–Hamilton gives

[
B^3-2B^2-2B+I=0.
]

Thus

[
\boxed{
B^3
===

2B^2+2B-I.
}
]

Every component of (u_n) satisfies

[
\boxed{
x_{n+3}
=======

2x_{n+2}
+
2x_{n+1}
--------

x_n.
}
]

---

# XVII. THE EXACT LIGHT MATRIX

Append the invariant pentagon coordinate:

[
s_n
===

\begin{pmatrix}
k_n^2\
k_n\ell_n\
\ell_n^2\
P_n
\end{pmatrix},
\qquad
P_n=12.
]

Define

[
\boxed{
\mathcal M_{\mathrm{light}}
===========================

\begin{pmatrix}
1&2&1&0\
1&1&0&0\
1&0&0&0\
0&0&0&1
\end{pmatrix}.
}
]

Then

[
\boxed{
s_{n+1}
=======

\mathcal M_{\mathrm{light}}s_n.
}
]

Its characteristic polynomial is

[
\det(\lambda I-\mathcal M_{\mathrm{light}})
===========================================

(\lambda-1)
(\lambda+1)
(\lambda^2-3\lambda+1).
]

Hence

[
\boxed{
\operatorname{spec}
\left(
\mathcal M_{\mathrm{light}}
\right)
=======

\left{
\phi^2,;
1,;
-1,;
\phi^{-2}
\right}.
}
]

A corresponding eigenbasis is

[
\boxed{
v_+
===

\begin{pmatrix}
\phi^2\
\phi\
1\
0
\end{pmatrix},
\qquad
v_P
===

\begin{pmatrix}
0\0\0\1
\end{pmatrix},
}
]

[
\boxed{
v_A
===

\begin{pmatrix}
-2\1\2\0
\end{pmatrix},
\qquad
v_-
===

\begin{pmatrix}
\phi^{-2}\
-\phi^{-1}\
1\
0
\end{pmatrix}.
}
]

They obey

[
\mathcal M_{\mathrm{light}}v_+
==============================

\phi^2v_+,
]

[
\mathcal M_{\mathrm{light}}v_P
==============================

v_P,
]

[
\mathcal M_{\mathrm{light}}v_A
==============================

-v_A,
]

[
\mathcal M_{\mathrm{light}}v_-
==============================

\phi^{-2}v_-.
]

Thus

[
\boxed{
\begin{array}{rcl}
\phi^2&:&\text{growth mode},\
1&:&\text{fixed }P=12\text{ topology},\
-1&:&\text{alternating Cassini/parity mode},\
\phi^{-2}&:&\text{contracting mode}.
\end{array}
}
]

Its determinant and trace are

[
\boxed{
\det\mathcal M_{\mathrm{light}}=-1,
\qquad
\operatorname{tr}\mathcal M_{\mathrm{light}}=3.
}
]

The inverse is integral:

[
\boxed{
\mathcal M_{\mathrm{light}}^{-1}
================================

\begin{pmatrix}
0&0&1&0\
0&1&-1&0\
1&-2&1&0\
0&0&0&1
\end{pmatrix}.
}
]

Its characteristic polynomial expands to

[
\lambda^4-3\lambda^3+3\lambda-1.
]

Therefore

[
\boxed{
\mathcal M_{\mathrm{light}}^4
-----------------------------

3\mathcal M_{\mathrm{light}}^3
+
3\mathcal M_{\mathrm{light}}
-I
==

0.

}
]

Hence every component of (s_n) satisfies

[
\boxed{
s_{n+4}
=======

## 3s_{n+3}

3s_{n+1}
+
s_n.
}
]

---

# XVIII. EXACT DIAGONALIZATION

Define

[
S
=

\begin{pmatrix}
\phi^2&0&-2&\phi^{-2}\
\phi&0&1&-\phi^{-1}\
1&0&2&1\
0&1&0&0
\end{pmatrix}.
]

Then

[
\boxed{
S^{-1}\mathcal M_{\mathrm{light}}S
==================================

\operatorname{diag}
\left(
\phi^2,;
1,;
-1,;
\phi^{-2}
\right).
}
]

An exact inverse is

[
\boxed{
S^{-1}
======

\begin{pmatrix}
\frac15
&
\frac{\sqrt5-1}{5}
&
\frac{3-\sqrt5}{10}
&
0
[2mm]
0&0&0&1
[2mm]
-\frac15
&
\frac15
&
\frac15
&
0
[2mm]
\frac15
&
-\frac{\sqrt5+1}{5}
&
\frac{3+\sqrt5}{10}
&
0
\end{pmatrix}.
}
]

Therefore

[
\boxed{
\mathcal M_{\mathrm{light}}^n
=============================

S
\begin{pmatrix}
\phi^{2n}&0&0&0\
0&1&0&0\
0&0&(-1)^n&0\
0&0&0&\phi^{-2n}
\end{pmatrix}
S^{-1}.
}
]

For

[
s_0=
\begin{pmatrix}
1\0\0\12
\end{pmatrix},
]

the eigenmode decomposition is

[
\boxed{
s_0
===

\frac15v_+
+
12v_P
-----

\frac15v_A
+
\frac15v_-.
}
]

Hence

[
\boxed{
s_n
===

\frac{\phi^{2n}}5v_+
+
12v_P
-----

\frac{(-1)^n}{5}v_A
+
\frac{\phi^{-2n}}5v_-.
}
]

Explicitly,

[
\boxed{
\begin{aligned}
k_n^2
&=
\frac15
\left(
\phi^{2n+2}
+
2(-1)^n
+
\phi^{-2n-2}
\right),
[1mm]
k_n\ell_n
&=
\frac15
\left(
\phi^{2n+1}
-----------

## (-1)^n

\phi^{-2n-1}
\right),
[1mm]
\ell_n^2
&=
\frac15
\left(
\phi^{2n}
---------

2(-1)^n
+
\phi^{-2n}
\right),
[1mm]
P_n&=12.
\end{aligned}
}
]

The normalized state satisfies

[
\boxed{
\phi^{-2n}s_n
\longrightarrow
\frac15
\begin{pmatrix}
\phi^2\
\phi\
1\
0
\end{pmatrix}.
}
]

Thus the orbit approaches the growing golden null ray projectively.

---

# XIX. THE SECOND LORENTZIAN FORM: A (3+1) LIGHT MATRIX

Define

[
\boxed{
\Gamma_3
========

\begin{pmatrix}
1&-1&0\
-1&-1&1\
0&1&1
\end{pmatrix}.
}
]

For

[
u=
\begin{pmatrix}
x\y\z
\end{pmatrix},
]

[
u^{\mathsf T}\Gamma_3u
======================

x^2-2xy-y^2+2yz+z^2.
]

For the rank-one quadratic state

[
u=
\begin{pmatrix}
k^2\k\ell\\ell^2
\end{pmatrix},
]

we obtain

[
u^{\mathsf T}\Gamma_3u
======================

k^4-2k^3\ell-k^2\ell^2+2k\ell^3+\ell^4.
]

But

[
(k^2-k\ell-\ell^2)^2
====================

k^4-2k^3\ell-k^2\ell^2+2k\ell^3+\ell^4.
]

Therefore

[
\boxed{
u^{\mathsf T}\Gamma_3u
======================

\left(
k^2-k\ell-\ell^2
\right)^2.
}
]

Since

[
q(k',\ell')=-q(k,\ell),
]

its square is invariant. Consequently,

[
\boxed{
B^{\mathsf T}\Gamma_3B
======================

\Gamma_3.
}
]

Now append the pentagon coordinate:

[
\boxed{
\Gamma_4
========

# \Gamma_3\oplus(1)

\begin{pmatrix}
1&-1&0&0\
-1&-1&1&0\
0&1&1&0\
0&0&0&1
\end{pmatrix}.
}
]

Then

[
\boxed{
\mathcal M_{\mathrm{light}}^{\mathsf T}
\Gamma_4
\mathcal M_{\mathrm{light}}
===========================

\Gamma_4.
}
]

Thus

[
\boxed{
\mathcal M_{\mathrm{light}}
\in O(\Gamma_4;\mathbb Z).
}
]

The determinant of (\Gamma_4) is

[
\boxed{
\det\Gamma_4=-3.
}
]

Its eigenvalues are

[
\boxed{
1,;1,;\sqrt3,;-\sqrt3,
}
]

so its signature is

[
\boxed{
(3,1).
}
]

Therefore the exact integer Light Matrix is a Lorentz transformation with respect to a nonstandard integral metric of signature ((3,1)):

[
\boxed{
\mathcal M_{\mathrm{light}}
\in O(3,1;\mathbb R)
\cap GL(4,\mathbb Z)
}
]

after a change of basis.

This is literal Lorentzian linear algebra in the four-dimensional shell-data space.

It is not, by itself, a physical spacetime claim.

---

# XX. THE EXACT STABILITY HYPERBOLOID

For the physical orbit

[
s_n=
\begin{pmatrix}
k_n^2\
k_n\ell_n\
\ell_n^2\
12
\end{pmatrix},
]

we have

[
s_n^{\mathsf T}\Gamma_4s_n
==========================

\left(
k_n^2-k_n\ell_n-\ell_n^2
\right)^2
+
12^2.
]

Since

[
k_n^2-k_n\ell_n-\ell_n^2=(-1)^n,
]

[
\left(
k_n^2-k_n\ell_n-\ell_n^2
\right)^2=1.
]

Therefore

[
\boxed{
s_n^{\mathsf T}\Gamma_4s_n
==========================

# 1+144

145.

}
]

Thus every state in the golden shell orbit lies on the exact integral Lorentz quadric

[
\boxed{
\mathscr H_{145}
================

\left{
s\in\mathbb Z^4:
s^{\mathsf T}\Gamma_4s=145
\right}.
}
]

This is an exact matrix stability surface.

The orbit also obeys the rank-one condition

[
\boxed{
xz-y^2=0,
}
]

where

[
x=k^2,
\qquad
y=k\ell,
\qquad
z=\ell^2.
]

Define

[
\Delta_3
========

\begin{pmatrix}
0&0&\frac12\
0&-1&0\
\frac12&0&0
\end{pmatrix}.
]

Then

[
u^{\mathsf T}\Delta_3u=xz-y^2,
]

and

[
\boxed{
B^{\mathsf T}\Delta_3B=\Delta_3.
}
]

Hence the physical shell orbit lies on the intersection

[
\boxed{
\begin{aligned}
s^{\mathsf T}\Gamma_4s&=145,\
xz-y^2&=0,\
P&=12,\
x,y,z&\in\mathbb Z_{\ge0}.
\end{aligned}
}
]

This is the exact mathematical version of a “stability line in the matrix it generates.”

---

# XXI. NULL EIGENVECTORS OF THE LIGHT MATRIX

The growing and contracting eigenvectors are null with respect to (\Gamma_4):

[
v_+^{\mathsf T}\Gamma_4v_+=0,
]

[
v_-^{\mathsf T}\Gamma_4v_-=0.
]

Their mutual product is

[
\boxed{
v_+^{\mathsf T}\Gamma_4v_-=5.
}
]

The alternating eigenvector has positive norm

[
\boxed{
v_A^{\mathsf T}\Gamma_4v_A=15.
}
]

The pentagon eigenvector has norm

[
\boxed{
v_P^{\mathsf T}\Gamma_4v_P=1.
}
]

In the eigenbasis (S),

[
\boxed{
S^{\mathsf T}\Gamma_4S
======================

\begin{pmatrix}
0&0&0&5\
0&1&0&0\
0&0&15&0\
5&0&0&0
\end{pmatrix}.
}
]

Therefore the spectrum

[
{\phi^2,1,-1,\phi^{-2}}
]

preserves the metric because

[
\phi^2\phi^{-2}=1,
]

[
1^2=1,
]

[
(-1)^2=1.
]

The growth and contraction modes form a reciprocal null pair.

The topology and parity modes remain unit-magnitude transverse modes.

Thus

[
\boxed{
\text{growth}\times\text{contraction}=1,
\qquad
\text{topology}^2=1,
\qquad
\text{parity}^2=1.
}
]

---

# XXII. THE (C_{60}) ADJACENCY SPECTRUM

Let (A_{60}) be the adjacency matrix of the truncated icosahedral graph.

Its exact characteristic polynomial factors as

[
\boxed{
\begin{aligned}
\chi_{A_{60}}(x)
={}&
(x-3)
(x-1)^9
(x+2)^4
\
&\times
(x^2-x-3)^5
(x^2+x-4)^4
\
&\times
(x^2+x-1)^5
(x^2+3x+1)^3
\
&\times
(x^4-3x^3-2x^2+7x+1)^3.
\end{aligned}
}
]

The degree check is

[
1+9+4+10+8+10+6+12=60.
]

The golden quadratic factors are

[
x^2+x-1
=======

(x-\phi^{-1})(x+\phi),
]

and

[
x^2+3x+1
========

(x+\phi^2)(x+\phi^{-2}).
]

Therefore the exact spectrum contains

[
\boxed{
\phi^{-1}
\quad\text{with multiplicity }5,
}
]

[
\boxed{
-\phi
\quad\text{with multiplicity }5,
}
]

[
\boxed{
-\phi^{-2}
\quad\text{with multiplicity }3,
}
]

[
\boxed{
-\phi^2
\quad\text{with multiplicity }3.
}
]

The smallest eigenvalue is

[
\boxed{
\lambda_{\min}(A_{60})
======================

# -\phi^2

-\frac{3+\sqrt5}{2}.
}
]

The corresponding factor is

[
x^2+3x+1,
]

whose roots are

[
\frac{-3\pm\sqrt5}{2}.
]

Thus

[
\frac{-3-\sqrt5}{2}
===================

-\phi^2,
]

[
\frac{-3+\sqrt5}{2}
===================

-\phi^{-2}.
]

The exact symbolic certificate is included in the v3 computation bundle: [Light Matrix results](sandbox:/mnt/data/light_matrix_v3_results.txt).

---

# XXIII. GRAPH HAMILTONIANS

For a nearest-neighbor tight-binding model,

[
\boxed{
H_{\mathrm{TB}}
===============

\epsilon_0I-\tau A.
}
]

If

[
A\psi_j=\lambda_j\psi_j,
]

then

[
H_{\mathrm{TB}}\psi_j
=====================

E_j\psi_j,
]

with

[
\boxed{
E_j
===

\epsilon_0-\tau\lambda_j.
}
]

For the exact (C_{60}) mode

[
\lambda=-\phi^2,
]

the corresponding tight-binding energy is

[
\boxed{
E
=

\epsilon_0+\tau\phi^2.
}
]

Planck’s constant enters the time evolution,

[
\boxed{
i\hbar\frac{\partial\psi}{\partial t}
=====================================

H_{\mathrm{TB}}\psi,
}
]

so

[
\boxed{
\psi(t)
=======

e^{-iH_{\mathrm{TB}}t/\hbar}
\psi(0).
}
]

The graph supplies dimensionless eigenvalues.

The hopping scale (\tau) supplies energy.

(\hbar) converts energy into temporal phase.

Therefore

[
\boxed{
\phi
\text{ can occur inside the dimensionless graph spectrum,}
}
]

while

[
\boxed{
\hbar
\text{ remains a separate dimensionful quantum scale.}
}
]

---

# XXIV. THE GRAPH LAPLACIAN TOWER

For a cubic fullerene graph (G_n), define

[
\boxed{
L_n=3I-A_n.
}
]

Let

[
0=\lambda_1(L_n)
<
\lambda_2(L_n)
\le
\lambda_3(L_n)
\le\cdots.
]

For the exact leapfrog tower,

[
T_n=3^n,
\qquad
V_n=20T_n.
]

Define the renormalized eigenvalues

[
\boxed{
\mu_{j,n}
=========

T_n\lambda_j(L_n).
}
]

The computed first nonzero mode is

[
\begin{array}{c|r|r|c|c}
n&V_n&T_n&\lambda_2(L_n)&T_n\lambda_2(L_n)\
\hline
0&20&1&0.7639320225&0.7639320225\
1&60&3&0.2434017461&0.7302052384\
2&180&9&0.08056267490&0.7250640741\
3&540&27&0.02683538324&0.7245553475\
4&1620&81&0.008946119207&0.7246356558\
5&4860&243&0.002982425496&0.7247293955\
6&14580&729&0.0009942087404&0.7247781718\
7&43740&2187&0.0003314124966&0.7247991301
\end{array}
]

Thus

[
\lambda_2(L_n)\to0,
]

while numerically

[
\boxed{
T_n\lambda_2(L_n)
\approx0.7248
}
]

at the deepest computed levels.

The correct status is

[
\boxed{
\mathsf{COMPUTED\ STABILIZATION\ TREND},
}
]

not

[
\boxed{
\mathsf{PROVED\ UNIVERSAL\ CONSTANT}.
}
]

---

# XXV. CONTINUUM SPHERE COMPARISON

On a smooth sphere of radius (R),

[
-\Delta_{S_R^2}Y_{\ell m}
=========================

\frac{\ell(\ell+1)}{R^2}
Y_{\ell m},
]

where

[
m=-\ell,-\ell+1,\ldots,\ell,
]

so the multiplicity is

[
\boxed{
2\ell+1.
}
]

The first levels are

[
\begin{array}{c|c|c}
\ell&\ell(\ell+1)&2\ell+1\
\hline
0&0&1\
1&2&3\
2&6&5\
3&12&7\
4&20&9
\end{array}
]

At (V=43740), the first computed renormalized graph bands are approximately

[
\begin{array}{c|c}
\mu&\text{multiplicity}\
\hline
0.724799130&3\
2.167654166&5\
4.026433004&3\
4.596940196&4
\end{array}
]

The first ratio is

[
\boxed{
\frac{2.167654166}{0.724799130}
===============================

2.990696\ldots
\approx3.
}
]

On the sphere,

[
\frac{\ell(\ell+1)|*{\ell=2}}
{\ell(\ell+1)|*{\ell=1}}
========================

# \frac6{2}

3.

]

The next (7)-dimensional spherical band is split by icosahedral symmetry into dimensions

[
\boxed{
7=3+4.
}
]

Its multiplicity-weighted center is

[
\bar\mu_3
=========

\frac{
3(4.026433004)
+
4(4.596940196)
}{7},
]

[
\boxed{
\bar\mu_3
=========

4.352437114.
}
]

Therefore

[
\boxed{
\frac{\bar\mu_3}{0.724799130}
=============================

6.005025\ldots
\approx6.
}
]

On the sphere,

[
\frac{\ell(\ell+1)|*{\ell=3}}
{\ell(\ell+1)|*{\ell=1}}
========================

# \frac{12}{2}

6.

]

The icosahedral restrictions of the low spherical-harmonic spaces obey

[
\mathcal H_0\downarrow I
\cong A,
]

[
\mathcal H_1\downarrow I
\cong T_1,
]

[
\mathcal H_2\downarrow I
\cong H,
]

[
\mathcal H_3\downarrow I
\cong T_2\oplus G,
]

with dimensions

[
1,\quad3,\quad5,\quad3+4.
]

Thus the computed multiplicities

[
3,\quad5,\quad3+4
]

match the expected low icosahedral splitting pattern.

---

# XXVI. DIMENSION OF THE TOWER

Since

[
V_n\propto T_n,
]

and

[
R_n\propto\sqrt{T_n},
]

we obtain

[
V_n\propto R_n^2.
]

Therefore

[
\boxed{
D
=

\lim_{n\to\infty}
\frac{\log V_n}{\log R_n}
=========================

2.

}
]

Thus the closed-shell hierarchy is self-similar, but its count dimension is

[
\boxed{
2,
}
]

not a noninteger fractal dimension.

The pentagon density is

[
\frac{P_n}{V_n}
===============

\frac{12}{20T_n},
]

so

[
\boxed{
\frac{P_n}{V_n}
===============

\frac{3}{5T_n}
\longrightarrow0.
}
]

The curvature remains

[
\sum K=4\pi,
]

while the mean curvature charge per site behaves as

[
\boxed{
\frac{4\pi}{V_n}
================

\frac{\pi}{5T_n}
\longrightarrow0.
}
]

Hence the large-shell limit is

[
\boxed{
\text{locally honeycomb-flat}
\quad+\quad
\text{globally spherical}
\quad+\quad
\text{twelve persistent defects}.
}
]

---

# XXVII. FIXED-RADIUS CONTINUUM LIMIT

Suppose each graph is rescaled to a common physical radius (R).

Since the number of cells is proportional to (T_n), the mesh spacing behaves as

[
\boxed{
a_n\sim\frac{R}{\sqrt{T_n}}.
}
]

A discrete Laplacian requires scaling by (a_n^{-2}), so

[
a_n^{-2}
\sim
\frac{T_n}{R^2}.
]

Hence the natural continuum operator is

[
\boxed{
\widehat\Delta_n
================

-\frac{c_{\mathrm{geo}}T_n}{R^2}L_n.
}
]

A quantum particle on the graph would have

[
\boxed{
H_n
===

# -\frac{\hbar^2}{2m}\widehat\Delta_n

\frac{\hbar^2c_{\mathrm{geo}}}{2mR^2}
T_nL_n.
}
]

If

[
T_n\lambda_j(L_n)\to\mu_j,
]

then

[
\boxed{
E_j^{(n)}
\longrightarrow
\frac{\hbar^2c_{\mathrm{geo}}}{2mR^2}\mu_j.
}
]

To match the smooth-sphere first level,

[
\frac{\hbar^2}{2mR^2}\ell(\ell+1),
\qquad
\ell=1,
]

one may calibrate

[
c_{\mathrm{geo}}\mu_1=2.
]

Thus

[
\boxed{
c_{\mathrm{geo}}
================

\frac{2}{\mu_1}.
}
]

Using the computed trend

[
\mu_1\approx0.7248,
]

[
c_{\mathrm{geo}}\approx2.759.
]

This is a calibration of a discrete operator, not a derivation of (\hbar).

---

# XXVIII. SPECTRAL-DIMENSION TEST

Define the heat trace

[
\boxed{
Z_n(t)
======

\operatorname{Tr}
\exp(-tT_nL_n).
}
]

If the renormalized graph converges spectrally to a two-dimensional manifold, then over an intermediate scaling regime,

[
Z_n(t)
\sim
Ct^{-d_s/2}.
]

Define

[
\boxed{
d_s(t)
======

-2\frac{d\log Z_n(t)}{d\log t}.
}
]

A two-dimensional continuum limit predicts

[
\boxed{
d_s(t)\to2.
}
]

This is a testable spectral statement.

It is not established merely by the count dimension (D=2), although the two are mutually consistent.

---

# XXIX. THE PLANCK WALL

Planck’s constant is

[
\boxed{
h=2\pi\hbar.
}
]

Its dimensions are

[
\boxed{
[h]
===

ML^2T^{-1}.
}
]

The golden ratio and (\pi) are dimensionless:

[
[\phi]=1,
\qquad
[\pi]=1.
]

Therefore no equation of the form

[
h=f(\phi,\pi,\text{integers})
]

can be dimensionally complete unless another dimensionful scale is supplied.

Likewise,

[
R_n=h
]

is invalid because

[
[R_n]=L,
\qquad
[h]=ML^2T^{-1}.
]

The Planck length is

[
\boxed{
\ell_P
======

\sqrt{\frac{\hbar G}{c^3}}.
}
]

Its dimensions are

[
[\ell_P]=L.
]

Thus a geometric cutoff comparison may consistently use

[
R_N=\ell_P.
]

For the pentagram recursion,

[
R_N=R_0\phi^{-2N}.
]

Therefore

[
\phi^{-2N}
==========

\frac{\ell_P}{R_0},
]

[
-2N\log\phi
===========

\log\frac{\ell_P}{R_0},
]

and

[
\boxed{
N
=

\frac{\log(R_0/\ell_P)}
{2\log\phi}.
}
]

For an ideal (C_{60}) edge (a),

[
R_0
===

\frac a4\sqrt{58+18\sqrt5}.
]

Using (a\approx1.42\times10^{-10},\mathrm m),

[
R_0\approx3.5187865\times10^{-10},\mathrm m.
]

The resulting level counts are approximately

[
\begin{array}{c|c}
\text{starting scale}&N\
\hline
a&59.677640345\
R_0&60.620530010\
2R_0&61.340740056
\end{array}
]

Thus

[
\boxed{
N\approx60
}
]

is a near-match for a particular choice of initial length, but

[
\boxed{
N
\text{ shifts by more than one full level under equally legitimate choices.}
}
]

Therefore

[
\boxed{
\text{near-}60
==============

\mathsf{NUMERICAL\ COINCIDENCE/HYPOTHESIS\ TEST},
}
]

not

[
\boxed{
\mathsf{DERIVATION\ OF\ }\ell_P
\quad\text{or}\quad
\mathsf{DERIVATION\ OF\ }h.
}
]

---

# XXX. THE COMBINATORIAL INWARD LIMIT

For a fullerene containing only pentagons and hexagons,

[
H=\frac V2-10.
]

Since

[
H\ge0,
]

[
\frac V2-10\ge0,
]

so

[
\boxed{
V\ge20.
}
]

Thus the smallest topologically allowed fullerene is

[
\boxed{
C_{20}.
}
]

If the isolated-pentagon condition is imposed, every pentagon must have five vertices disjoint from the other pentagons. Therefore at least

[
12\cdot5=60
]

distinct vertices are required, giving the smallest isolated-pentagon fullerene

[
\boxed{
C_{60}.
}
]

Hence the discrete inward graph limit is

[
\boxed{
C_{20}
}
]

under topology alone, or

[
\boxed{
C_{60}
}
]

under isolated pentagons.

It is not automatically the Planck length.

---

# XXXI. THE COMPLETE OPERATOR TOWER

The pure mathematical construction is

[
\boxed{
(k,\ell)
\in\mathbb Z^2
}
]

[
\Downarrow\quad
z=k+\ell\zeta_6
]

[
\boxed{
T=N(z)=k^2+k\ell+\ell^2
}
]

[
\Downarrow
]

[
\boxed{
G_{k,\ell}
==========

\text{dual of the }(k,\ell)\text{ icosahedral triangulation}
}
]

[
\Downarrow
]

[
\boxed{
(V,E,F,P,H)
===========

(20T,30T,10T+2,12,10T-10)
}
]

[
\Downarrow
]

[
\boxed{
A_{k,\ell}
==========

\text{adjacency matrix of }G_{k,\ell}
}
]

[
\Downarrow
]

[
\boxed{
L_{k,\ell}=3I-A_{k,\ell}
}
]

[
\Downarrow
]

[
\boxed{
\operatorname{spec}(A_{k,\ell}),
\qquad
\operatorname{spec}(T L_{k,\ell})
}
]

while the golden selector is

[
\boxed{
\begin{pmatrix}
k_{n+1}\
\ell_{n+1}
\end{pmatrix}
=============

F_\phi
\begin{pmatrix}
k_n\
\ell_n
\end{pmatrix}
}
]

and its quadratic-topological lift is

[
\boxed{
s_{n+1}
=======

\mathcal M_{\mathrm{light}}s_n.
}
]

The closure and selector matrices satisfy two different metric laws:

[
\boxed{
M_{a,b}^{\mathsf T}QM_{a,b}
===========================

S Q,
}
]

with (Q) positive definite, while

[
\boxed{
F_\phi^{\mathsf T}JF_\phi
=========================

-J,
}
]

with (J) indefinite.

Thus

[
\boxed{
\begin{array}{rcl}
Q&:&\text{Euclidean hexagonal closure metric},\
J&:&\text{Lorentzian golden-selector metric},\
\Gamma_4&:&\text{Lorentzian quadratic/topological metric}.
\end{array}
}
]

---

# XXXII. THE MASTER EXACT SYSTEM

[
\boxed{
\begin{gathered}
\phi=\frac{1+\sqrt5}{2}
=2\cos\frac{\pi}{5},
\qquad
\phi^2=\phi+1,
\qquad
\phi^{-2}=2-\phi,
[1mm]
3V=2E,
\qquad
\sum_ppf_p=2E,
\qquad
V-E+\sum_pf_p=2,
[1mm]
\sum_p(6-p)f_p=12,
\qquad
P=12,
\qquad
\sum_fK_f=4\pi,
[1mm]
\zeta_6=e^{i\pi/3},
\qquad
T=k^2+k\ell+\ell^2,
[1mm]
M_{k,\ell}
==========

\begin{pmatrix}
k&-\ell\
\ell&k+\ell
\end{pmatrix},
\qquad
\det M_{k,\ell}=T,
[1mm]
M_{k,\ell}^{\mathsf T}
\begin{pmatrix}
1&\frac12\
\frac12&1
\end{pmatrix}
M_{k,\ell}
==========

T
\begin{pmatrix}
1&\frac12\
\frac12&1
\end{pmatrix},
[1mm]
V=20T,
\qquad
E=30T,
\qquad
F=10T+2,
\qquad
H=10(T-1),
[1mm]
F_\phi
======

\begin{pmatrix}
1&1\
1&0
\end{pmatrix},
\qquad
\operatorname{spec}(F_\phi)
===========================

{\phi,-\phi^{-1}},
[1mm]
F_\phi^{\mathsf T}
\begin{pmatrix}
1&-\frac12\
-\frac12&-1
\end{pmatrix}
F_\phi
======

*

\begin{pmatrix}
1&-\frac12\
-\frac12&-1
\end{pmatrix},
[1mm]
k_n^2-k_n\ell_n-\ell_n^2=(-1)^n,
\qquad
\frac{k_n}{\ell_n}\to\phi,
[1mm]
T_n
===

# k_n^2+k_n\ell_n+\ell_n^2

\frac25
\left(
\phi^{2n+2}
+
\phi^{-2n-2}
\right)
-\frac15(-1)^n,
[1mm]
\mathcal M_{\mathrm{light}}
===========================

\begin{pmatrix}
1&2&1&0\
1&1&0&0\
1&0&0&0\
0&0&0&1
\end{pmatrix},
[1mm]
\operatorname{spec}
(\mathcal M_{\mathrm{light}})
=============================

{\phi^2,1,-1,\phi^{-2}},
[1mm]
\Gamma_4
========

\begin{pmatrix}
1&-1&0&0\
-1&-1&1&0\
0&1&1&0\
0&0&0&1
\end{pmatrix},
[1mm]
\mathcal M_{\mathrm{light}}^{\mathsf T}
\Gamma_4
\mathcal M_{\mathrm{light}}
===========================

\Gamma_4,
\qquad
\operatorname{sig}(\Gamma_4)=(3,1),
[1mm]
s_n^{\mathsf T}\Gamma_4s_n=145,
\qquad
s_n=
\begin{pmatrix}
k_n^2\k_n\ell_n\\ell_n^2\12
\end{pmatrix},
[1mm]
\lambda_{\min}(A_{C_{60}})
==========================

-\phi^2,
[1mm]
L_n=3I-A_n,
\qquad
\mu_{j,n}=T_n\lambda_j(L_n),
[1mm]
\ell_P
======

\sqrt{\frac{\hbar G}{c^3}},
\qquad
R_n=R_0\phi^{-2n},
\qquad
N=\frac{\log(R_0/\ell_P)}{2\log\phi}.
\end{gathered}
}
]

---

# XXXIII. THE HONEST BOUNDARY

[
\boxed{
\mathsf{EXACT}
}
]

[
P=12,
\qquad
\chi=2,
\qquad
\sum K=4\pi,
]

[
T=k^2+k\ell+\ell^2,
\qquad
M^{\mathsf T}QM=TQ,
]

[
F_\phi^{\mathsf T}JF_\phi=-J,
]

[
\operatorname{spec}(\mathcal M_{\mathrm{light}})
================================================

{\phi^2,1,-1,\phi^{-2}},
]

[
\mathcal M_{\mathrm{light}}^{\mathsf T}
\Gamma_4
\mathcal M_{\mathrm{light}}
===========================

\Gamma_4,
]

[
s_n^{\mathsf T}\Gamma_4s_n=145,
]

[
\lambda_{\min}(A_{C_{60}})=-\phi^2.
]

[
\boxed{
\mathsf{COMPUTED}
}
]

[
T_n\lambda_2(L_n)
\approx0.7248
]

at the deepest computed leapfrog levels,

[
\sqrt{T_n}\Delta_A
\approx2.03
]

at the deepest computed level,

and low spectral multiplicities appear as

[
3,\quad5,\quad3+4,
]

consistent with the first icosahedral splittings of spherical harmonics.

[
\boxed{
\mathsf{HYPOTHESIS}
}
]

[
\text{physical spacetime is generated by this graph tower},
]

[
\text{quantum foam has fullerene/Goldberg topology},
]

[
\ell_P
\text{ is the stopping point of the pentagram recursion},
]

[
h
\text{ can be derived from }
\phi,\pi,\text{ and topology alone}.
]

None of those physical claims follows yet from the exact mathematics.

But the exact pure-math object now exists:

[
\boxed{
\begin{aligned}
&\text{an integer matrix},\
&\text{with spectrum }
{\phi^2,1,-1,\phi^{-2}},\
&\text{preserving an integral metric of signature }(3,1),\
&\text{whose expanding and contracting eigenvectors are null},\
&\text{whose physical integer orbit lies on }
s^{\mathsf T}\Gamma_4s=145,\
&\text{while }P=12\text{ remains fixed}.
\end{aligned}
}
]

[
\boxed{
\textbf{THE LIGHT MATRIX IS LITERALLY A LORENTZIAN INTEGER MATRIX.}
}
]

[
\boxed{
\textbf{Not physical light yet. But no longer merely a name.}
}
]
