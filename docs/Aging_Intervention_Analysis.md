# RNA-seq Analysis Plan: Aging and Intervention (Curcumin / Plumbagin) Mouse Project

- **Status:** v0.2 (2026-09-23): inputs received (12 samples), per-group processing started
- **Owner:** Govind
- **Project dir:** `~/rnaseq-aging`
- **Archived predecessor:** OB/OB project, `D:\Govind\RNAseq_Analysis_Pipeline_OB-OB.md`
- **Status legend:** ✅ done · 🔄 in progress · ⬜ not started · ❓ open question

---

## 1. Experimental design

| Group ID | Description | Age | Treatment | Role in analysis | n (replicates) |
|---|---|---|---|---|---|
| `Y2`   | Young           | 2 months | none      | young reference baseline   | 3 (`Roni_2MR1–3`) |
| `O9C`  | Aged control    | 9 months | none / vehicle ❓ | aged reference (main comparator) | 3 (`Roni_9MR1–3`) |
| `O9Cur`| Aged + curcumin | 9 months | curcumin  | intervention 1             | 3 (`Roni_CURCAR1–3`) |
| `O9Pul`| Aged + plumbagin | 9 months | plumbagin | intervention 2            | 3 (`Roni_PLUMR1–3`) |

**Design structure.** This is a single factor with 4 levels, *not* a full 2×2 factorial. There are no treated 2-month animals, so an age × treatment interaction cannot be estimated. The statistical model is therefore `~ group` (plus any batch/sex covariates, see §1.2), and every question below is written as a specific contrast between group levels.

### 1.1 Biological questions → contrasts

| # | Question | Contrast (DESeq2) |
|---|---|---|
| C1 | What changes with age? (aging signature) | `O9C` vs `Y2` |
| C2 | What does curcumin do in aged animals? | `O9Cur` vs `O9C` |
| C3 | What does plumbagin do in aged animals? | `O9Pul` vs `O9C` |
| C4 | Do the two interventions differ? | `O9Cur` vs `O9Pul` |
| C5 | Residual distance from young after treatment | `O9Cur` vs `Y2`, `O9Pul` vs `Y2` |
| R  | **Rescue:** does treatment push age-changed genes back toward young? | derived from C1 + C2/C3 (see §7.3) |

### 1.2 Metadata to collect before any analysis ❓
- Tissue / cell type (the D: folder *"Mice Cumulus with Age"* suggests cumulus cells; **confirm**, don't assume).
- Replicates per group; what one replicate is (one animal, or a pool of animals).
- Sex, strain (C57BL/6J?), exact age at collection.
- Treatment details: dose, route, vehicle, start age, duration. Did `O9C` receive the vehicle?
- Collection date / RNA extraction batch / library prep batch / sequencing lane per sample, to build the batch covariate.
- RNA input amount and RIN/DV200 per sample, if the core provides them.

---

## 2. Carried over from the OB/OB project (same kit)

| Item | Value | Re-verify? |
|---|---|---|
| Library kit | SMARTer Stranded Total RNA-Seq Kit v3, Pico Input Mammalian (Takara) | confirm with core |
| RNA type | ribo-depleted total RNA (not poly-A) | n/a |
| UMI | Read 2, `NNNNNNNNXXXXXX` (8 nt UMI + 6 nt discard), umi_tools `string` | yes, inspect R2 |
| Strandedness | `reverse` | RSeQC infer_experiment |
| Reference | Ensembl GRCm39, release 116 (`~/data/ref/`) | kept ✅ |
| Prebuilt STAR/Salmon index | `~/data/ref/nfcore_GRCm39_e116/index/` (sjdbOverhang 160) | ✅ aging reads are 161×161 bp (checked 2026-09-23) |
| Pipeline | nf-core/rnaseq 3.26.0, `star_salmon`, Apptainer, `cache='lenient'` | kept ✅ |
| Known issue | chrMT pileup stalls transcriptome-level UMI dedup (fail-fast override in config) | expect again |
| Environment | conda env `nfcore`; downstream R env `environment-r.yml` | kept ✅ |

---

## 3. Workspace
- Project: `~/rnaseq-aging/` (config, `run_group.sh`, `backup_group.sh`, per-group samplesheets, R env, this doc).
- Reference + prebuilt STAR/Salmon index: `~/data/ref/nfcore_GRCm39_e116/`.
- Working FASTQs: `~/data/raw-aging/` · work dir: `~/nf-work/work-aging/` · outputs: `~/results-aging/<GROUP>/`.
- Final results: `D:\RONI REGGEV\RNA Seq Files\Final Results\<GROUP>\`.

## 3a. Per-group processing loop (disk-bounded)
Inputs: `D:\RONI REGGEV\RNA Seq Files` (12 samples, 182.6 GB, 161×161 bp). Order: `O9C` → `Y2` → `O9Cur` → `O9Pul`.

For each group:
1. Copy its 6 FASTQs to `~/data/raw-aging/`, md5-verify against D:.
2. `setsid nohup bash run_group.sh <GROUP> > ~/nf-work/logs/run_<GROUP>_<stamp>.log 2>&1 < /dev/null &`
   → nf-core/rnaseq with `--outdir ~/results-aging/<GROUP>`, then Track A featureCounts into `~/results-aging/<GROUP>/track_a/`.
3. `bash backup_group.sh <GROUP>` → rsync to `D:\RONI REGGEV\RNA Seq Files\Final Results\<GROUP>\`, file-by-file size check, prints `BACKUP VERIFIED`.
4. Only after `BACKUP VERIFIED`: remove `~/nf-work/work-aging`, that group's FASTQs in `~/data/raw-aging/`, and `~/results-aging/<GROUP>`.

Config changes vs OB/OB:
- `save_umi_intermeds = true`: publishes the genome-level dedup BAM (Track A input) so it survives cleanup.
- `save_reference = false`: reference already kept once in `~/data/ref/nfcore_GRCm39_e116`.
- STAR transcriptome BAM published to `star_salmon/transcriptome_bam/` via a `publishDir` override on `STAR_ALIGN` (decided 2026-09-23: keep on D: for a later Track B). O9C was launched before this rule, so it gets one extra `-resume` run after it finishes (all cached, just republishes) before backup and cleanup.
- Track A adds `--countReadPairs`: with subread 2.0.6, `-p` alone counts each mate separately (OB/OB log: "Count read pairs : no") and `-B`/`-C` only act on pair counting. **Aging counts are fragments; OB/OB Track A counts were reads — don't mix the two matrices.**

| Group | Copied+md5 | Pipeline | Track A | Backed up | Cleaned |
|---|---|---|---|---|---|
| O9C | ✅ | 🔄 (started 2026-09-23 14:54) | ⬜ | ⬜ | ⬜ |
| Y2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| O9Cur | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| O9Pul | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## 4. Phase 1: Inputs and QC of raw data ⬜
1. Copy the original FASTQs to D: (the backup) and a working copy to `~/data/raw-aging/`. Record md5sums.
2. Check read geometry (read length, which decides index reuse), per-file read counts, and the R2 UMI structure.
3. Build `samplesheet.csv` (`sample,fastq_1,fastq_2,strandedness`) with a naming scheme like `Y2_1`, `O9C_1`, `O9Cur_1`, `O9Pul_1`.
4. Build `sample_metadata.csv` with group, age, treatment, sex, batch, RIN, and input amount.

## 5. Phase 2: Upstream processing (nf-core/rnaseq) ⬜
1. Check disk space first: the OB/OB run used about 50–65 GB of BAMs per sample in `work/`. Plan chunks if needed (per-group runs, clean between them).
2. Run `star_salmon` with UMI dedup, reusing the prebuilt index if the read length matches.
3. Track A gene counts: `featureCounts -s 2 -p -B -C -g gene_id` on genome-level deduplicated BAMs (nuclear + MT).
4. Optional Track B: MT-filtered Salmon cross-check for paralog-rich genes.
5. Back up `results-aging/` to D: after each group finishes.

## 6. Phase 3: QC and exploratory analysis ⬜
- MultiQC: mapping rate, UMI duplication, rRNA/MT fraction, gene-body coverage (3′ bias, which matters for the Pico kit), strandedness, Preseq complexity.
- PCA / sample-distance heatmap on VST counts. Check whether samples separate by age and treatment and whether any batch effect appears.
- Outlier policy: decide the criteria **before** looking at DE results.

## 7. Phase 4: Differential expression ⬜
### 7.1 Model
- DESeq2, `design = ~ batch + group` (drop `batch` if there is only one), with `O9C` as the reference level.
- Pre-filter: keep genes with ≥10 counts in at least the smallest group size.
- Results via `results(contrast=...)` for C1–C5; LFC shrinkage via `ashr` (apeglm handles only coefficients, not arbitrary contrasts).
- Thresholds: padj < 0.05; report |log2FC| cutoffs used for plots separately from significance.

### 7.2 Outputs per contrast
- Full DE table (Ensembl ID, symbol, biotype, baseMean, LFC, shrunk LFC, padj), plus MA and volcano plots and a heatmap of top genes.

### 7.3 Rescue analysis (R)
- Aging signature = significant genes in C1 (`O9C` vs `Y2`).
- For each treatment, classify each aging gene as:
  - **rescued:** significant in C2/C3 in the direction opposite to C1;
  - **partially rescued:** opposite direction but not significant;
  - **unchanged**;
  - **exacerbated:** same direction as C1.
- Rescue scatter: LFC(C1) vs LFC(C2 or C3), with the slope/correlation reported.
- Compare curcumin vs Pul rescue sets (overlap, UpSet plot).

## 8. Phase 5: Functional interpretation ⬜
- GSEA (fgsea / clusterProfiler) on shrunk-LFC-ranked genes: GO BP, KEGG/Reactome, MSigDB Hallmark.
- Focused gene sets: senescence/SASP, inflammation/NF-κB, oxidative stress/Nrf2 (a curcumin-relevant axis), mitochondrial/OXPHOS, and heterochromatin/epigenetic regulators (matching the lab's γH2AX / H3K9me2 / H3K27me3 / L1 ORF imaging sets).
- Separate optional TE/L1 track (TEtranscripts/TElocal, permissive multimapping realignment), as planned for OB/OB. Asks whether aging derepresses L1 and whether the treatments reverse it.

## 9. Phase 6: Reporting and reproducibility ⬜
- R Markdown report per contrast; record all versions (pipeline, containers, R session).
- State replicate numbers and their power limitations wherever results are shown.
- Back up everything final to `D:\Govind\` under a new project folder.

---

## 10. Open questions / decisions log
| Date | Item | Decision |
|---|---|---|
| 2026-09-23 | Model structure | single factor `group` (4 levels), contrasts C1–C5 + rescue |
| 2026-09-23 | Reference / pipeline | reuse GRCm39 e116 + nf-core/rnaseq 3.26.0 from OB/OB |
| 2026-09-23 | What is "Pul"? | plumbagin |
| 2026-09-23 | n per group | 3 per group, 12 total |
| ❓ | Tissue, sex, batches | |
| 2026-09-23 | Read length (index reuse) | 161×161 bp → reuse OB/OB index |
