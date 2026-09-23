#!/usr/bin/env bash
# ARCHIVED AS RUN: paths refer to the original ~/rnaseq-obob layout (config files were beside this script).
# Launch nf-core/rnaseq for the OB/OB mouse project. See docs/RNAseq_Analysis_Pipeline.md.
set -euo pipefail

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate nfcore

cd "$(dirname "${BASH_SOURCE[0]}")"

nextflow run nf-core/rnaseq -r 3.26.0 \
    -profile apptainer \
    -c nextflow.config \
    --input samplesheet.csv \
    -resume
