"""Add Press ENTER to HOLLY7.py then recompile."""
from pathlib import Path
import subprocess, sys

f = Path(__file__).parent / "HOLLY7.py"
s = f.read_text(encoding="utf-8")
if 'Press ENTER' not in s:
    s = s.rstrip() + '\ninput("  Press ENTER to close...")\n'
    f.write_text(s, encoding="utf-8")
    print("Added Press ENTER")
else:
    print("Already there")

# Recompile
print("Recompiling...")
r = subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--onefile", "--name", "HOLLY7", "--console",
    "--distpath", "builder/dist",
    "--workpath", "builder/_pyibuild",
    "--specpath", "builder",
    "builder/HOLLY7.py"
], capture_output=True, text=True, encoding="utf-8", errors="replace")
# Show last 10 lines
lines = (r.stdout + r.stderr).splitlines()
for l in lines[-10:]:
    print(l)
print("Return code:", r.returncode)
