# StatsBomb_value_actions


# StatsBomb Value Actions & Possession Explorer

A lightweight pipeline and notebook suite to:
- clean and compact StatsBomb-style event data,
- build *possession-level* datasets,
- visualize sequences/possessions on a pitch,
- and prototype value-added / xG-style modeling.

> **Why?** To go from raw events → analysis-ready tables → clear visuals → first-pass models, fast.

---

## 🚀 Quick Start

### 1 Environment
```bash
# Recommended: conda or venv
conda create -n soccer_data python=3.10 -y
conda activate soccer_data

# Core deps
pip install pandas numpy matplotlib mplsoccer scikit-learn lightgbm shap tqdm jupyter
```

### 2 Files in this repo
.
├─ Soccer_data.ipynb            # Pull/clean + build compact event tables
├─ Soccer_data_verify.ipynb     # Sanity checks: schema, nulls, dedupes, possession alignment
├─ Soccer_modeling.ipynb        # Feature engineering + prototype models (value/xG)
├─ events_compact.csv           # Compact event table (core columns only)
├─ possessions.csv              # Possession-level table
└─ sequence.json                # Small demo clip for rendering a sequence on a pitch
```

> If you prefer a `requirements.txt`, generate one with:  
> `pip freeze > requirements.txt`

---

## 📦 Data Artifacts

### `events_compact.csv`
- One row per **event** with core columns like: `minute, second, team, player, x, y, end_x, end_y, event, xg`.  
- Designed to be light enough for plotting and quick joins.

### `possessions.csv`
- One row per **possession** with identifiers, start/end info, and summarized features (progress, carries, passes, shots, etc.).

### `sequence.json`
- A tiny example sequence (pass → carry → shot, etc.) used for quick visualization demos in the notebooks.


## 📒 Notebooks (run in this order)

1. **`Soccer_data.ipynb`**
   - Loads raw/JSON events (or your own feed).
   - Cleans & flattens columns, standardizes coordinates (0–120 x 0–80), and exports `events_compact.csv`.

2. **`Soccer_data_verify.ipynb`**
   - Validates schema, checks nulls/dupes, and verifies possession stitching.
   - Produces `possessions.csv` with possession-level aggregates.

3. **`Soccer_modeling.ipynb`**
   - Feature engineering (progress, carries, pressures, last-action context, etc.).
   - First-pass models (e.g., possession value/xG, classification or regression) using `scikit-learn`/`lightgbm`.
   - Optional explainability with `shap`.

> Tip: If you’re using custom competitions or seasons, parameterize the “ingest” cell at the top of `Soccer_data.ipynb`.

## 🖼️ Example: Render a Sequence on a Pitch

The snippet below shows how to replay **`sequence.json`** on a pitch with `mplsoccer`. Tweak markers/arrows to your style.

```python
import json, pandas as pd, matplotlib.pyplot as plt
from mplsoccer import Pitch

# Load the demo sequence
with open("sequence.json", "r") as f:
    seq = json.load(f)
df = pd.DataFrame(seq)

# Basic pitch
pitch = Pitch(pitch_type="statsbomb", pitch_length=120, pitch_width=80, line_zorder=2)
fig, ax = pitch.draw(figsize=(10, 7))

# Draw passes/carries/shots
for _, r in df.iterrows():
    kind = str(r["event"]).lower()
    if kind in ["pass", "carry"]:
        pitch.arrows(r["x"], r["y"], r["end_x"], r["end_y"], ax=ax, width=1, headwidth=6, zorder=3)
    elif kind == "shot":
        pitch.scatter(r["x"], r["y"], s=60, ax=ax, zorder=4)
        ax.text(r["x"], r["y"]+2, f"xG={r.get('xg', 0):.3f}", ha="center")

ax.set_title("Demo Sequence Replay", fontsize=14)
plt.show()
```

## 🧠 Modeling Notes

- **Targets:** start simple (e.g., shot vs. no shot), then try possession value (EPV-like) or xG-on-possession.  
- **Features:** progress, last action, carry distance, pressure counts, entry zones, team possession %, rolling player form, etc.  
- **Imbalance:** use class weights / threshold tuning; track precision–recall, not just accuracy.  
- **Explainability:** `shap` can highlight which features move predictions up/down.

---

## 🗺️ Roadmap

- Rolling & opponent-context features (recent xG for/against, field tilt).
- Spatial enrichments (zones, thirds, pressure heat, Voronoi/nearest-defender if available).
- Better visualization layers (event glyphs, outcomes, highlights).
- Packaging helpers into functions/py modules for reuse.

---

## 🤝 Contributing

PRs & issues welcome! If you add datasets or models, include:
- short description, schema, and license,
- a minimal repro cell or script,
- a small PNG of any new visual (optional).

---

## 📜 License & Data

- **Code:** MIT (or your preferred OSS license—update this line if you choose another).  
- **Data:** Respect the terms of your data provider (e.g., StatsBomb Open Data). Do not redistribute data files without permission.

**Acknowledgments:** Massive thanks to the open-source soccer analytics community, including `mplsoccer` and StatsBomb Open Data.
