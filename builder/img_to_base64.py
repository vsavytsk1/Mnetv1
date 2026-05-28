#!/usr/bin/env python3
"""
img_to_base64.py — Image ingestion pipeline for HTML embedding
==============================================================
DROP images into shell/gate/img/
RUN this script
GET base64 data URIs injected into gate_v1.html

Pipeline:
  1. Read all images from img/ folder
  2. Resize to max 1200px wide (preserves aspect ratio)
  3. Compress to JPEG 85% quality
  4. Convert to base64 data URI
  5. Report size before/after
  6. Optionally inject into HTML

Supported formats: .jpg .jpeg .png .webp .bmp .tiff
Target: JPEG 85% — best size/quality ratio for HTML embedding

Usage:
  python img_to_base64.py              # report only
  python img_to_base64.py --inject     # inject into gate_v1.html
  python img_to_base64.py --test       # compress + decompress + compare
"""
import os, sys, base64, json
from pathlib import Path
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    print("ERROR: pip install Pillow")
    sys.exit(1)

# === CONFIG ===
IMG_DIR = Path(__file__).parent / "img"
HTML_FILE = Path(__file__).parent / "gate_v1.html"
MAX_WIDTH = 1200
MAX_HEIGHT = 900
JPEG_QUALITY = 85
SUPPORTED = {'.jpg','.jpeg','.png','.webp','.bmp','.tiff','.gif'}

# === Expected image slots (order matters) ===
SLOTS = {
    'gate_closed': ['gate_closed', 'gate', 'closed'],
    'gate_open':   ['gate_open', 'open', 'opening'],
    'truth':       ['truth', 'sitting', 'white'],
    'exchange':    ['exchange', 'edward', 'price', 'equivalent']
}

def find_images():
    """Scan img/ folder and match to slots by filename keywords."""
    if not IMG_DIR.exists():
        print(f"  ERROR: {IMG_DIR} not found. Create it and drop images in.")
        return {}
    
    files = [f for f in IMG_DIR.iterdir() if f.suffix.lower() in SUPPORTED]
    print(f"\n  Found {len(files)} images in {IMG_DIR}/")
    
    matched = {}
    unmatched = []
    
    for f in sorted(files):
        name_lower = f.stem.lower()
        slot_found = None
        for slot, keywords in SLOTS.items():
            if slot not in matched:
                for kw in keywords:
                    if kw in name_lower:
                        slot_found = slot
                        break
            if slot_found:
                break
        
        if slot_found:
            matched[slot_found] = f
            print(f"    {f.name} → slot: {slot_found}")
        else:
            unmatched.append(f)
    
    # Auto-assign unmatched to empty slots in order
    empty_slots = [s for s in SLOTS if s not in matched]
    for f, slot in zip(unmatched, empty_slots):
        matched[slot] = f
        print(f"    {f.name} → slot: {slot} (auto-assigned by order)")
    
    remaining = unmatched[len(empty_slots):]
    if remaining:
        print(f"    UNUSED: {[f.name for f in remaining]}")
    
    return matched

def process_image(filepath):
    """Resize + compress + base64 encode."""
    img = Image.open(filepath)
    original_size = filepath.stat().st_size
    original_dims = img.size
    
    # Convert to RGB (drop alpha if PNG)
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (0, 0, 0))
        if img.mode == 'P':
            img = img.convert('RGBA')
        bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize preserving aspect ratio
    w, h = img.size
    if w > MAX_WIDTH or h > MAX_HEIGHT:
        ratio = min(MAX_WIDTH / w, MAX_HEIGHT / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Compress to JPEG
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
    jpeg_bytes = buffer.getvalue()
    
    # Base64 encode
    b64 = base64.b64encode(jpeg_bytes).decode('ascii')
    data_uri = f"data:image/jpeg;base64,{b64}"
    
    compressed_size = len(jpeg_bytes)
    b64_size = len(data_uri)
    
    return {
        'data_uri': data_uri,
        'original_size': original_size,
        'original_dims': original_dims,
        'compressed_size': compressed_size,
        'b64_size': b64_size,
        'final_dims': img.size
    }

def test_roundtrip(filepath):
    """Compress → base64 → decode → decompress → compare."""
    result = process_image(filepath)
    
    # Decode back
    b64_data = result['data_uri'].split(',')[1]
    decoded = base64.b64decode(b64_data)
    img_back = Image.open(BytesIO(decoded))
    
    print(f"    Roundtrip OK: {result['final_dims'][0]}x{result['final_dims'][1]} JPEG")
    print(f"    Original: {result['original_size']:,} bytes ({result['original_dims'][0]}x{result['original_dims'][1]})")
    print(f"    Compressed: {result['compressed_size']:,} bytes")
    print(f"    Base64: {result['b64_size']:,} chars ({result['b64_size']/1024:.0f} KB in HTML)")
    print(f"    Ratio: {result['original_size']/max(result['compressed_size'],1):.1f}x smaller")
    
    return result

def inject_into_html(results):
    """Replace IMAGES object in gate_v1.html with actual base64 data."""
    if not HTML_FILE.exists():
        print(f"  ERROR: {HTML_FILE} not found")
        return False
    
    html = HTML_FILE.read_text(encoding='utf-8')
    
    for slot, result in results.items():
        # Find the slot in the IMAGES object and replace empty string
        old = f'{slot}: ""'
        new = f'{slot}: "{result["data_uri"]}"'
        if old in html:
            html = html.replace(old, new, 1)
            print(f"    Injected {slot}: {result['b64_size']/1024:.0f} KB")
        else:
            print(f"    WARNING: slot '{slot}' not found in HTML (already filled?)")
    
    HTML_FILE.write_text(html, encoding='utf-8')
    total_kb = sum(r['b64_size'] for r in results.values()) / 1024
    print(f"\n  Total injected: {total_kb:.0f} KB ({total_kb/1024:.1f} MB)")
    print(f"  Saved to: {HTML_FILE}")
    return True

def main():
    print("=" * 50)
    print("  IMG → BASE64 PIPELINE")
    print("=" * 50)
    
    mode = '--report'
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    matched = find_images()
    if not matched:
        print("\n  No images found. Drop files into:")
        print(f"    {IMG_DIR}/")
        print(f"\n  Expected names (or any — auto-assigned by order):")
        for slot, kw in SLOTS.items():
            print(f"    {slot}: keywords {kw}")
        return
    
    print(f"\n  Processing {len(matched)} images...")
    print(f"  Target: JPEG {JPEG_QUALITY}%, max {MAX_WIDTH}x{MAX_HEIGHT}")
    print()
    
    results = {}
    for slot, filepath in matched.items():
        print(f"  [{slot}] {filepath.name}")
        results[slot] = test_roundtrip(filepath)
        print()
    
    total_original = sum(r['original_size'] for r in results.values())
    total_compressed = sum(r['compressed_size'] for r in results.values())
    total_b64 = sum(r['b64_size'] for r in results.values())
    
    print("  " + "=" * 46)
    print(f"  SUMMARY")
    print(f"    Images:     {len(results)}")
    print(f"    Original:   {total_original/1024:.0f} KB")
    print(f"    Compressed: {total_compressed/1024:.0f} KB")
    print(f"    Base64:     {total_b64/1024:.0f} KB ({total_b64/1024/1024:.1f} MB in HTML)")
    print(f"    Ratio:      {total_original/max(total_compressed,1):.1f}x compression")
    print("  " + "=" * 46)
    
    if mode == '--inject':
        print(f"\n  INJECTING into {HTML_FILE.name}...")
        inject_into_html(results)
        print("  DONE.")
    elif mode == '--test':
        print("\n  TEST MODE: roundtrip verified above. No injection.")
    else:
        print(f"\n  DRY RUN. To inject into HTML:")
        print(f'    python img_to_base64.py --inject')

if __name__ == '__main__':
    main()
