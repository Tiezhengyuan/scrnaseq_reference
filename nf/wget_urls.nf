#!/usr/bin/nextflow
// example : nextflow /home/yuan/bio/scrnaseq_reference/nf/wget_urls.nf

params.infile = file('./urls.csv')
params.outdir = file("./fastq")

channel.fromPath(params.infile)
    .splitText()
    .map { it.trim() }
    .set { ch_url }

process download{

    maxForks = 24
    queueSize = 24

    input:
    val url
    path outdir

    output:
    stdout

    script:
    """
    wget -c -r -v -np -nd $url -P $outdir || true
    """
}

workflow {
    download(ch_url, params.outdir)
    .view { println it }
}
