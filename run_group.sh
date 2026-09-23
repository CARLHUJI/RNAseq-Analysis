#!/usr/bin/env bash
# Run one group end to end: nf-core/rnaseq, then Track A featureCounts.
# Usage: run_group.sh <GROUP>   (GROUP = Y2 | O9C | O9Cur | O9Pul; reads samplesheet_<GROUP>.csv)
# Launch detached:  setsid nohup bash run_group.sh O9C > ~/nf-work/logs/run_O9C_$(date +%Y%m%d_%H%M%S).log 2>&1 < /dev/null &
# See docs/Aging_Intervention_Analysis.md.
set -euo pipefail

GROUP="$1"
cd "$(dirname "${BASH_SOURCE[0]}")"
[ -f "samplesheet_${GROUP}.csv" ] || { echo "no samplesheet_${GROUP}.csv"; exit 1; }

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate nfcore

OUTDIR="$HOME/results-aging/${GROUP}"
stamp() { date +"%Y-%m-%d %H:%M:%S %Z"; }

echo "=== $(stamp) : nf-core/rnaseq ${GROUP} ==="
nextflow run nf-core/rnaseq -r 3.26.0 \
    -profile apptainer \
    -c nextflow.config \
    --input "samplesheet_${GROUP}.csv" \
    --outdir "$OUTDIR" \
    -resume

# Track A: unique-read gene counts on the genome-level UMI-deduplicated BAM (nuclear + MT).
# Same settings as OB/OB Track A, plus --countReadPairs: in subread 2.0.6, -p alone counts each
# mate separately (OB/OB log showed "Count read pairs : no") and -B/-C only apply to pair counting.
echo "=== $(stamp) : Track A featureCounts ${GROUP} ==="
SUBREAD_IMG="$HOME/nf-work/apptainer-cache/quay.io-biocontainers-subread-2.0.6--he4a0461_2.img"
GTF="$HOME/data/ref/nfcore_GRCm39_e116/Mus_musculus.GRCm39.116.filtered.gtf"
TA="$OUTDIR/track_a"
mkdir -p "$TA"
for bam in "$OUTDIR"/star_salmon/*.umi_dedup.sorted.bam; do
    s=$(basename "$bam" .umi_dedup.sorted.bam)
    echo "--- $(stamp) : ${s}"
    apptainer exec -B "$HOME" "$SUBREAD_IMG" featureCounts \
        -T 12 -s 2 -p --countReadPairs -B -C -g gene_id \
        -a "$GTF" -o "$TA/${s}.gene_counts.tsv" "$bam"
done
echo "=== $(stamp) : ${GROUP} done ==="
