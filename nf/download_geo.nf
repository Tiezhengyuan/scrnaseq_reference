#!/usr/bin/nextflow
// example : nextflow src/download_geo.nf --urls "soft_urls.txt"

// params.urls = "soft_url.txt"
params.infile = file("/home/yuan/bio/scrnaseq_reference/results/${params.urls}")
params.outdir = file("/home/yuan/data")

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
    val "${HOME}/${outdir}/${url}"

    script:
    """
    wget -c -r -nc --tries=3 ftp://$url -P $outdir || true
    """
}

workflow {
    download(ch_url, params.outdir)
    .view { println it }
}
