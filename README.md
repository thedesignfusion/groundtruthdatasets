# Ground Truth Datasets

Hyperspectral dataset explorer — interactive dashboard for browsing
655 scenes across 8 sensor families (AVIRIS, PRISMA, EnMAP, HYDICE,
ROSIS, WHU-Hi Nano-Hyperspec, Houston, Synthetic).

Single self-contained HTML file — all metadata, thumbnails, and Google
Drive links baked in. Deployed as a static site on Vercel.

To update: regenerate `dataset_full_payload.json` via the Colab audit
notebook, re-bake into a new `index.html`, and commit.
