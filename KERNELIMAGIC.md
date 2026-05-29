# KERNELIC MAGIC — Black Magic Good Practices
## Read this BEFORE touching the builder. If you fail twice — re-read the whole file.

---

## RULE 0 — THE PRIME RULE

> The builder generates HTML that contains JavaScript.
> Python f-strings + JavaScript = black magic.
> Respect it or it will destroy you.

---

## THE 4 CURSES (what kills us every time)

### CURSE 1 — The Curly Brace Curse
JavaScript uses `{}` everywhere. Python f-strings use `{}` for interpolation.

```python
# KILLS YOU:
html = f"var x = {{}}"          # becomes var x = {}  ← OK
html = f"var obj = {{Re:150}}"  # becomes var obj = {Re:150}  ← OK
html = f"try {{ }} catch(e){{}}" # nested = CHAOS

# THE FIX: if JS gets complex → use .format() or string concat, NOT f-string
# OR: keep ALL JS in a separate variable built with regular strings, then inject
```

### CURSE 2 — The Unicode/CRLF Curse
Windows git CRLF conversion + unicode chars in Python strings = corrupted bytes.

```python
# KILLS YOU:
# Using · ✓ ✗ λ̃ χ ← → ⬡ directly inside f-strings on Windows
# Git converts LF→CRLF, byte 0xB7 (·) becomes invalid UTF-8 sequence

# THE FIX: Use ASCII-only in builder .py files
# Instead of · use  .   or  *
# Instead of ✓ use  OK  or  PASS
# Instead of ✗ use  X   or  FAIL
# Instead of λ̃ use  lam  or  lambda1
# Unicode is fine INSIDE the generated HTML (the output) — just not in the .py source
```

### CURSE 3 — The Multi-Edit Corruption Curse
The multi_edit tool finds strings by exact match including whitespace.
If the file has CRLF corruption — the string won't match. Ever.

```
# KILLS YOU:
# Trying to multi_edit a file that has unicode corruption
# The old_string will never match → all edits fail → file untouched
# Then you try again → same failure → 2 attempts wasted

# THE FIX: If multi_edit fails twice on same file → REWRITE THE FILE CLEAN
# Use create_new_file to replace it entirely
# Never patch a corrupted file — delete and recreate
```

### CURSE 4 — The f-string Nesting Curse
f-strings cannot contain `\` in expressions. Nested quotes cause SyntaxError.

```python
# KILLS YOU:
html = f"""
  el.innerHTML = rows.map(function(r){{
    return '<div class=\"dp-row\">' + r[0] + '</div>';  # ← \n in f-string = DEATH
  }}).join('');
"""

# THE FIX: Build JS glue as regular string, then concat
JS_GLUE = '''
  el.innerHTML = rows.map(function(r) {
    return '<div class="dp-row">' + r[0] + '</div>';
  }).join('');
'''
html = SHELL + "<script>" + JS_GLUE + "</script>" + CLOSE
```

---

## THE 3 SAFE PATTERNS

### PATTERN 1 — Template + Inject (safest)
```python
# Read an existing HTML file as template
# Find the seam (e.g. </script> before </body>)
# Inject new <script> blocks AFTER all existing scripts
# Never modify the template's existing JS

src = TEMPLATE.read_text(encoding="utf-8")
inject = "<script>\n" + M2 + "\n" + M3 + "\n" + GLUE_JS + "\n</script>"
out = src.replace("</body></html>", inject + "\n</body></html>")
```

### PATTERN 2 — Separate Variables (for complex JS)
```python
# Build CSS, HTML shell, and JS SEPARATELY as plain strings
# Only use f-string for simple version/timestamp substitutions at the END

CSS = """..."""           # plain string, no f
HTML_SHELL = """..."""    # plain string, no f
JS_MODULES = M1 + M2     # plain concat
JS_GLUE = """..."""       # plain string, no f — ASCII ONLY

# Only ONE f-string at the very end to stamp version/date:
final = f"""<!DOCTYPE html>
<title>ENG {VERSION}</title>
<style>{CSS}</style>
{HTML_SHELL}
<script>{JS_MODULES}</script>
<script>{JS_GLUE}</script>
</body></html>"""
```

### PATTERN 3 — Write with explicit encoding (always)
```python
# ALWAYS write with utf-8 and no BOM
OUT.write_text(html, encoding="utf-8")

# NEVER use open(OUT, 'w') without encoding= 
# Windows default encoding (cp1252) will destroy unicode in output
```

---

## THE RECOVERY PROTOCOL

When the builder breaks:

```
1. STOP — do not patch, do not multi_edit a second time
2. READ this file
3. Identify which CURSE hit you (usually Curse 1 or 2)
4. CREATE NEW FILE — clean rewrite, ASCII-only, Pattern 2
5. Run it — verify output
6. ONLY THEN commit
```

---

## WHAT IS SAFE TO PUT IN AN f-STRING

```python
# SAFE — simple substitutions only:
f"<title>ENG {VERSION}</title>"
f"// Built: {TIMESTAMP}"
f"console.log('ENG {VERSION} loaded');"
f"git:{GIT}"

# NOT SAFE:
f"var x = {{}}"              # OK actually — but avoid nesting
f"function fn(){{ {JS} }}"   # JS variable inside f-string braces = CHAOS
f"color:#{hex_color}"        # # is fine but be careful
f"'\u00b7'"                  # unicode escape in f-string on Windows = CRLF death
```

---

## THE KERNEL MODULE INJECT ORDER (never change this)

```
M1  goldberg_kernel.js   → GK       (always first — everything depends on it)
M2  graph_axioms.js      → GA       (depends on GK)
M3  sar_modular.js       → SAR      (depends on GK)
M4  ns_spectral.js       → NSS      (depends on GK)
M5  fractal_search.js    → FS       (depends on GK + SAR)
M6  mnet_nanite.js       → MNetNanite (depends on GK)
M7  math_tree            → (standalone, inject last, wrap in try/catch)
GLUE                     → always LAST, after all modules
```

---

## THE DATA PANEL PATTERN (for eng dashboard)

When adding live data panels from modules, do it in JS only — no Python generation:

```javascript
// In GLUE JS (plain string, not f-string):
var PC = {cyan:"#00d4ff", green:"#00ffd5", pink:"#ff69b4",
          gold:"#ffd700", orange:"#ff9040", dim:"#1a2a3a"};

function setPanel(id, rows) {
  var el = document.getElementById('dp-' + id);
  if (!el) return;
  el.innerHTML = rows.map(function(r) {
    return '<div class="dp-row"><span class="dp-k">' + r[0] +
           '</span><span class="dp-v" style="color:' +
           (PC[r[2]] || '#aaa') + '">' + r[1] + '</span></div>';
  }).join('');
}

window.addEventListener('load', function() {
  // GK
  var gk = GK.buildC60();
  var inv = GK.invariants(gk);
  setPanel('gk', [
    ['V', inv.vertices, 'cyan'],
    ['P', inv.pents, 'pink'],
    ['chi', inv.vertices - inv.edges + inv.faces, 'gold']
  ]);
  // ... same for SAR, NSS, FS, NAN
});
```

HTML side — just empty divs:
```html
<div id="dp-gk" class="data-panel"></div>
<div id="dp-sar" class="data-panel"></div>
```

---

## CURSE 5 — The File Too Long Curse
Builder scripts get long. create_new_file times out on large files.

```
FIX: 
  1. create_new_file with empty content first
  2. Output the file content in chunks as code blocks in chat
  3. Vlad pastes each chunk into the file manually
  4. Run + verify
  Never write >200 lines in one create_new_file call
```

---

## CURSE 6 -- The File:// Curse
We build locally. We open with file://. We see it differently than the world.
GitHub Pages serves the REAL version. file:// is a lie.

```
FIX:
  NEVER open with file:// to verify a build.
  ALWAYS open the live GitHub Pages URL:
  https://vsavytsk1.github.io/Mnetv1/shell/FILENAME.html

  In every builder script the open command must be:
  Start-Process brave "https://vsavytsk1.github.io/Mnetv1/..."
  NOT:
  Start-Process brave "file:///C:/Users/..."

  The math_tree works because we opened its URL.
  VALE exists at its URL. We just never looked.
```

---

## THE DASHBOARD DEVELOPMENT RULE
When building a new dashboard visual or theme -- TWO TABS always:

```
TAB 1 -- current FULL working dashboard (ENG v2.0 or latest)
         https://vsavytsk1.github.io/Mnetv1/shell/eng_v2.0.html
         This is the reference. Always alive. Always clickable.
         You can summon any module from here while you work.

TAB 2 -- the visual you are actively building
         https://vsavytsk1.github.io/Mnetv1/shell/vale_v1.1.html
         Only the new thing. Nothing else.

WHY:
  The new visual is incomplete until fully integrated.
  You need the working dashboard to access modules during dev.
  You need the new visual isolated to see it clearly.
  Never develop blind -- always have the working version open.

WHEN IS IT FULLY INTEGRATED:
  When the new visual is added as a card in ENG dashboard.
  When it can be summoned from ENG via the overlay.
  When it is in the LEDGER.
  Only then close TAB 1.
```

---

## CURSE 7 -- The Black Iframe Mystery (blackMcMistry)
When summonig a full-canvas module inside an iframe it shows BLACK.
This is NOT a CSS issue. NOT a sandbox issue. NOT a GitHub Pages issue.

```
ROOT CAUSE:
  The tree (math_tree_v4.3 / v5.0) calls center() INLINE at script end:
    drawGridEmpty(); center();

  center() = panX = (window.innerWidth/2/zm) - CX  where CX = 2000

  When called inside an iframe at load time:
    window.innerWidth = 0  (iframe layout not finalized yet)
    panX = (0/2/0.6) - 2000 = -2000px
    plane div renders at left:-2000px -- off screen -- BLACK.

  The EXACT same code works fine in a full tab because
  window.innerWidth is the real viewport width.

WHAT WE TRIED (all failed):
  1. sandbox attribute -- allow-scripts allow-same-origin etc.
     Result: still black. Wrong diagnosis.
  2. allow=fullscreen on iframe
     Result: still black. Wrong diagnosis.
  3. Loading v5.0 instead of v4.3
     Result: same black. Version was not the issue.
  4. Dispatching resize event to iframe contentWindow
     Result: blocked by sandbox + CORS complexity.

WHAT WORKED:
  window.open(LINKS[key], _blank)  -- open tree in NEW TAB
  The tree gets a real viewport. center() fires correctly.
  The tree renders. The user sees it.

THE RULE:
  Any module that calls center() or uses window.innerWidth
  at script-load time (not in a load/resize event) CANNOT
  be summoned in an iframe. It MUST open in a new tab.

  Modules safe for iframe:
    -- pure data panels (no canvas pan/zoom)
    -- modules that init canvas in window.addEventListener(load)
    -- modules with ResizeObserver for canvas sizing

  Modules that need new tab:
    -- math_tree (center() inline)
    -- graph_sandbox (pan/zoom canvas init inline)
    -- any module with   drawX(); center();  at script end

DETECTION PATTERN:
  grep for these patterns at END of script (outside event listeners):
    center()  drawGrid()  drawGridEmpty()  panX =  panY =
  If found at top level -- new tab required.
```

---

## CURSE 8 -- The allow-top-navigation Curse
Adding allow-top-navigation to iframe sandbox lets the iframe HIJACK the parent page.
Any link, redirect, or window.location in the summoned module navigates the parent.
The user loses the dashboard. No BACK button can save them. The page is gone.

```
SYMPTOM:
  User clicks a module card in ENG.
  Module loads in iframe overlay.
  Something in the module triggers navigation.
  ENG dashboard disappears. User is now on the module URL.
  BACK button in browser goes to previous site, not ENG.

ROOT CAUSE:
  sandbox="allow-top-navigation"
  This grants the iframe permission to set window.top.location.
  Any link with target=_top, any window.location= in module JS,
  any form submit = parent page hijacked.

FIX:
  Remove allow-top-navigation from sandbox. Always.
  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
  allow-popups is enough for any external links (they open new tab).
  The parent page is now inviolable.

RULE:
  iframe sandbox NEVER gets allow-top-navigation.
  If a module needs to navigate: use allow-popups (new tab).
  The dashboard is the god context. Nothing inside can touch it.
```

---

## FAILURE LOG

| Date | File | Curse | What happened | Fix |
|------|------|-------|---------------|-----|
| 2026-05-28 | build_eng_v2.py | Curse 2 | unicode · in f-string → CRLF → UnicodeDecodeError on LEDGER.md read | errors='ignore' |
| 2026-05-28 | build_eng_v2.py | Curse 1+2 | JS {{}} + unicode in f-string → SyntaxError f-string empty expression | Rewrite needed |
| 2026-05-28 | build_eng_v2.py | Curse 3 | multi_edit failed — corrupted file, string not found | Full rewrite |

---

*"Each time we touch the builder, black magic is summoned"*
*"More modules = more black magic required"*
*Buenos Aires · May 2026*

---

## CURSE 9 -- The 12-Second LCP (Heavy Kernel Load)

ENG v2.0 loads 6 kernel modules synchronously on page load.
LCP = 12.01s measured in Chrome DevTools.
This is NOT a bug. It is expected behavior.

```
ROOT CAUSE:
  6 kernel modules load and RUN on window load event:
    M1 goldberg_kernel.js    -- builds C60, runs invariants
    M2 graph_axioms.js       -- runs P1-P7 axiom checks
    M3 sar_modular.js        -- computes lam=0.1473 spectral proof
    M4 ns_spectral.js        -- runs NS flow spectral gap
    M5 fractal_search.js     -- runs fractal architecture search
    M6 mnet_nanite.js        -- builds cluster DAG
  All synchronous. All heavy. All correct.
  LCP fires when the largest element paints = after all 6 run.
  12s on first load. Sub-second on cached repeat.

WHAT IS NOT THE PROBLEM:
  Not a network issue (GitHub Pages CDN is fast)
  Not a code bug (everything runs correctly)
  Not a render issue (CLS=0, INP=32ms -- excellent)

WHAT TO DO:
  Accept it. This is a research tool, not a landing page.
  The 12s is the price of having 6 live kernel modules.
  Future optimization: Web Workers for heavy modules.
  But not now. Math first. Performance later.

HOW TO EXPLAIN IT:
  "LCP 12s because 6 physics modules compute on load.
   Same reason a Jupyter notebook takes 10s to start.
   The computation is the feature."

SMALL MODULES (obsidius, valtium, etc) load instantly.
Only ENG v2.0 (the full kernel) has the 12s LCP.
Document this in LEDGER when questioned.
```

---

## CURSE 10 -- The Shared Pop-Up Lock (blackModuleMystry)

When a new-tab module opens a popup window,
ALL other modules inherit the popup state.
Subsequent clicks on other modules think THEY
are the popup module and lock the entire dashboard.

```
SYMPTOM:
  Click sandbox (opens new tab) -> OK
  Go BACK to dashboard
  Click second module -> popup appears (wrong!)
  Click third module -> locked, nothing happens
  Reload page -> vale loads fine in iframe
  
  The popup open/close state is SHARED
  across all module summon() calls.
  Every module thinks it is the one that popped.

ROOT CAUSE:
  summon() checks NEW_TAB_MODULES dict.
  When popup opens, fr.srcdoc is set.
  The overlay stays OPEN with srcdoc content.
  Next summon() call:
    fr.src = ''  (clears iframe)
    overlay already open = logic confused
    NEW_TAB_MODULES check fires again
    sets srcdoc AGAIN even for non-popup modules
    ALL modules now show portal placeholder
    
  The overlay open state + srcdoc state
  are not reset between summons.
  They bleed into the next call.

FIX:
  In overlayClose():
    fr.srcdoc = ''    <- clear srcdoc on close
    fr.src = ''       <- already done
    
  In summon() before NEW_TAB_MODULES check:
    if overlay already open -> close first
    reset ALL iframe state
    THEN decide: new tab or iframe
    
  Add a flag: isPopupOpen = false
  Set true when new tab opens
  Reset in overlayClose()
  Check in summon() before proceeding

THE RULE:
  New-tab modules MUST reset ALL overlay state.
  srcdoc, src, isPopupOpen flag.
  The overlay is not a toggle. It is a state machine.
  Each summon() must start from clean state.
```

**Curse count: 10. All documented. All slain (eventually).**
**Black magic respects the scroll.**

---

## CURSE 11 -- The srcdoc Origin Lock (about:srcdoc freeze)

The portal placeholder uses fr.srcdoc to show "LAUNCHED IN NEW TAB".
srcdoc creates an about:srcdoc document inside the iframe.
This is a DIFFERENT ORIGIN from the parent page.
On next summon(), the browser blocks cross-origin iframe access.
The overlay state machine freezes trying to communicate
with the about:srcdoc document.

```
SYMPTOM:
  Fresh load: all modules work perfectly
  Click SANDBOX or TREE (new tab + srcdoc portal shown)
  Go BACK to dashboard
  Click ANY other module:
    IF srcdoc still in iframe -> freeze
    IF reloaded fresh -> works fine
    
  Two sessions behave differently:
    Session A (fresh):    all work
    Session B (post-tab): locks after new-tab module

ROOT CAUSE:
  fr.srcdoc = '<html>...' sets about:srcdoc as iframe src
  about:srcdoc is cross-origin to parent page
  Browser security: cannot access cross-origin iframe
  fr.onload fires but fr.contentWindow = blocked
  Next summon() tries fr.src = '' on cross-origin frame
  Browser throws silent security exception
  Overlay never resets properly
  All subsequent summons: dead

FIX:
  NEVER use srcdoc for the portal placeholder.
  Instead: use a real URL that we control.
  
  Option A: create shell/portal.html
    Tiny file. Shows "LAUNCHED IN NEW TAB" + arrow.
    Served from same origin as ENG.
    No cross-origin issues. Ever.
    
  Option B: use about:blank
    fr.src = 'about:blank' before summon
    about:blank is same-origin-ish
    Safer than srcdoc.
    
  CHOSEN: Option A (portal.html)
  One tiny file. Zero cross-origin issues.
  Same aesthetic. Full control.
  
THE RULE:
  NEVER set srcdoc in production iframe code.
  srcdoc = about:srcdoc = cross-origin = freeze.
  Always use a real URL from the same domain.
  Even for placeholder content.
  Especially for placeholder content.
```

**Curse count: 11. The srcdoc was the demon. portal.html is the counter-hex.**

---

## CURSE 12 -- The Corkscrew Parasite (insideDizzy)

When entering inside view with cam.rx != 0:
  cam.ry += cam.spin  (horizontal rotation)
  cam.rx = 0.3        (fixed pitch tilt)
  RESULT: corkscrew motion. Viewer feels dizzy.
  WE are spinning, not the sphere.

```
ROOT CAUSE:
  cam.rx tilt + cam.ry spin = helical path
  From outside: looks like a nice angled rotation
  From inside:  looks like the whole room corkscrewing
  The camera is TILTED and SPINNING simultaneously.
  The monkey brain reads this as: I AM MOVING.

FIX:
  In inside mode:
    cam.rx = 0  on ENTER (look straight at equator)
    cam.rx = 0  every frame in animate() (lock it)
    only cam.ry spins
    
  Result: sphere faces pass by HORIZONTALLY
  like a panorama rotating past a fixed observer.
  The monkey brain reads this as: THE SPHERE is moving.
  Correct. Comfortable. Fracyclic.

CODE:
  animate():
    if(!dragging) {
      cam.ry += cam.spin;
      if(_insideMode) cam.rx = 0;  // kill the parasite
    }
    
  toggleInsideView() ENTER:
    cam.rx = 0;  // not 0.3 -- that was the parasite

THE RULE:
  Inside view = lock pitch (rx = 0).
  Only yaw (ry) rotates.
  This is also the VR rule:
    in Quest 3, head rotation handles rx.
    auto-spin should never touch rx.
    Only ry (horizontal orbit) auto-spins.
```

**Curse count: 12. The corkscrew is dead.**

---

## CURSE 13 -- The Ghost Spinner (spinnerEgo)

The SPIN slider starts at value="5" (cam.spin=0.005).
You drag it to 0. It shows 0.000.
The sphere keeps spinning.

ROOT CAUSE (three heads):

  HEAD 1: value="5" not value="0"
    Slider starts spinning. Nobody asked for that.
    Developer thought "a little spin looks nice".
    User cannot find zero. Ego. Haunts forever.

  HEAD 2: floating point
    cam.spin = 0/1000 = 0.0
    BUT JavaScript 0.0 is sometimes not exactly 0.
    cam.ry += 0.0 still ticks on some engines.
    Fix: if(Math.abs(cam.spin) > 0.00001) only then add.

  HEAD 3: inside mode sets cam.spin = 0.0008
    This maps to slider value = 0.8 (rounds to 0 visually)
    Slider shows "0.000" but spin is NOT zero.
    User confused. Thinks they stopped it.
    They have not stopped it.

```
FIX:
  1. Slider starts at value="0" (no ego spin on load)
  2. Slider oninput: if value < 1 -> snap to exact 0
     var sv = +this.value;
     cam.spin = sv < 1 ? 0 : sv/1000;
  3. animate(): float zero guard
     if(Math.abs(cam.spin) > 0.00001) cam.ry += cam.spin;
  4. inside mode: cam.spin = 0.001 (visible on slider as 1)
     slider updates to show 1 so user can see and control it

THE RULE:
  Default spin = 0. Always.
  Motion is opt-in, not opt-out.
  The user starts still. They choose to move.
  The ego of "a little spin looks nice on load"
  is the enemy of user control.
  
  This is also the VR rule:
  In Quest 3: start still. Motion sickness kills apps.
  Auto-spin = nausea. Still start = comfort.
  Let the user orbit with their head/hand.
  Only spin on explicit request.
```

**Curse count: 13. The ghost spinner is dead.**
**It came back to haunt us. We knew. We fixed it.**
**Ego = ghost. Documentation = exorcism.**


---

## CURSE 14 -- The CR Accumulator (gitiumCurse)

Repeated Python patch scripts on a Windows HTML file
accumulate carriage returns.

```
ROOT CAUSE:
  File on disk: CRLF line endings (Windows)
  Python reads with errors="ignore"
  Each patch: read -> modify -> write
  
  Problem: some patches use raw string replacement
  that matches \n but the file has \r\n
  When write happens: \r\n + \n = \r\r\n
  Next patch: \r\r\n + \n = \r\r\r\n
  4 patches later: 4 carriage returns per line
  File: 175KB instead of 158KB
  All searches fail (wrong whitespace)
  File is garbage.

HOW TO DETECT:
  raw.count(b"\r") != raw.count(b"\r\n")
  lone CRs > 0 = CURSED

HOW TO FIX:
  git checkout <last_clean_commit> -- shell/file.html
  Verify: lone CRs = 0
  Then re-apply ALL patches in ONE script.

THE RULE:
  DO NOT apply patches incrementally to HTML files.
  Write ONE clean script that does ALL changes.
  Run once. Verify. Commit. Done.
  
  BEFORE any patch script:
    raw = SRC.read_bytes()
    src = raw.decode("utf-8", errors="ignore")
    src = src.replace("\r\n", "\n")  <- NORMALIZE FIRST
    ... do all patches on normalized src ...
    SRC.write_bytes(src.encode("utf-8"))  <- write as UTF-8 no BOM

  This is KERNELIMAGIC PATTERN 3:
    normalize line endings first
    patch on clean \n-only string
    write back as UTF-8
    one script, all patches, run once

PATTERN 3 -- Normalize Then Patch:
  src = SRC.read_bytes().decode("utf-8", errors="ignore")
  src = src.replace("\r\n", "\n").replace("\r", "\n")
  # ... all patches here on clean src ...
  SRC.write_text(src, encoding="utf-8", newline="\n")

This is now the law.
The CR accumulator is documented.
The git restore is the counter-hex.
```

**Curse count: 14. The CR accumulator is named.**
**git checkout is the exorcism.**
**PATTERN 3 is the prevention.**


---

## CURSE 15 -- The Invisible Sort (sortGhost)

sorted.sort() appears to work.
The string is found in the file.
The patch reports OK.
The sort is WRONG.

```
ROOT CAUSE:
  The sort line in genesis_v8.1.html
  was ALREADY patched by a previous
  surviving script run.
  
  Current file contains:
    sorted.sort(function(a,b){
      return _insideMode ? b.depth-a.depth
                         : a.depth-b.depth;
    });
    
  Patch script looks for:
    sorted.sort(function(a,b){return a.depth-b.depth});
    
  NOT FOUND. Patch reports FAIL.
  But the sort IS already correct.
  The FAIL was a false negative.

THE LESSON:
  Before patching: CHECK what is already there.
  A FAIL on patch != the file is wrong.
  A FAIL on patch = the old string not found.
  Could mean: already patched. Or broken. Or different.
  
  ALWAYS verify the INTENT not just the patch result:
    check = "_insideMode?b.depth" in src
    if check: print("SORT ALREADY CORRECT -- skip")
    else: apply patch

PATTERN 3 ADDENDUM:
  After all patches run:
  verify INTENT (what should be true)
  not just patch success (was old string found).
  
  results["P8 sort intent"] = "_insideMode?b.depth" in src
  OR
  results["P8 sort intent"] = "_insideMode ? b.depth" in src

CURRENT STATE of sort:
  sorted.sort(function(a,b){
    return _insideMode ? b.depth-a.depth : a.depth-b.depth;
  });
  CORRECT. No patch needed.
```

**Curse count: 15. The invisible sort. False negative.**
**The file was right. The patch string was wrong.**
**Check intent. Not just patch success.**


---

## CURSE 16 -- The Shadow Duplicate (shadowInject)

Pattern 1 injects JS before last </script>.
The base file ALREADY contains the JS from a previous session.
Inject runs again = TWO copies of same function.
Two var _insideMode. Two toggleInsideView.
JavaScript: last declaration wins.
But BOTH run. State is split. Ghost behavior.

```
ROOT CAUSE:
  Session 1: inject toggleInsideView into genesis_v8.1.html
  Commit. Push.
  
  Session 2: restore to ae55ac4 (already has the injection)
  Run inject script again.
  NOW: TWO toggleInsideView in file.
  TWO var _insideMode.
  The second one overwrites the first at parse time.
  But event handlers bound to first function.
  Chaos.

DETECTION:
  ALWAYS check before injecting:
    count = src.count("function toggleInsideView")
    if count > 0:
      print("ALREADY EXISTS -- replace, do not append")
      
THE RULE:
  Before Pattern 1 inject:
  Check if the target function already exists.
  If yes: REPLACE it, not append.
  
  if "function toggleInsideView" in src:
    # replace existing
    src = re.sub(r'var _insideMode.*?^}',
                 NEW_JS, src,
                 flags=re.DOTALL|re.MULTILINE)
  else:
    # safe to inject at end
    src = src[:last] + NEW_JS + src[last:]

PATTERN 1 ADDENDUM:
  Check for existing before inject.
  Replace if found. Append only if new.
  
THE CORRECT BASE for inside-view work:
  git checkout ae55ac4 -- shell/genesis_v8.1.html
  This base ALREADY has toggleInsideView (from previous session).
  DO NOT inject again.
  ONLY patch the existing function via string replace.
```

**Curse count: 16. The shadow duplicate.**
**The base already had the injection.**
**Replace, do not append.**


---

## CURSE 17 -- The Block Eater (regexDevour)

re.search finds a block.
block_start = 6387
block_end   = 144409
Replace block with new content.
File shrinks from 158KB to 11KB.

```
ROOT CAUSE:
  The regex matched from position 6387
  all the way to the LAST cx.restore();}
  in the ENTIRE file.
  
  The file has many cx.restore(); calls.
  The greedy .* ate everything between
  the inside view block start
  and the LAST restore() in the file.
  
  src[:6387] + NEW_BLOCK + src[144409:]
  src[144409:] = only the last 14KB of file
  src[:6387]   = only first 6KB
  Everything in between: EATEN.

THE FIX:
  NEVER use greedy regex to find block end.
  NEVER replace large blocks of HTML.
  
  Instead: ONLY replace the specific function text.
  Find the exact function string.
  Replace ONLY that string.
  Nothing more. Nothing less.
  
  PATTERN 3 ADDENDUM 2:
    Do NOT find block by start+end regex.
    Find the EXACT string you want to change.
    If string is too long to match: split into parts.
    Replace each part separately.
    
  The safest replace for functions:
    OLD = "function toggleInsideView() {
  var btn..."
    NEW = "function toggleInsideView() {
  var btn..."
    src = src.replace(OLD, NEW)
    assert src.count("function toggleInsideView") == 1

THE RECOVERY:
  git checkout ae55ac4 -- shell/genesis_v8.1.html
  Always. Every time. Do not cry. Just restore.
  The scroll protects the cave.
```

**Curse count: 17. The block eater.**
**Greedy regex devoured 133KB of the file.**
**git restore is always the answer.**
**Replace functions by exact string. Never by regex block.**
