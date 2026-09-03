# Contributing

Small, focused changes are best. Anyone with a GitHub account can open a
pull request; a maintainer at [The Design Fusion](https://thedesignfusion.co)
reviews and merges.

---

## What lives where

| Folder / file | What it is | How to change it |
|---|---|---|
| `index.html`        | The self-contained dashboard | Regenerate via `tools/bake.py`, don't hand-edit |
| `tools/`            | Python scripts that build the dashboard | Edit directly, PR the change |
| `notebook_labeled_overlays_colab.ipynb` | Colab notebook that produces paper-GT overlays | Edit directly, PR the change |
| `masks/`            | Ground-truth label masks (LFS) | Add a `<stem>_gt.<ext>` file |
| `previews/`         | RGB preview JPEGs (LFS) | Add a `<stem>_rgb.jpg` file |
| `splits/*.csv`      | Train / val / test / pretrain membership | Edit the CSV directly |
| `README.md`         | Project docs | Edit directly |

`masks/` and `previews/` use **Git LFS** — install it once with
`git lfs install` before your first push.

---

## Common changes

### Fix a label on one scene

1. Open the dashboard and note the scene's exact `stem` (e.g. `abu-airport-1`).
2. Drop the corrected mask into `masks/<stem>_gt.mat` (or `.tif` / `.png`).
3. In Colab, run `notebook_labeled_overlays_colab.ipynb` — it picks up
   the new mask and rebuilds the overlay for that scene.
4. Commit the download `payload_v4_labeled.json` back as
   `tools/payload_v3.json`, then run `python tools/bake.py`.
5. PR the change: the updated mask, the updated `index.html`.

### Add a new scene to the corpus

1. Drop the cube, the GT mask, and an RGB preview into the shared Drive
   folder — the audit notebook picks it up on the next run.
2. Re-run `notebook_dataset_audit_colab.ipynb` to regenerate
   `dataset_full_payload.json`.
3. Run `tools/augment_payload.py` → `tools/generate_overlays.py` →
   `tools/bake.py`.
4. PR the resulting `index.html`.

### Move a scene between splits

Edit the CSV directly in `splits/`. Then rebuild the payload's `split`
field from the CSV and rebake. Keep splits stratified by sensor family
and anomaly category so evaluation stays comparable to published papers.

### Change how a category is defined

`tools/augment_payload.py` — the `CATEGORIES`, `STEM_HINTS`, and
`RARE_CLASS_OVERRIDES` tables at the top of the file are the source of
truth for the taxonomy. Editing those and re-running the pipeline
propagates the change through the dashboard.

---

## Pull-request checklist

- [ ] The change is scoped to one thing (a mask, a preview, a fix, a doc)
- [ ] `index.html` is regenerated from the tools/notebook, not hand-edited
- [ ] LFS is installed if you touched `masks/` or `previews/`
- [ ] The description says WHAT the change is and WHY it matters

---

## Licensing

Code in this repo: MIT. Ground-truth masks in `masks/` retain the
license of their originating paper — cite the paper (linked in each
scene's detail pane) when you use its labels in your own work.
