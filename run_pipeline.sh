#!/usr/bin/env bash
# Launch nf-core/rnaseq for the aging/curcumin/Pul mouse project. See docs/Aging_Intervention_Analysis.md.
set -euo pipefail

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate nfcore

cd "$(dirname "${BASH_SOURCE[0]}")"

nextflow run nf-core/rnaseq -r 3.26.0 \
    -profile apptainer \
    -c nextflow.config \
    --input samplesheet.csv \
    -resume
