# masks/

Ground-truth **label masks** for the scenes in the corpus. One file per
scene, named `<stem>_gt.<ext>`. These are the pixel-level truth that the
dashboard's "Labeled overlay" renders.

## What lives here

For each scene, whichever of these formats the source paper published:

- `<stem>_gt.mat`   — MATLAB v5 / v7 / v7.3 integer label map (0 = background)
- `<stem>_gt.tif`   — GeoTIFF label map
- `<stem>_gt.png`   — PNG single-band label map (0-255)
- `<stem>_gt.npy`   — NumPy array

All go through Git LFS (see `.gitattributes`) so the repo stays clone-able.

## How to add a new mask

1. Drop the file into this folder using the exact scene stem shown in the
   dashboard (e.g. `abu-airport-1_gt.mat`, `PaviaU_gt.tif`).
2. Commit and push — Git LFS handles the upload.
3. Run the labeled-overlay Colab notebook so the new mask flows into the
   dashboard's Labeled view.
4. Bake and push the updated `index.html`.

## Where the current masks came from

The 23 masks the dashboard already links to were published by the source
papers listed in the top-level README. Everything in this folder retains
the license of its originating paper — cite the paper, not this repo,
when you use the mask in your own work.
