# Aging-Intervention · 2026-09 · 2 m vs 9 m, curcumin / plumbagin

| | |
|---|---|
| **Design** | one factor with 4 levels: `Y2` (2 months) · `O9C` (9 months, control) · `O9Cur` (9 months + curcumin) · `O9Pul` (9 months + plumbagin); n = 3 each |
| **Contrasts** | aging (O9C vs Y2), each treatment vs O9C, curcumin vs plumbagin, residual distance to young, and a rescue analysis |
| **Library** | SMARTer Stranded Total RNA-Seq v3 Pico, 2×161 bp (same kit and settings as OB-OB) |
| **Plan** | [`docs/Aging_Intervention_Analysis.md`](docs/Aging_Intervention_Analysis.md) (also as PDF and Word) |

## Contents

| Path | What it is |
|---|---|
| `config/nextflow.config` | pipeline configuration (reuses the prebuilt GRCm39 e116 STAR/Salmon index) |
| `config/samplesheet_<GROUP>.csv` | one samplesheet per group |
| `scripts/run_group.sh <GROUP>` | nf-core/rnaseq, then Track A featureCounts **with `--countReadPairs`** |
| `scripts/backup_group.sh <GROUP>` | copies the group's results to D: and verifies them |
| `scripts/run_pipeline.sh <samplesheet>` | pipeline only, no counting step |
| `docs/build_methods_doc.py` | builds the Word methods overview from the lab template |

Run the scripts from this folder, e.g. `bash scripts/run_group.sh O9C`.
