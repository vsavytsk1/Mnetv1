#!/usr/bin/env python3
"""
smr.py — StrangerDanger patch utility.
Adds Layer 5 (English Technical Brain) to existing vault.
Run ONCE after --build. Decrypts, patches, re-encrypts same passphrase.
Part of the StrangerDanger ecosystem (github.com/vsavytsk1/StrangerDanger).
"""
import json, hmac, hashlib, secrets, sys
from pathlib import Path
from getpass import getpass
from datetime import datetime

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from argon2.low_level import hash_secret_raw, Type
except ImportError:
    print("pip install -r requirements.txt"); sys.exit(1)

MAGIC=b"VLADVAULT"; VERSION=b"\x01"
SALT_LEN=32; NONCE_LEN=12; HMAC_LEN=32
A2_TIME=3; A2_MEM=65536; A2_PARA=4; A2_LEN=32
VAULT_PATH = Path("DangerDoNotHoldInMemory/2pComplete/personality.vault")

LAYER5 = {
    "note": "Injected 2026-05-22. WhatsApp=99.1% Spanish casual life. English technical brain lives in GitHub/VSCode/4am AI sessions. This is the other half.",
    "technical_proficiency": {
        "python":     "intermediate-advanced — NumPy, SciPy, CuPy CUDA12.9, h5py, multiprocessing",
        "vba":        "advanced — production automation, replaced 20yr manual process at AmEx",
        "sql":        "intermediate — AmEx/JPM internal systems",
        "javascript": "intermediate — Three.js, WebXR, Electron, goldberg_kernel.js",
        "latex":      "functional — physics papers, KaTeX equation validation",
        "git":        "functional — 5 public repos, GitHub Pages on all"
    },
    "english_register": "Switches to English for: physics, code, AI sessions, GitHub, X. Long-form explosions (2000+ words) ONLY in English with AI. Spanish brain=6.9 words avg, warm, polite. English brain=precise, paranoid, 4am.",
    "active_projects": [
        "SpookyPrimes — F_gauge=7 verified, NCG, phase7_v3.py",
        "MachineNet — fullerene knowledge graph, goldberg_kernel.js, VR shell v9",
        "StrangerDanger — this vault, shipped",
        "VALE/JARVIS — local AI, llama3, no cloud",
        "Mnetv1 — Mobius precursor, shipped"
    ],
    "work_history": [
        "AmEx — KYC/AML automation, USA-LatAm corridor, 3+ years",
        "JPMorgan — Automation CoE Project Owner, Agile",
        "Lock mechanism specialist — 2 years Buenos Aires",
        "Current — AI pipeline engineer, large corp"
    ],
    "languages_full": [
        "Spanish (Rioplatense native)",
        "Portuguese (Rio native)",
        "Russian (Soviet family native)",
        "Ukrainian (grandparent native)",
        "English (advanced — corporate+technical+academic)"
    ],
    "cognitive_profile": {
        "pattern": "generates first, verifies later — but DOES verify (paranoia checklist, 3-run protocol)",
        "domains": "holds 5+ domains simultaneously: physics, VR, AI, finance, career",
        "hours":   "4am — not a choice, just true",
        "energy":  "3.2% unhinged in WhatsApp = 4am physics sessions leaking into messages",
        "depth":   "3 deep contacts of 89 — threat-detection explains the number",
        "bias":    "iterates obsessively, never deletes versions (Gaming_Desk_v30, phase7_v4)"
    },
    "the_thesis": "UTN Chemical Engineering (2012, not finished) and goldberg_kernel.js are the same person. The degree was the cave.",
    "verified_result": "F_gauge(A_F)=7.000000 — 3 runs identical. Step 4 NOT closed.",
    "north_star": "Find the role where KYC automation gets you in the door, 5 languages make you irreplaceable, and nobody minds Saturday mornings looking for subalgebra plateaus.",
    "cave_dweller_parable": "I was a crazy guy in a cave making imaginary spoons. Some carpenter picks one up and builds 400 houses. Everyone throws oranges into the cave.",
    "manic_brake": "If next action is PUBLIC (tweet, email to mathematicians, launch video) — slow down once, cold pass after 4hrs. He does not resent the brake. He resents the flattering.",
    "injected_at": datetime.utcnow().isoformat() + "Z"
}

def derive_key(pw, salt):
    return hash_secret_raw(pw.encode(), salt, A2_TIME, A2_MEM, A2_PARA, A2_LEN, Type.ID)

def decrypt_vault(data, pw):
    if not data.startswith(MAGIC): raise ValueError("Not a valid vault.")
    o=len(MAGIC)+len(VERSION)
    salt=data[o:o+SALT_LEN]; o+=SALT_LEN
    non=data[o:o+NONCE_LEN]; o+=NONCE_LEN
    mac=data[o:o+HMAC_LEN];  o+=HMAC_LEN
    ct=data[o:]
    key=derive_key(pw, salt)
    if not hmac.compare_digest(mac, hmac.new(key, salt+non+ct, hashlib.sha256).digest()):
        raise ValueError("TAMPER DETECTED.")
    return AESGCM(key).decrypt(non, ct, None)

def reencrypt(plaintext_bytes, pw):
    salt=secrets.token_bytes(SALT_LEN)
    nonce=secrets.token_bytes(NONCE_LEN)
    key=derive_key(pw, salt)
    ct=AESGCM(key).encrypt(nonce, plaintext_bytes, None)
    body=salt+nonce+ct
    mac=hmac.new(key, body, hashlib.sha256).digest()
    return MAGIC+VERSION+salt+nonce+mac+ct

if __name__ == "__main__":
    if not VAULT_PATH.exists():
        print(f"Not found: {VAULT_PATH}"); sys.exit(1)
    pw = getpass("Passphrase: ")
    print("Decrypting...")
    try:
        plain = decrypt_vault(VAULT_PATH.read_bytes(), pw)
    except Exception as e:
        print(f"FAILED: {e}"); sys.exit(1)
    matrix = json.loads(plain)
    matrix["layer5_english_brain"] = LAYER5
    matrix.setdefault("layer4_live", {}).setdefault("entries", []).append({
        "date":   datetime.utcnow().strftime("%Y-%m-%d"),
        "source": "patch_layer5.py",
        "note":   "Layer 5 injected. English technical brain added. WhatsApp blind spot patched."
    })
    print("Re-encrypting...")
    VAULT_PATH.write_bytes(reencrypt(json.dumps(matrix, ensure_ascii=False).encode(), pw))
    print(f"✓ Done. {VAULT_PATH.stat().st_size/1024:.1f} KB")
    print("Run --open to verify.")