#!/usr/bin/env python3
"""Augment the 655-scene payload with anomaly categories, colors, and normalized Drive links."""
import json, re, sys

SRC = "/root/.claude/uploads/a26392d2-457b-509a-9388-0e06577eb55e/678cbece-dataset_full_payload.json"
OUT = "/tmp/claude-0/-home-user-roofflowfin/a26392d2-457b-509a-9388-0e06577eb55e/scratchpad/payload_v2.json"

# ---------------------------------------------------------------
# Category taxonomy — colors are the legend across the entire UI.
# ---------------------------------------------------------------
CATEGORIES = [
    # id                  label                                   color        (light on dark)
    ("aircraft",          "Aircraft on tarmac",                    "#FF7A45"),
    ("urban_buildings",   "Urban / Buildings / Settlements",       "#4FD1FF"),
    ("roads_vehicles",    "Roads & Vehicles",                      "#FFC857"),
    ("water_dams_coast",  "Water, Dams & Coast",                   "#7ED8B8"),
    ("vegetation_ag",     "Vegetation & Agriculture",              "#A3E066"),
    ("calibration",       "Calibration / Survey Targets",          "#C792EA"),
    ("synthetic",         "Synthetic implants",                    "#F686BD"),
    ("background",        "Clean background (pretrain)",           "#4A5568"),
    ("other",             "Other / Mixed",                         "#9EA7B8"),
]
CAT_ID = {c[0]: c for c in CATEGORIES}

# ---------------------------------------------------------------
# Rule-based classifier: stem + dataset + declared anomaly_type
# ---------------------------------------------------------------
STEM_HINTS = [
    (r"^abu-airport",         "aircraft"),
    (r"sandiego|san.diego",   "aircraft"),
    (r"airport|tarmac|plane|airplane|aircraft", "aircraft"),
    (r"^abu-urban",           "urban_buildings"),
    (r"hydice.urban|hydice_urban", "roads_vehicles"),
    (r"pavia|berlin|houston|chikusei|muufl|utopia|holden|pingan|qingyun|tangdaowan", "urban_buildings"),
    (r"road|highway|street|vehicle|car", "roads_vehicles"),
    (r"^abu-beach",           "water_dams_coast"),
    (r"beach|coast|water|dam|river|lake|harbor|port|marine", "water_dams_coast"),
    (r"salinas|indian_pines|botswana|ksc|whu_honghu|whu_hanchuan|whu_longkou|dioni|loukia|trento", "vegetation_ag"),
    (r"crop|farm|agri|vegetation|forest|grass|wetland", "vegetation_ag"),
    (r"^ang\d{8}",            "calibration"),      # AVIRIS-NG flight targets
    (r"nili_fossae|mars",     "calibration"),
    (r"syn|synthetic|implant","synthetic"),
]

TYPE_TO_CAT = {
    "Clean background (pretrain)": "background",
    "AVIRIS-NG survey target":     "calibration",
    "Aircraft on tarmac":          "aircraft",
    "Aircraft (San Diego)":        "aircraft",
    "Urban anomalies":             "urban_buildings",
    "Urban vehicles (HYDICE)":     "roads_vehicles",
    "Beach anomalies":             "water_dams_coast",
    "Rare-class anomaly":          "vegetation_ag",   # dominant Tier-2 rare classes are ag/vegetation
    "Synthetic implant":           "synthetic",
}

# Per-stem overrides for Tier-2 rare-class scenes (dataset semantics we know)
RARE_CLASS_OVERRIDES = {
    "Trento":         "urban_buildings",   # Trento rural airport + roofs
    "pavia_u":        "urban_buildings",
    "pavia_c":        "urban_buildings",
    "berlin":         "urban_buildings",
    "houston13":      "urban_buildings",
    "houston18":      "urban_buildings",
    "chikusei":       "urban_buildings",
    "muufl":          "urban_buildings",
    "utopia":         "urban_buildings",
    "holden":         "urban_buildings",
    "pingan":         "urban_buildings",
    "qingyun":        "urban_buildings",
    "tangdaowan":     "water_dams_coast",
    "botswana":       "vegetation_ag",
    "ksc":            "vegetation_ag",
    "indian_pines":   "vegetation_ag",
    "salinas":        "vegetation_ag",
    "whu_honghu":     "vegetation_ag",
    "whu_hanchuan":   "vegetation_ag",
    "whu_longkou":    "vegetation_ag",
    "dioni":          "vegetation_ag",
    "loukia":         "vegetation_ag",
    "nili_fossae":    "calibration",
    "unknown":        "other",
}

def classify(stem: str, anomaly_type: str, sensor: str) -> str:
    # 1) direct rare-class override by stem
    if stem in RARE_CLASS_OVERRIDES:
        return RARE_CLASS_OVERRIDES[stem]
    # 2) anomaly_type map
    if anomaly_type in TYPE_TO_CAT:
        # For rare-class fallback, further refine by stem hints
        base = TYPE_TO_CAT[anomaly_type]
        if base == "vegetation_ag":
            # rare class default; scan stem hints anyway
            for rx, cat in STEM_HINTS:
                if re.search(rx, stem, re.I):
                    return cat
        return base
    # 3) stem hints
    for rx, cat in STEM_HINTS:
        if re.search(rx, stem, re.I):
            return cat
    return "other"

def normalize_drive(url: str) -> dict:
    """Extract the file id and produce view + preview + direct-download variants."""
    if not url:
        return {}
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        return {"view": url}
    fid = m.group(1)
    return {
        "file_id":  fid,
        "view":     f"https://drive.google.com/file/d/{fid}/view",
        "preview":  f"https://drive.google.com/file/d/{fid}/preview",   # iframe-embeddable
        "download": f"https://drive.google.com/uc?export=download&id={fid}",
        "thumbnail":f"https://drive.google.com/thumbnail?id={fid}&sz=w800",
    }

def main():
    with open(SRC) as f:
        p = json.load(f)

    for s in p["scenes"]:
        cat_id = classify(s.get("stem",""), s.get("anomaly_type",""), s.get("sensor",""))
        _, label, color = CAT_ID[cat_id]
        s["category"]        = cat_id
        s["category_label"]  = label
        s["category_color"]  = color
        s["cube"]      = normalize_drive(s.get("cube_url"))
        s["gt"]        = normalize_drive(s.get("gt_url"))
        s["preview"]   = normalize_drive(s.get("preview_url"))

    # Category summary stats
    from collections import Counter
    cat_counts = Counter(s["category"] for s in p["scenes"])
    p["categories"] = [
        {"id": cid, "label": label, "color": color, "count": cat_counts.get(cid,0)}
        for (cid, label, color) in CATEGORIES
    ]
    # Coverage summary
    p["coverage"] = {
        "with_cube_link":    sum(1 for s in p["scenes"] if s.get("cube",{}).get("file_id")),
        "with_gt_link":      sum(1 for s in p["scenes"] if s.get("gt",{}).get("file_id")),
        "with_preview_link": sum(1 for s in p["scenes"] if s.get("preview",{}).get("file_id")),
        "with_thumbnail":    sum(1 for s in p["scenes"] if s.get("thumb")),
    }
    p["schema_version"] = 2

    with open(OUT, "w") as f:
        json.dump(p, f, separators=(",", ":"))

    print(f"Wrote {OUT}  ({len(p['scenes'])} scenes)")
    print("Category distribution:")
    for cid, label, color in CATEGORIES:
        print(f"  {cat_counts.get(cid,0):4d}  [{color}]  {label}")
    print("Coverage:", p["coverage"])

if __name__ == "__main__":
    main()
