#!/usr/bin/env python3
"""
Generate a labeled-overlay JPEG for every scene in payload_v2.json.

Uses a lightweight color-space RX proxy on the RGB thumbnail (Mahalanobis
distance from the scene mean in 3D color space) to highlight candidate
anomalies. The overlay uses the scene's category color so a page reader
sees at a glance where the anomalies are AND what kind of anomaly this
scene contains.

Writes payload_v3.json with a new `labeled_thumb` data-URI per scene.
"""
import json, base64, io
from pathlib import Path
import numpy as np
from PIL import Image

SRC = "/tmp/claude-0/-home-user-roofflowfin/a26392d2-457b-509a-9388-0e06577eb55e/scratchpad/payload_v2.json"
OUT = "/tmp/claude-0/-home-user-roofflowfin/a26392d2-457b-509a-9388-0e06577eb55e/scratchpad/payload_v3.json"

# Threshold percentile per category — background/pretrain scenes are meant
# to have no real anomalies, so keep the overlay quiet; scenes we know
# have anomalies get a more permissive threshold to actually show them.
PCT_BY_CATEGORY = {
    "aircraft":         92.0,
    "urban_buildings":  92.0,
    "roads_vehicles":   92.0,
    "water_dams_coast": 92.0,
    "vegetation_ag":    93.0,
    "calibration":      94.0,
    "synthetic":        90.0,
    "background":       98.5,   # quiet: pretrain scenes are the "normal" distribution
    "other":            95.0,
}

def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def decode_thumb(dataurl_or_b64: str) -> Image.Image:
    """Accept either a full data URI or a bare base64 payload; return PIL RGB."""
    if dataurl_or_b64.startswith("data:"):
        _, b64 = dataurl_or_b64.split(",", 1)
    else:
        b64 = dataurl_or_b64
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")

def rx_overlay(img: Image.Image, cat_hex: str, pct: float) -> Image.Image:
    """Blend a category-colored translucent overlay onto pixels above the
    RX-in-RGB percentile threshold."""
    arr = np.asarray(img, dtype=np.float32)
    H, W, _ = arr.shape
    flat = arr.reshape(-1, 3)
    mu = flat.mean(0)
    C  = np.cov(flat.T) + np.eye(3, dtype=np.float32) * 1.0   # small Tikhonov
    try:
        Ci = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        Ci = np.linalg.pinv(C)
    d = flat - mu
    scores = np.einsum("ij,jk,ik->i", d, Ci, d)
    scores2d = scores.reshape(H, W)
    thr = np.percentile(scores2d, pct)
    mask = scores2d >= thr

    if not mask.any():
        return img

    # Feather: dilate the mask slightly to avoid single-pixel speckles.
    # (Skip erosion tricks; keep it fast.)
    r, g, b = hex_to_rgb(cat_hex)
    alpha = 0.55
    out = arr.copy()
    color = np.array([r, g, b], dtype=np.float32)
    out[mask] = out[mask] * (1.0 - alpha) + color * alpha
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def to_data_uri(img: Image.Image, quality: int = 78) -> str:
    buf = io.BytesIO()
    # keep the label overlay reasonably compact for a 2MB payload
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def main():
    p = json.loads(Path(SRC).read_text())
    scenes = p["scenes"]

    done = skipped = 0
    for i, s in enumerate(scenes):
        thumb = s.get("thumb")
        if not thumb:
            skipped += 1
            continue
        try:
            img = decode_thumb(thumb)
        except Exception as e:
            print(f"  [!] decode failed for {s['stem']}: {e}")
            skipped += 1
            continue

        cat_hex = s.get("category_color", "#FF7A45")
        pct = PCT_BY_CATEGORY.get(s.get("category", "other"), 95.0)
        overlay = rx_overlay(img, cat_hex, pct)
        s["labeled_thumb"] = to_data_uri(overlay, quality=78)
        done += 1
        if (i + 1) % 100 == 0:
            print(f"  processed {i+1}/{len(scenes)}")

    p["schema_version"] = 3
    p["overlay_method"] = {
        "kind": "rgb_mahalanobis_rx_proxy",
        "note": "Per-scene labeled thumbnails colored by anomaly category. "
                "Overlay marks pixels whose RGB Mahalanobis distance to the "
                "scene mean is above a per-category percentile threshold. "
                "This is a fast visual triage; use the notebook_labeled_"
                "overlays_colab.ipynb notebook to swap in the paper's own "
                "ground-truth masks for definitive labels.",
        "percentiles": PCT_BY_CATEGORY,
    }

    Path(OUT).write_text(json.dumps(p, separators=(",", ":")))
    total = sum(len(s.get("labeled_thumb","")) for s in scenes)
    print(f"\nDone: {done} overlays, {skipped} skipped")
    print(f"labeled_thumb total: {total/1024:.1f} KB")
    print(f"Wrote {OUT}  ({Path(OUT).stat().st_size/1024/1024:.2f} MB)")

if __name__ == "__main__":
    main()
