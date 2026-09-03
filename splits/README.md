# splits/

Canonical **train / val / test / pretrain** membership for every scene,
one CSV per split. These are the assignments the dashboard shows in
each scene's detail pane and the ones a data scientist should use to
reproduce a paper-comparable model.

| File | Rows | What's in it |
|---|---:|---|
| `pretrain.csv` | 522 | Clean-background AVIRIS-NG tiles for self-supervised pretraining. No labels. |
| `train.csv`    | 103 | Labeled anomaly scenes used to fit a supervised or fine-tuning model. |
| `val.csv`      |  16 | Held-out labeled scenes for hyperparameter tuning. |
| `test.csv`     |  14 | Held-out labeled scenes for final reported metrics. Never use for tuning. |

Columns in every CSV:

```
stem, sensor, sensor_family, tier, category, category_label,
anomaly_type, bands, height, width, anomaly_px, anomaly_pct,
cube_url, gt_url, preview_url
```

## How the split was made

- **Pretrain** — all `Clean background (pretrain)` scenes (AVIRIS-NG L1
  radiance tiles) go here. Never used for evaluation.
- **Train / Val / Test** — labeled scenes are stratified by sensor family
  and anomaly category, then randomly assigned 80 / 10 / 10.

## How to regenerate

```bash
python tools/augment_payload.py   # writes payload_v2.json
# then a one-liner iterates payload['scenes'] into splits/{split}.csv
```

See the top-level README for the full regeneration pipeline.
