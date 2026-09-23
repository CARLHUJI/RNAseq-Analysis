"""Build the aging RNA-seq methods overview .docx on top of the Haile template package
(same styles, fonts, page setup, table look), replacing only word/document.xml."""
import re, sys, zipfile
from xml.sax.saxutils import escape

TPL = "/mnt/c/Users/govindp/Downloads/RNAseq_methods_Haile.docx"
OUT = sys.argv[1]

src = zipfile.ZipFile(TPL)
doc = src.read("word/document.xml").decode()
head = doc[: doc.index("<w:body>")]
sect = re.search(r"<w:sectPr.*?</w:sectPr>", doc, re.S).group(0)

A = '<w:rFonts w:cs="Arial"/>'


def run(text, bold=False, hl=None):
    rpr = A + ("<w:b/><w:bCs/>" if bold else "") + (f'<w:highlight w:val="{hl}"/>' if hl else "")
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def para(*segs, bold=False, hl=None, indent=False):
    """segs: plain strings, or (text, bold) tuples for mixed runs."""
    ind = '<w:ind w:left="360"/>' if indent else ""
    ppr = f"<w:pPr>{ind}<w:rPr>{A}</w:rPr></w:pPr>"
    runs = "".join(run(s, bold, hl) if isinstance(s, str) else run(s[0], s[1], hl) for s in segs)
    return f"<w:p>{ppr}{runs}</w:p>"


def blank():
    return f"<w:p><w:pPr><w:rPr>{A}</w:rPr></w:pPr></w:p>"


def heading(t):
    return para(t, bold=True)


def table(rows):
    def cell(t, bold):
        return ('<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/><w:shd w:val="clear" w:color="auto" w:fill="auto"/></w:tcPr>'
                + para((t, bold)) + "</w:tc>")
    tr = "".join(
        '<w:tr><w:trPr><w:trHeight w:val="432"/><w:tblCellSpacing w:w="21" w:type="dxa"/></w:trPr>'
        + cell(k, True) + cell(v, False) + "</w:tr>" for k, v in rows)
    return ('<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblCellSpacing w:w="21" w:type="dxa"/>'
            '<w:tblCellMar><w:left w:w="43" w:type="dxa"/><w:right w:w="43" w:type="dxa"/></w:tblCellMar>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="2856"/><w:gridCol w:w="7116"/></w:tblGrid>' + tr + "</w:tbl>")


B = []  # body parts
add = B.append

add(para("ANALYSIS IN PROGRESS (status: 23 September 2026). Upstream processing is running one group at a time. "
         "Sections marked [PLANNED] describe the intended analysis and will be updated with final parameters, "
         "versions and results. THIS FILE SHOULD NOT BE USED FOR PUBLICATION AS IS.", bold=True, hl="green"))
add(blank())

add(heading("Project"))
add(para("RNA-seq of mouse samples from an aging and intervention study (data: Roni Reggev). Four groups, three biological "
         "replicates each (12 samples): 2-month-old mice, 9-month-old control mice, 9-month-old mice treated with curcumin, "
         "and 9-month-old mice treated with plumbagin. Libraries were sequenced paired-end, 2 × 161 bp. Library preparation: "
         "SMARTer Stranded Total RNA-Seq Kit v3 – Pico Input Mammalian (Takara), i.e. ribosomal-RNA-depleted total RNA with "
         "unique molecular identifiers (UMIs) on Read 2 (the same kit as the lab's previous OB/OB project; to be confirmed with "
         "the sequencing core)."))
add(blank())

add(heading("Processing overview"))
add(para("All samples are processed with the community-standard nf-core/rnaseq pipeline (release 3.26.0, run with Nextflow "
         "and Apptainer containers), with identical settings for every group. To limit disk use, the four groups are processed "
         "one after another; after each group, its final results are copied to D:\\RONI REGGEV\\RNA Seq Files\\Final Results\\<group> "
         "and verified before temporary files are removed. Processing groups separately does not introduce a batch effect, "
         "because software, reference and parameters are the same for all samples. Differential expression is then run once, "
         "on all 12 samples together."))
add(blank())

add(heading("Trimming and filtering of raw reads"))
add(para("Raw reads (fastq files) were inspected for quality issues with FastQC. The 8-nt UMI at the start of Read 2 was moved "
         "into the read name with UMI-tools extract, and the following 6 nt (3-nt UMI linker + 3 nt from the Pico v3 SMART UMI "
         "adapter) were removed, as recommended by the kit manufacturer. Reads were then trimmed with Trim Galore (a wrapper around "
         "cutadapt) using default settings: bases with quality below 20 were trimmed from the 3' end, Illumina adapter sequences "
         "were removed, and read pairs in which either read became shorter than 20 nt were discarded. Samples keeping fewer than "
         "10,000 reads after trimming would be excluded from downstream steps."))
add(blank())

add(heading("Alignment and counting"))
add(para("The processed reads were aligned to the Mouse genome with STAR aligner. The reference genome version was GRCm39 "
         "(primary assembly), with annotations from Ensembl release 116. The STAR index was built with a splice-junction overhang "
         "of 160 (read length − 1). PCR duplicates were removed with UMI-tools dedup on the genome alignments: read pairs with the "
         "same mapping position and the same UMI are counted once, so remaining counts reflect original RNA molecules rather than "
         "PCR copies."))
add(para("Gene-level counts (\"Track A\") were produced with featureCounts (Subread package) on the deduplicated alignments, "
         "at the Ensembl gene_id level, with strand information set to 'reverse'. Read pairs are counted as one fragment; only "
         "pairs with both reads aligned are counted, chimeric pairs are excluded, and reads mapping to more than one location or "
         "overlapping more than one gene are not counted. Nuclear and mitochondrial genes are counted together. Because "
         "multi-mapping reads are discarded, genes with close paralogs or pseudogenes may be under-counted; this should be kept "
         "in mind when interpreting such genes."))
add(para("In addition, transcript abundances were estimated with Salmon (pseudo-alignment mode) as an independent, "
         "methodologically different cross-check. The pipeline's default gene-count route (Salmon on STAR transcriptome "
         "alignments) is replaced by the three quantification tracks described below."))
add(blank())

add(heading("Quantification strategy: Tracks A, B and C"))
add(para("Why three tracks. Two separate issues shape how reads are turned into numbers in this project. The first is technical. "
         "This kit captures total RNA after ribosomal-RNA depletion, and depletion is never complete, so a very large number of "
         "reads land on the small (16.3 kb) mitochondrial genome. In the lab's previous project with the same kit, mitochondrial "
         "read density was 1,300–2,000 times the genome average. UMI deduplication slows down much faster than linearly when "
         "that many reads pile up at the same positions. As a result, the pipeline's standard gene-count route (UMI "
         "deduplication on transcript alignments, then Salmon) could not finish, even when given 48 hours per sample. "
         "Deduplication on genome alignments is not affected, because it only processes each read's primary alignment. The "
         "second issue is biological. Measuring gene expression and measuring transposable elements (repeats such as L1) are "
         "different questions, and they need opposite handling of reads that match several places in the genome. Each track "
         "therefore answers one question in the way that suits it."))
add(blank())
add(para(("Track A: primary gene counts (used for differential expression; runs for every group now). ", True),
         "What: featureCounts gene counts from the UMI-deduplicated genome alignments, as described above. Why: it uses the "
         "route that is not affected by the mitochondrial pile-up, it produces nuclear and mitochondrial gene counts together "
         "in one table, and it is fast and standard. Limitation: reads that match more than one location are discarded, not "
         "shared out. Genes with close paralogs, gene families or pseudogenes can therefore be under-counted, and this caveat is "
         "stated wherever Track A results are shown."))
add(blank())
add(para(("Track B: Salmon cross-check, nuclear genes only (optional; not yet scheduled). ", True),
         "What: the 37 mitochondrial transcripts are removed from the STAR transcriptome alignments; UMI deduplication and "
         "Salmon quantification (alignment mode) are then run with the same arguments the pipeline would use. Why: removing "
         "the mitochondrial pile-up lets deduplication finish. Salmon then shares reads that match several genes or isoforms "
         "between them statistically instead of discarding them, which covers exactly the genes where Track A is weakest. "
         "Use: a cross-check for genes of interest that belong to gene families, not a replacement for Track A. Track B has "
         "no mitochondrial counts by design; those always come from Track A. Its run time is long and hard to predict. "
         "The STAR transcriptome alignments that Track B needs are kept for every sample "
         "(star_salmon/transcriptome_bam), so Track B can be run later without realigning."))
add(blank())
add(para(("Track C: transposable elements / L1 (planned; after Track A is complete for all groups). ", True),
         "What: a separate STAR realignment that allows reads to match many locations (up to about 100), followed by "
         "TEtranscripts (repeat-family level) and TElocal (individual-locus level), using a RepeatMasker repeat annotation for "
         "GRCm39, with its own normalization. Why: this asks a different biological question, namely whether aging loosens "
         "heterochromatin and reactivates young, potentially active L1 subfamilies (L1Md_A, L1Md_T, L1Md_Gf), and whether "
         "curcumin or plumbagin reverses this. It complements the lab's γH2AX, H3K9me2, H3K27me3 and L1 ORF imaging. Copies of "
         "these repeats are nearly identical, so their reads match many places; the standard alignment used for Tracks A and B "
         "discards exactly those reads, which is why a separate realignment is needed rather than a setting change. The "
         "total-RNA kit helps here, because many repeat transcripts are not polyadenylated and would be missed by poly-A "
         "selection. Because low-input libraries can produce artifacts that look like repeat signal, 3' bias, internal priming "
         "and PCR duplication will be checked before any L1 result is reported. Track C starts again from the raw fastq files "
         "kept on D:, so it does not depend on any temporary files."))
add(blank())

add(heading("Quality control"))
add(para("Quality control is reported per sample and summarised in one MultiQC report per group. It includes: read quality "
         "(FastQC), alignment statistics (STAR, SAMtools), UMI deduplication rates (UMI-tools), strandedness, read distribution "
         "and gene-body coverage for 3'/5' bias (RSeQC), RNA-seq QC (Qualimap), library complexity (Preseq), duplication versus "
         "expression (dupRadar), and ribosomal/mitochondrial content via biotype counts. No reads are removed in silico for rRNA; "
         "depletion efficiency is monitored in the QC instead."))
add(blank())

add(heading("Differential expression [PLANNED]"))
add(para("Normalization and differential expression analysis will be performed with the DESeq2 package on the Track A counts "
         "of all 12 samples together. The model is a single factor with four levels (design ~ group, plus a batch term if "
         "sample-collection or library batches are identified), with the 9-month control group (O9C) as the reference level. "
         "This is not a full 2 × 2 design: there are no treated 2-month animals, so an age × treatment interaction cannot be "
         "estimated, and each question is tested as a specific contrast (see Comparisons). Genes with at least 10 counts in at "
         "least 3 samples will be kept. Variance-stabilized (VST) counts will be used for quality control plots such as sample-"
         "distance heatmaps and principal component analysis. Criteria for excluding outlier samples will be fixed before looking "
         "at differential expression results. Log2 fold changes will be shrunk with the ashr method, and genes with an adjusted "
         "p-value (Benjamini–Hochberg) below 0.05 will be called significant; any fold-change cut-off used for plots will be "
         "reported separately. With n = 3 per group, statistical power is limited, and this will be stated wherever results are shown."))
add(para("Rescue analysis: genes changed with age (O9C vs Y2) will be classified for each treatment as rescued (significant change "
         "in the opposite direction), partially rescued (opposite direction, not significant), unchanged, or exacerbated (same "
         "direction as aging). Pathway analysis will use gene set enrichment (fgsea / clusterProfiler) on GO Biological Process, "
         "KEGG/Reactome and MSigDB Hallmark gene sets, with focused sets for senescence/SASP, inflammation, oxidative stress/Nrf2, "
         "mitochondrial/OXPHOS and heterochromatin/epigenetic regulators."))
add(blank())

add(heading("Abbreviations:"))
for code, desc, files in [
    ("Y2", "Young mice, 2 months old, untreated", "Roni_2MR1–3 (S40–S42)"),
    ("O9C", "Aged mice, 9 months old, control", "Roni_9MR1–3 (S43–S45)"),
    ("O9Cur", "Aged mice, 9 months old, treated with curcumin", "Roni_CURCAR1–3 (S46–S48)"),
    ("O9Pul", "Aged mice, 9 months old, treated with plumbagin", "Roni_PLUMR1–3 (S49–S51)"),
]:
    add(para((f"{code}: ", True), f"{desc}. Samples {code}_1–3 = raw files {files}."))
add(para(("UMI: ", True), "unique molecular identifier; ", ("Track A / B / C: ", True), "primary gene counts / Salmon "
         "cross-check / transposable elements (see Quantification strategy); ", ("padj: ", True), "Benjamini–Hochberg adjusted p-value; ", ("LFC: ", True), "log2 fold change."))
add(blank())

add(heading("Comparisons:"))
for c, t, q in [
    ("C1_Aging", "O9C vs. Y2", "what changes with age"),
    ("C2_Curcumin", "O9Cur vs. O9C", "effect of curcumin in aged mice"),
    ("C3_Plumbagin", "O9Pul vs. O9C", "effect of plumbagin in aged mice"),
    ("C4_CurVsPlum", "O9Cur vs. O9Pul", "difference between the two treatments"),
    ("C5_Cur_Young / C5_Plum_Young", "O9Cur vs. Y2 and O9Pul vs. Y2", "remaining distance from young after treatment"),
    ("Rescue", "derived from C1 together with C2 / C3", "does treatment move age-changed genes back toward young levels"),
]:
    add(para((f"{c} = ", True), f"{t} ({q})"))
add(blank())

add(heading("Result files and naming conventions:"))
add(para("Final results for each group are stored in D:\\RONI REGGEV\\RNA Seq Files\\Final Results\\<group> (Y2, O9C, O9Cur, O9Pul):"))
for item in [
    "track_a/<sample>.gene_counts.tsv = Track A gene counts (the input for differential expression); .summary = how many read pairs were assigned or why they were not.",
    "star_salmon/<sample>.umi_dedup.sorted.bam (+ .bai) = deduplicated genome alignments, viewable in IGV.",
    "star_salmon/bigwig = strand-specific coverage tracks for genome browsers.",
    "star_salmon/transcriptome_bam/<sample>.Aligned.toTranscriptome.out.bam = STAR alignments to transcripts (input for Track B; not deduplicated).",
    "star_salmon/rseqc, qualimap, preseq, dupradar, samtools_stats = per-sample QC outputs.",
    "salmon = Salmon pseudo-alignment quantification (cross-check).",
    "multiqc = one combined, interactive QC report per group (multiqc_report.html); the easiest place to start.",
    "fastqc, trimgalore, umitools = read-level QC, trimming and UMI logs.",
    "pipeline_info = exact software versions and run parameters.",
    "samplesheet_<group>.csv = mapping of sample names to raw fastq files.",
]:
    add(para("• " + item, indent=True))
add(para("[PLANNED] Differential expression outputs will be provided per comparison: a full results table (Ensembl ID, gene "
         "symbol, biotype, baseMean, LFC, shrunk LFC, p-value, padj, raw and normalized counts), MA and volcano plots (grey = "
         "non-significant, red = significant genes), and heatmaps of significant genes. File-naming conventions for plots will be "
         "added here when those files are produced."))
add(blank())

add(heading("Missing values:"))
add(para("In DESeq2 results, a gene can get 'NA' values: if both pvalue and padj are NA, the gene has a sample with an extreme count "
         "compared with the other samples (a Cook's distance outlier) and was not tested; if only padj is NA, the gene was removed "
         "by DESeq2's independent filtering because its expression was too low to reach significance; genes with zero counts in "
         "all samples have NA in all statistics columns. Genes removed by the pre-filter (see above) have raw counts but no "
         "normalized counts or statistics."))
add(blank())

add(heading("Citations"))
for name, ref in [
    ("nf-core", "Ewels PA, Peltzer A, Fillinger S, Patel H, Alneberg J, Wilm A, Garcia MU, Di Tommaso P, Nahnsen S. The nf-core framework for community-curated bioinformatics pipelines. Nat Biotechnol. 2020;38(3):276-278. doi:10.1038/s41587-020-0439-x"),
    ("Nextflow", "Di Tommaso P, Chatzou M, Floden EW, Barja PP, Palumbo E, Notredame C. Nextflow enables reproducible computational workflows. Nat Biotechnol. 2017;35(4):316-319. doi:10.1038/nbt.3820"),
    ("UMI-tools", "Smith T, Heger A, Sudbery I. UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy. Genome Res. 2017;27(3):491-499. doi:10.1101/gr.209601.116"),
    ("Cutadapt", "Martin M. Cutadapt removes adapter sequences from high-throughput sequencing reads. EMBnet.journal 2011, 17.1:10-12. doi:10.14806/ej.17.1.200"),
    ("STAR", "Dobin A, Davis CA, Schlesinger F, Drenkow J, Zaleski C, Jha S, Batut P, Chaisson M, Gingeras TR. STAR: ultrafast universal RNA-seq aligner. Bioinformatics. 2013;29(1):15-21. doi:10.1093/bioinformatics/bts635"),
    ("SAMtools", "Danecek P, Bonfield JK, Liddle J, Marshall J, Ohan V, Pollard MO, Whitwham A, Keane T, McCarthy SA, Davies RM, Li H. Twelve years of SAMtools and BCFtools. GigaScience. 2021;10(2):giab008. doi:10.1093/gigascience/giab008"),
    ("featureCounts", "Liao Y, Smyth GK, Shi W. featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. Bioinformatics. 2014;30(7):923-930. doi:10.1093/bioinformatics/btt656"),
    ("Salmon", "Patro R, Duggal G, Love MI, Irizarry RA, Kingsford C. Salmon provides fast and bias-aware quantification of transcript expression. Nat Methods. 2017;14(4):417-419. doi:10.1038/nmeth.4197"),
    ("RSeQC", "Wang L, Wang S, Li W. RSeQC: quality control of RNA-seq experiments. Bioinformatics. 2012;28(16):2184-2185. doi:10.1093/bioinformatics/bts356"),
    ("MultiQC", "Ewels P, Magnusson M, Lundin S, Käller M. MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics. 2016;32(19):3047-3048. doi:10.1093/bioinformatics/btw354"),
    ("DESeq2", "Love MI, Huber W, Anders S. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biology 2014, 15:550. doi:10.1186/s13059-014-0550-8"),
    ("ashr", "Stephens M. False discovery rates: a new deal. Biostatistics. 2017;18(2):275-294. doi:10.1093/biostatistics/kxw041"),
]:
    add(para(name, bold=True))
    add(para(ref))
add(blank())

add(heading("Program versions"))
add(para("Versions as pinned by nf-core/rnaseq 3.26.0; the exact versions used are recorded in pipeline_info for each group."))
add(table([
    ("nf-core/rnaseq:", "3.26.0, https://nf-co.re/rnaseq"),
    ("Nextflow:", "25.04.7"),
    ("FastQC:", "v0.12.1"),
    ("UMI-tools:", "v1.1.6 (extract, dedup)"),
    ("Trim Galore:", "v2.1.0 (cutadapt wrapper)"),
    ("STAR:", "v2.7.11b"),
    ("SAMtools:", "v1.21 / v1.23.1"),
    ("featureCounts (Subread):", "v2.0.6"),
    ("Salmon:", "v1.10.3"),
    ("RSeQC:", "v5.0.4"),
    ("Qualimap:", "v2.3"),
    ("Preseq:", "v3.2.0"),
    ("dupRadar:", "v1.38.0"),
    ("MultiQC:", "v1.33"),
    ("Reference:", "Mus musculus GRCm39 primary assembly, Ensembl release 116"),
    ("R / DESeq2:", "[PLANNED] R 4.4 with DESeq2, ashr, pheatmap, ggplot2, ggrepel; versions to be recorded at analysis"),
]))
add(blank())

body = "<w:body>" + "".join(B) + sect + "</w:body></w:document>"
out = zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED)
for item in src.infolist():
    data = (head + body).encode() if item.filename == "word/document.xml" else src.read(item.filename)
    out.writestr(item, data)
out.close()
print("wrote", OUT)
