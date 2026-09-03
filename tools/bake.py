#!/usr/bin/env python3
"""Bake payload_v2.json into hsi_viz.html by replacing __PAYLOAD__ once."""
TMPL = "/tmp/claude-0/-home-user-roofflowfin/a26392d2-457b-509a-9388-0e06577eb55e/scratchpad/hsi_viz.html"
DATA = "/tmp/claude-0/-home-user-roofflowfin/a26392d2-457b-509a-9388-0e06577eb55e/scratchpad/payload_v3.json"
OUT  = "/home/user/groundtruthdatasets/index.html"

with open(TMPL) as f: html = f.read()
with open(DATA) as f: js = f.read()

assert "__PAYLOAD__" in html, "template placeholder missing"
# Escape any '</' inside the JSON to avoid closing the <script> tag prematurely.
js_safe = js.replace("</", "<\\/")
baked = html.replace("__PAYLOAD__", js_safe, 1)

with open(OUT, "w") as f: f.write(baked)

print(f"Wrote {OUT}  ({len(baked):,} bytes, payload {len(js_safe):,} bytes)")
