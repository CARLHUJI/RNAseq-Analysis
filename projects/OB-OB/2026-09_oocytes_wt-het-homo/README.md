# OB-OB · 2026-09 · oocytes, wt vs het vs homo

| | |
|---|---|
| **Design** | genotype (3 levels): `wt` (wt2, wt3) · `het` (het2, het3) · `homo` (homo1–3) |
| **Library** | SMARTer Stranded Total RNA-Seq v3 Pico, 2×161 bp, about 87–144 M read pairs per sample |
| **Processing** | nf-core/rnaseq 3.26.0 (`star_salmon`), run per group; Track A featureCounts on UMI-deduplicated genome BAMs |
| **Downstream** | DESeq2 `~ genotype`; contrasts homo vs wt, het vs wt, homo vs het |
| **Full log** | [`docs/RNAseq_Analysis_Pipeline.md`](docs/RNAseq_Analysis_Pipeline.md): every decision, failure and fix |

## Contents

| Path | What it is |
|---|---|
| `config/nextflow.config` | pipeline configuration **as run** (paths refer to the original machine layout) |
| `config/samplesheet*.csv` | full and per-group samplesheets; `sample_metadata.csv` is the DESeq2 design table |
| `scripts/run_pipeline.sh`, `pause_pipeline.sh`, `resume_pipeline.sh` | launch and scheduled pause/resume helpers as run |
| `scripts/track_a_featurecounts.sh` | Track A gene counting, with the exact command recovered from the output headers |
| `scripts/merge_track_a_counts.py` | builds `all_samples_gene_counts.tsv`; verified to reproduce the archived file byte for byte |
| `analysis/Rna_seq.Rmd` | DESeq2 / QC / enrichment analysis, rebuilt from the 2026-09-16 knitted report (see the header comment) |

Data (FASTQ archive, count matrices, results) is kept on backup storage, not in git.

## Known issues

These affect how the current results should be read. Details are in the analysis log.

1. **Counts are per read, not per read pair.** Track A ran `featureCounts -p` without `--countReadPairs` (subread 2.0.6), so each read of a pair was counted separately. Assigned counts exceed the number of fragments (het2: 143.8 M assigned vs 95.6 M pairs), and about 70% of non-zero counts are even. Normalisation absorbs most of this, but p-values are somewhat too optimistic for low-count genes. **Fix:** re-count with `--countReadPairs`. The deduplicated BAMs were not kept, so this requires realignment.
2. **Samples do not separate by genotype.** PC1 (56% of variance) follows an unexplained per-sample factor, not genotype.
3. **Top homo vs wt hits are non-oocyte signal.** Collagen and stromal genes (Col1a1/1a2/3a1, Sparcl1, Mgp) and Cyp17a1 are at about 1–8 CPM, against about 400–2,400 CPM for oocyte genes (Gdf9, Bmp15, Zp3, Nobox). This is consistent with carry-over of surrounding ovarian cells.
4. **Outliers are not flagged at n = 2.** Some hits are driven by a single sample, e.g. Apol7a, which is expressed only in wt3.
5. **Inconsistent LFC shrinkage.** The report uses apeglm for the vs-wt contrasts and `normal` for homo vs het, so fold changes aren't comparable across contrasts. Use `ashr` for all three.
6. **Deferred tracks.** Track B (Salmon cross-check with mitochondrial reads filtered) and Track C (TE/L1 quantification) were deliberately postponed.

**Overall:** the data quality and oocyte purity are high. The DE gene lists are **exploratory**, suitable for hypothesis generation but not for publication without the fixes above.
