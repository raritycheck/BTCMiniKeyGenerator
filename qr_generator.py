#!/usr/bin/env python3
"""Generate QR code images small enough to print at 4.5 x 4.5 mm."""

import qrcode
from qrcode.constants import ERROR_CORRECT_L

# ── Put your keys here ──────────────────────────────────────────────
# label → data string.  Each entry produces one PNG named <label>.png
KEYS = { ,
}

DPI = 600
# ─────────────────────────────────────────────────────────────────────


def generate_qr(data, filename, dpi=600):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=5,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img.save(filename, dpi=(dpi, dpi))

    modules = qr.modules_count
    px = modules * qr.box_size
    mm = px / dpi * 25.4
    print(f"  {filename:<30} {data[:40]:<42} "
          f"v{qr.version} ({modules}×{modules})  {mm:.2f}×{mm:.2f} mm")


if __name__ == "__main__":
    print(f"Generating {len(KEYS)} QR codes @ {DPI} DPI\n")
    print(f"  {'File':<30} {'Data':<42} {'QR':>14}  {'Print size'}")
    print(f"  {'─'*30} {'─'*42} {'─'*14}  {'─'*14}")
    for label, data in KEYS.items():
        generate_qr(data, f"{label}.png", dpi=DPI)
    print(f"\nDone.")
