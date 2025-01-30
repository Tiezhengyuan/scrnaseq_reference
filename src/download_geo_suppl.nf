#!/usr/bin/nextflow
// example : nextflow src/download_geo_suppl.nf --urls "scrnaseq_cell_line_urls.csv"

params.urls = "scrnaseq_cell_line_url.txt"
params.infile = file("/home/yuan/bio/scrnaseq_reference/results/${params.urls}")
params.outdir = file("/home/yuan/results/scrnaseq_cell_line")

channel.fromPath(params.infile)
    .splitCsv()
    .set { ch_url }

process download{

    maxForks = 24
    queueSize = 24

    input:
    tuple val(geo), val(url)
    path outdir

    output:
    val "${HOME}/${outdir}/${geo}"

    script:
    """
    wget -c -r -nc -nH --cut-dirs=10 -P $outdir/$geo $url || true &&
    tar -xvf $outdir/$geo/*.tar -C $outdir/$geo || true
    """
}

workflow {
    download(ch_url, params.outdir)
    .view { println it }
}
