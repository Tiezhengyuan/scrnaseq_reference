#!/usr/bin/nextflow
// example : nextflow nf/fastq_dump.nf

params.infile = file("./srr_ids.csv")
params.outdir = file("fastq")

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
    cd ${PWD}
    fastq-dump $srr_acc --outdir $outdir --gzip --split-3 --readids --dumpbase --clip || true
    """
}

workflow {
    download(ch_url, params.outdir)
    .view { println it }
}
