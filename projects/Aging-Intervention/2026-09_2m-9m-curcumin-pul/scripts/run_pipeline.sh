#!/usr/bin/env bash
# Launch nf-core/rnaseq on one samplesheet for the aging/curcumin/Pul project (no Track A step).
# Usage: scripts/run_pipeline.sh <samplesheet.csv in config/>   e.g. scripts/run_pipeline.sh samplesheet_Y2.csv
# For the normal per-group run (pipeline + Track A counts) use scripts/run_group.sh. See ../docs/Aging_Intervention_Analysis.md.
set -euo pipefail

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate nfcore

SHEET="${1:?usage: run_pipeline.sh <samplesheet.csv>}"
cd "$(dirname "${BASH_SOURCE[0]}")/../config"

nextflow run nf-core/rnaseq -r 3.26.0 \
    -profile apptainer \
    -c nextflow.config \
    --input "$SHEET" \
    -resume
