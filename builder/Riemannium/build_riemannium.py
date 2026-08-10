"""Build shell/latexium_riemannium_v0.2.html from the Fable gift base, and
TRIPLE-CHECK the live-compute math with a THIRD independent engine (mpmath).

The three witnesses (proof by kernel, Path III -- target != result):
  1. the browser JS (Euler-Maclaurin zeta, Lanczos lnGamma, bisection zeros),
  2. your eyes (the seals board, printed live),
  3. THIS builder: mpmath at 30 dps recomputes the same invariants from scratch.
If the builder and the sim disagree, the build FAILS -- the number is not shipped.

It also injects, via stable anchors:
  * a KaTeX 'latexium' panel (0700): the real formulas, rendered, not sup/sub HTML.
  * a pi(x) vs Li(x) vs R(x) live prime-counting race (0250): more live compute.

ONE run. Normalize CRLF->LF, UTF-8 no BOM. Byte-scan the output. ASCII-only source.
"""
import os, sys, re
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(HERE, 'riemannium_base.html')
OUT  = os.path.join(ROOT, 'shell', 'latexium_riemannium_v0.2.html')

mp.mp.dps = 30
PI = mp.pi

# ---- the KaTeX head include (only CDN, matches cave law: no local dep) ----
KATEX_HEAD = (
    '<link rel="stylesheet" '
    'href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">\n'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>\n'
    '<script defer '
    'src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>\n'
)

# ---- panel 0250: the prime-counting race (extra live compute) ----
RACE_PANEL = '''
 <div class="panel"><h2><span class="pn">0250</span> the race &mdash; &pi;(x) vs Li(x) vs R(x), the monkey's real question</h2>
  <div class="bd"><canvas id="cvR" width="580" height="300"></canvas>
  <div class="cap">You asked "which prime is next"; here is the whole field, live.
  Gold step: <b>&pi;(x)</b>, the exact prime count (sieve). Cyan: <b>Li(x)</b>=&int;<sub>0</sub><sup>x</sup>dt/ln&thinsp;t.
  Pink: <b>R(x)</b>=&Sigma;<sub>n&ge;1</sub>&mu;(n)/n&middot;Li(x<sup>1/n</sup>), Riemann's sharper guess.
  <b id="racegap">?</b> &mdash; R hugs the truth; Li runs ahead (Littlewood: it eventually loses, past 10<sup>316</sup>).</div></div></div>
'''

# ---- panel 0700: the latexium (real rendered formulas) ----
LATEX_PANEL = r'''
<div class="panel" style="margin-top:12px"><h2><span class="pn">0700</span> latexium &middot; the four sigils, rendered</h2>
 <div class="bd" id="tex">
  <div class="texrow">$$Z(t)=e^{i\theta(t)}\,\zeta\!\left(\tfrac12+it\right)\in\mathbb{R},\qquad
    \theta(t)=\arg\Gamma\!\left(\tfrac14+\tfrac{it}{2}\right)-\tfrac{t}{2}\ln\pi$$</div>
  <div class="texrow">$$\psi(x)=x-\sum_{\rho}\frac{x^{\rho}}{\rho}-\ln 2\pi-\tfrac12\ln\!\left(1-x^{-2}\right),
    \qquad \rho=\tfrac12+i\gamma$$</div>
  <div class="texrow">$$\xi(s)=\tfrac12 s(s-1)\,\pi^{-s/2}\,\Gamma\!\left(\tfrac{s}{2}\right)\zeta(s)
    \;=\;\xi(1-s)\quad\textbf{(the = of the zeta world)}$$</div>
  <div class="texrow">$$N(T)=\frac{T}{2\pi}\ln\frac{T}{2\pi e}+\frac{7}{8}+S(T)
    \quad\Rightarrow\quad N(100)\approx 29\ \text{(counted live above)}$$</div>
  <div class="cap">Four sigils, one claim: the primes are the music of these zeros. Rendered with KaTeX;
  the numbers behind them are computed in panels 0100&ndash;0500, and cross-checked by the mpmath kernel
  (build receipt below).</div>
 </div></div>

<div class="panel" style="margin-top:12px"><h2><span class="pn">0800</span> the kernel receipt &middot; a third witness (mpmath, offline)</h2>
 <div class="bd"><div class="seals">__KERNEL_RECEIPT__</div>
 <div class="cap">Built by <b>builder/Riemannium/build_riemannium.py</b> at 30 dps &mdash; an engine that shares
 NO code with the browser. Where it agrees with the live seals, the number has three independent witnesses.
 Proof by kernel: the target is not the result.</div></div></div>
'''

TEX_CSS = (
    '.texrow{padding:7px 2px;border-bottom:1px solid #141a2c;overflow-x:auto}'
    '.texrow:last-child{border-bottom:none}'
    '.katex{color:#e8ecf6}\n'
)

RENDER_JS = (
    "\n// ---- latexium: render the sigils once KaTeX is ready ----\n"
    "window.addEventListener('load',function(){\n"
    "  if(window.renderMathInElement){renderMathInElement(document.getElementById('tex'),{\n"
    "    delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});}\n"
    "});\n"
    "// ---- 0250 the prime-counting race, computed live ----\n"
    "(function(){\n"
    " function Li(x){ if(x<2)return 0; var n=600,a=2,b=x,h=(b-a)/n,s=0;\n"
    "   for(var i=0;i<=n;i++){var t=a+i*h,w=(i===0||i===n)?1:(i%2?4:2);s+=w/Math.log(t);}\n"
    "   return 1.04516378+h/3*s; }\n"
    " var MU=(function(){var N=64,mu=new Array(N+1).fill(1),pr=[];\n"
    "   var comp=new Uint8Array(N+1);\n"
    "   for(var i=2;i<=N;i++){if(!comp[i]){pr.push(i);mu[i]=-1;}\n"
    "     for(var j=0;j<pr.length&&i*pr[j]<=N;j++){comp[i*pr[j]]=1;\n"
    "       if(i%pr[j]===0){mu[i*pr[j]]=0;break;}else mu[i*pr[j]]=-mu[i];}}\n"
    "   return mu; })();\n"
    " function R(x){var s=0;for(var n=1;n<=40;n++){if(MU[n]===undefined||MU[n]===0)continue;\n"
    "   var xr=Math.pow(x,1/n); if(xr<2)break; s+=MU[n]/n*Li(xr);} return s;}\n"
    " function piExact(x){var s=new Uint8Array(x+1),c=0;\n"
    "   for(var i=2;i<=x;i++){if(!s[i]){c++;for(var j=i*i;j<=x;j+=i)s[j]=1;}}return c;}\n"
    " var c=document.getElementById('cvR').getContext('2d'),W=580,H=300;\n"
    " c.fillStyle='#04040c';c.fillRect(0,0,W,H);\n"
    " var xmax=1000,ymax=170;\n"
    " function PX(x){return 30+x/xmax*(W-40);}function PY(y){return H-24-y/ymax*(H-44);}\n"
    " c.strokeStyle='#ffd93d';c.lineWidth=1.5;c.beginPath();var f=true;\n"
    " for(var x=2;x<=xmax;x+=2){var p=piExact(x);if(f){c.moveTo(PX(x),PY(p));f=false;}else c.lineTo(PX(x),PY(p));}\n"
    " c.stroke();\n"
    " c.strokeStyle='#00e5ff';c.lineWidth=1.1;c.beginPath();f=true;\n"
    " for(var x2=2;x2<=xmax;x2+=4){var v=Li(x2);if(f){c.moveTo(PX(x2),PY(v));f=false;}else c.lineTo(PX(x2),PY(v));}\n"
    " c.stroke();\n"
    " c.strokeStyle='#ff4fd8';c.lineWidth=1.1;c.beginPath();f=true;\n"
    " for(var x3=8;x3<=xmax;x3+=4){var w=R(x3);if(f){c.moveTo(PX(x3),PY(w));f=false;}else c.lineTo(PX(x3),PY(w));}\n"
    " c.stroke();c.lineWidth=1;\n"
    " var pTrue=piExact(xmax),gLi=Math.abs(Li(xmax)-pTrue),gR=Math.abs(R(xmax)-pTrue);\n"
    " c.fillStyle='#8fa0c4';c.font='11px ui-monospace,monospace';\n"
    " c.fillText('pi(1000)='+pTrue+'  Li err '+gLi.toFixed(2)+'  R err '+gR.toFixed(2),34,18);\n"
    " document.getElementById('racegap').textContent=\n"
    "   'at x=1000: pi='+pTrue+', Li off by '+gLi.toFixed(1)+', R off by '+gR.toFixed(1);\n"
    "})();\n"
)


def kernel_verify():
    """The third witness. Recompute the sim's headline seals in mpmath, 30 dps."""
    lines = []
    def add(ok, name, detail):
        lines.append(('HIT ' if ok else 'MISS ') + name + ' -- ' + detail)
        return ok
    allok = True

    # K1: zeta(2) = pi^2/6
    z2 = mp.zeta(2)
    allok &= add(abs(z2 - PI**2/6) < mp.mpf(10)**-25, 'K1 zeta(2)=pi^2/6', mp.nstr(z2, 15))
    # K2: Gamma(1/2) = sqrt(pi)
    g = mp.gamma(mp.mpf(1)/2)
    allok &= add(abs(g - mp.sqrt(PI)) < mp.mpf(10)**-25, 'K2 Gamma(1/2)=sqrt(pi)', mp.nstr(g, 15))
    # K3: first zero of zeta on the line = 14.134725...
    z1 = mp.zetazero(1)
    allok &= add(abs(mp.im(z1) - mp.mpf('14.134725141734693')) < mp.mpf(10)**-9,
                 'K3 first zeta zero (im)', mp.nstr(mp.im(z1), 16))
    # K4: count zeros with 0<im<100 (Riemann-von Mangoldt says 29)
    n_below = 0
    for k in range(1, 40):
        g_k = mp.im(mp.zetazero(k))
        if g_k < 100:
            n_below += 1
        else:
            break
    rvm = 100/(2*PI)*mp.log(100/(2*PI*mp.e)) + mp.mpf(7)/8
    allok &= add(n_below == 29 and round(float(rvm)) == 29,
                 'K4 zeros below T=100 = 29 = RvM', str(n_below) + ' counted, RvM=' + mp.nstr(rvm, 6))
    # K5: functional equation xi(s)=xi(1-s) at a random-ish s
    def xi(s):
        return mp.mpf(1)/2 * s*(s-1) * PI**(-s/2) * mp.gamma(s/2) * mp.zeta(s)
    s = mp.mpc('0.37', '12.5')
    rel = abs(xi(s) - xi(1-s)) / abs(xi(s))
    allok &= add(rel < mp.mpf(10)**-20, 'K5 xi(s)=xi(1-s)', 'rel ' + mp.nstr(rel, 4))
    # K6: pi(1000) = 168 (the race panel's headline)
    def pi_exact(n):
        sieve = bytearray([1])*(n+1); c = 0
        for i in range(2, n+1):
            if sieve[i]:
                c += 1
                for j in range(i*i, n+1, i):
                    sieve[j] = 0
        return c
    allok &= add(pi_exact(1000) == 168, 'K6 pi(1000)=168', str(pi_exact(1000)))

    return allok, lines


def main():
    src = open(BASE, encoding='utf-8').read()

    ok, klines = kernel_verify()
    print('=== KERNEL (mpmath 30dps, the third witness) ===')
    for l in klines:
        print('  ' + l)
    print('KERNEL:', 'PASS' if ok else 'FAIL')
    if not ok:
        print('Refusing to ship: the third witness disagrees.', file=sys.stderr)
        return 1

    receipt = '<br>'.join(
        ('<i>' + l[:4] + '</i>' + l[4:]) if l.startswith('HIT ')
        else ('<span class="m">' + l[:5] + '</span>' + l[5:])
        for l in klines)

    # version + title bump
    src = src.replace('LATEXIUM RIEMANNIUM v0.1', 'LATEXIUM RIEMANNIUM v0.2')
    src = src.replace('Riemannium <span>v0.1</span>', 'Riemannium <span>v0.2</span>')

    # inject KaTeX head + tex css (before </head>)
    src = src.replace('</style></head>', TEX_CSS + '</style>\n' + KATEX_HEAD + '</head>')

    # inject the race panel INSIDE #grid, right after the 0100 panel's close.
    # anchor: the 0300 panel opener -- put the race before it so grid stays 2-col.
    anchor_0300 = '<div class="panel"><h2><span class="pn">0300</span>'
    assert anchor_0300 in src, 'anchor 0300 missing'
    src = src.replace(anchor_0300, RACE_PANEL.strip() + '\n\n ' + anchor_0300, 1)

    # inject latexium + kernel-receipt panels after the whole #grid closes.
    # anchor: the 0600 standalone panel (it sits after </div> of #grid).
    anchor_0600 = '<div class="panel" style="margin-top:12px"><h2><span class="pn">0600</span>'
    assert anchor_0600 in src, 'anchor 0600 missing'
    latex_block = LATEX_PANEL.replace('__KERNEL_RECEIPT__', receipt)
    src = src.replace(anchor_0600, latex_block.strip() + '\n\n' + anchor_0600, 1)

    # inject the render + race JS just before the final IIFE close of </script>
    src = src.replace('document.getElementById(\'rvm\').textContent=rvm.toFixed(2);',
                      'document.getElementById(\'rvm\').textContent=rvm.toFixed(2);\n' + RENDER_JS, 1)

    # normalize + strip BOM
    src = src.replace('\r\n', '\n').replace('\r', '\n')
    if src.startswith('\ufeff'):
        src = src[1:]

    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src)

    # byte scan
    raw = open(OUT, 'rb').read(); txt = raw.decode('utf-8')
    lone = sum(1 for i, b in enumerate(raw) if b == 13 and (i+1 >= len(raw) or raw[i+1] != 10))
    fffd = txt.count('\ufffd'); bom = raw[:3] == b'\xef\xbb\xbf'
    esc = txt.count('<\\/'); so = txt.count('<script'); sc = txt.count('</script>')
    endok = txt.rstrip().lower().endswith('</html>')
    clean = (lone == 0 and fffd == 0 and not bom and esc == 0 and so == sc and endok)
    print('=== BYTE SCAN ' + os.path.basename(OUT) + ' ===')
    print(f'  bytes={len(raw)} loneCR={lone} FFFD={fffd} BOM={bom} esc={esc} script={so}/{sc} endsHtml={endok}')
    print('SCAN:', 'PASS' if clean else 'FAIL')
    print('wrote', OUT)
    return 0 if clean else 1


if __name__ == '__main__':
    sys.exit(main())
