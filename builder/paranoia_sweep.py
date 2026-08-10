"""Full paranoia sweep: static byte-scan every GIT-TRACKED .html in the repo.
Catches the curses: loneCR, U+FFFD (rune rot), BOM, escaped closing tag <\\/,
unbalanced <script>, and truncation (no closing </html>). ASCII-only source.
Prints only the SICK files + a final tally. Exit 1 if any sin found.
"""
import subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked_html():
    # -z = NUL-delimited, no quoting/escaping of unicode or spaced names
    out = subprocess.check_output(['git', 'ls-files', '-z', '*.html'], cwd=ROOT).decode('utf-8', 'replace')
    return [l for l in out.split('\0') if l]


def scan(rel):
    path = os.path.join(ROOT, rel.replace('/', os.sep))
    raw = open(path, 'rb').read()
    txt = raw.decode('utf-8', 'replace')
    sins = []
    lone = sum(1 for i, b in enumerate(raw) if b == 13 and (i + 1 >= len(raw) or raw[i + 1] != 10))
    if lone:                              sins.append(f'loneCR={lone}')
    if txt.count('\ufffd'):               sins.append(f'FFFD={txt.count(chr(0xfffd))}')
    if raw[:3] == b'\xef\xbb\xbf':         sins.append('BOM')
    if '<\\/' in txt:                     sins.append(f'escClose={txt.count(chr(60)+chr(92)+chr(47))}')
    so, sc = txt.count('<script'), txt.count('</script>')
    if so != sc:                          sins.append(f'script {so}/{sc}')
    low = txt.rstrip().lower()
    if not low.endswith('</html>'):        sins.append('no </html> (truncated?)')
    return len(raw), sins


def main():
    files = tracked_html()
    print(f'=== PARANOIA SWEEP: {len(files)} git-tracked .html ===')
    sick = []
    total = 0
    for rel in files:
        try:
            n, sins = scan(rel)
        except Exception as e:
            sins = [f'READ-FAIL {e}']
            n = 0
        total += n
        if sins:
            sick.append((rel, sins))
    if sick:
        print(f'\n!! {len(sick)} SICK file(s):')
        for rel, sins in sick:
            print(f'   {rel}  ->  {", ".join(sins)}')
    else:
        print('all clean.')
    print(f'\nscanned {len(files)} files, {total/1024:.0f} KB tracked html. '
          f'SWEEP: {"PASS" if not sick else "FAIL"}')
    return 0 if not sick else 1


if __name__ == '__main__':
    sys.exit(main())
