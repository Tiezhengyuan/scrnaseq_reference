#!/usr/bin/nextflow
// example : nextflow src/download_srr_fastq.nf --urls "srr_ids.txt"

params.urls = "srr_ids.txt"
params.infile = file("/home/yuan/bio/scrnaseq_reference/results/${params.urls}")
params.outdir = file("/home/yuan/data/fastq")

channel.fromPath(params.infile)
    .splitText()
    .map { it.trim() }
    .set { ch_url }

process download{

    maxForks = 24
    queueSize = 24

    input:
    val srr_acc
    path outdir

    output:
    stdout

    script:
    """
    fastq-dump $srr_acc -O $outdir --gzip || true
    """
}

workflow {
    download(chr_url, params.outdir)
    .view { println it }
}
