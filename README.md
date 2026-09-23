# RNAseq-Analysis: aging and intervention (curcumin / Pul)

Bulk RNA-seq of mice at 2 months, 9 months (control), 9 months + curcumin, and 9 months + Pul.
Library kit: Takara SMARTer Stranded Total RNA-Seq Kit v3, Pico Input Mammalian (UMI on Read 2, reverse-stranded).
Processed with nf-core/rnaseq 3.26.0 (`star_salmon`, Apptainer) against Ensembl GRCm39 release 116.

| File | Purpose |
|---|---|
| `nextflow.config` | pipeline parameters (kit-specific UMI/strandedness settings, resources, reference) |
| `samplesheet_{Y2,O9C,O9Cur,O9Pul}.csv` | per-group nf-core samplesheets (n = 3 per group) |
| `run_group.sh <GROUP>` | runs one group end to end: nf-core/rnaseq, then Track A featureCounts |
| `backup_group.sh <GROUP>` | copies a group's results to D: and verifies every file size |
| `run_pipeline.sh` | single-samplesheet launcher (`conda activate nfcore`, nf-core/rnaseq with `-resume`) |
| `environment-r.yml` | conda env for downstream DESeq2/edgeR analysis |
| `docs/Aging_Intervention_Analysis.md` / `.pdf` | analysis plan: design, contrasts, rescue analysis, phases |
| `docs/Aging_Intervention_Analysis.docx`, `docs/build_methods_doc.py` | methods overview (Word) and the script that builds it |
| `docs/WSL2_Environment_Setup.md` | how the compute environment was built |

Raw FASTQs and results are not versioned here.
