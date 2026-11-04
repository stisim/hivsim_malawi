# hivsim_malawi

Calibration of HIVsim (STIsim on Starsim v4) to Malawi. A finalized parameter set from here is copied into [hivsim_paper](https://github.com/stisim/hivsim_paper) (`models/hivsim/reference/`), where it's one of the reference models compared with EMOD-HIV and Optima HIV.

| Folder | What it holds |
|---|---|
| `hivsim/` | The Malawi model (`malawi.py`), its data (`data/`), the scripts that make the data and targets, and `targetfit.py`, which scores runs against the targets and plots them |
| `experiments/NN_slug/` | Calibration experiments: README before running, SUMMARY after, `run.py`, `config.yaml`, outputs and figures |
| `results/targets.csv` | Calibration targets, made by `hivsim/make_targets.py` (described in `docs/targets.md`) |
| `envs/starsim.yml` | Conda environment |

Moved from hivsim_paper with its git history on 3 Nov 2026. The same targets are used in hivsim_paper to compare all three models, so a change to `results/targets.csv` here should be copied there.

```bash
conda env create -f envs/starsim.yml
python experiments/03_testing_art/run.py
```
