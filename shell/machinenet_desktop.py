"""
MachineNet v4.4-W11D — Desktop Launcher (.exe compatible)
Budget: 500K default, 5M max. Pure geometry.
pyinstaller --onefile --windowed bundles this + HTML into one .exe
"""
import webview
import os
import sys
import tempfile

def get_html_path():
    """Find HTML whether running as script or frozen .exe"""
    # PyInstaller sets sys._MEIPASS when frozen
    if getattr(sys, '_MEIPASS', None):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    
    html = os.path.join(base, "shell", "machinenet_shell_v4.4_W11D_mobius.html")
    if os.path.exists(html):
        return html
    
    # Fallback: same directory as script
    html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "machinenet_shell_v4.4_W11D_mobius.html")
    if os.path.exists(html):
        return html
    
    return None

HTML = get_html_path()
if not HTML:
    print("ERROR: HTML file not found!")
    print("Expected: machinenet_shell_v4.4_W11D_mobius.html")
    input("Press Enter to exit...")
    sys.exit(1)

print(f"MachineNet v4.4-W11D")
print(f"HTML: {HTML}")

window = webview.create_window(
    title="MachineNet - MOBIUSIFY v4.4-W11D",
    url=HTML,
    width=1920,
    height=1080,
    resizable=True,
    fullscreen=False,
    min_size=(800, 600),
    background_color="#050510",
    text_select=True,
)

webview.start(
    debug=False,
    gui="edgechromium",
)
