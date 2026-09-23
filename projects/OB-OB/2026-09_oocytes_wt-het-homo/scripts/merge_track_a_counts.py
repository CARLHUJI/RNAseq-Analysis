#!/usr/bin/env python3
"""Merge per-sample Track A featureCounts tables into one gene x sample matrix.

Usage: merge_track_a_counts.py OUT.tsv SAMPLE=path/to/SAMPLE.gene_counts.tsv [SAMPLE=...]
Output columns: gene_id chr start end strand length <sample...> (annotation taken from the
first file; all inputs must list the same genes in the same order, which featureCounts
guarantees when run with the same GTF).

Reconstructed 2026-09-23: reproduces the archived all_samples_gene_counts.tsv byte for byte.
"""
import sys

out_path, pairs = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
handles = [open(p) for _, p in pairs]
for h in handles:
    next(h)  # "# Program:featureCounts ..." line
    next(h)  # featureCounts column header (last column is the BAM path)

with open(out_path, "w") as out:
    out.write("\t".join(["gene_id", "chr", "start", "end", "strand", "length"] + [s for s, _ in pairs]) + "\n")
    for lines in zip(*handles):
        rows = [l.rstrip("\n").split("\t") for l in lines]
        gid = rows[0][0]
        assert all(r[0] == gid for r in rows), f"gene order differs at {gid}"
        out.write("\t".join(rows[0][:6] + [r[6] for r in rows]) + "\n")
