#!/usr/bin/env bash
# Track A gene counts for OB/OB: featureCounts on the genome-level UMI-deduplicated BAMs.
# Recorded AS RUN (Sep 2026). The command line below is copied from the "# Program:featureCounts"
# header of every archived *.gene_counts.tsv; the loop/log format matches ~/nf-work/logs/track_a_*.log.
#
# KNOWN ISSUE: no --countReadPairs. In subread >= 2.0.2, -p only declares paired-end data; each
# mate was counted separately (log: "Count read pairs : no"), so counts are per read, ~1.5x the
# number of fragments, and -B/-C had no effect. See ../README.md "Known issues".
# Do not reuse this for new experiments; use shared/templates/run_group.sh (has --countReadPairs).
#
# Usage: track_a_featurecounts.sh <sample.umi_dedup.sorted.bam>...
set -uo pipefail

SUBREAD_IMG="$HOME/nf-work/apptainer-cache/quay.io-biocontainers-subread-2.0.6--he4a0461_2.img"
GTF="$HOME/results/genome/Mus_musculus.GRCm39.116.filtered.gtf"

for bam in "$@"; do
    s=$(basename "$bam" .umi_dedup.sorted.bam)
    echo "=== $(date) : starting featureCounts for ${s} ==="
    apptainer exec -B "$HOME" "$SUBREAD_IMG" featureCounts \
        -B -C -p -s 2 -T 8 -t exon -g gene_id \
        -a "$GTF" -o "${s}.gene_counts.tsv" "$bam"
    echo "=== $(date) : finished ${s}, exit=$? ==="
done

# Then merge (sample order as archived):
#   merge_track_a_counts.py all_samples_gene_counts.tsv het2=het2.gene_counts.tsv het3=... wt2=... wt3=... homo1=... homo2=... homo3=...
