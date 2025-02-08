#!/usr/bin/nextflow

params.local_dir = "/home/yuan/data/"
params.indir = file("${params.local_dir}ftp.ncbi.nlm.nih.gov/geo/series/GSE83nnn")
params.outfile = '../data/test.txt'

channel
    .fromPath("${params.indir}/*/soft/GSE830*.soft.gz")
    .set {ch_file}


process validate {
    input:
    path infile

    output:
    stdout

    script:
    """
    python ${PWD}/src/validate_gz.py ${infile}
    """
}

process download {
    debug true

    input:
    val url

    output:
    stdout

    script:
    """
    wget -c -r ${url} -P ${params.local_dir}
    """
}

workflow {
     validate(ch_file).combine(ch_file)
        .filter { it -> it[0].contains('False')}
        .set { ch_fail }

        ch_fail
            .map {
                String p = it[1]
                p = it[0] + p
            }
            .collectFile(name: "${PWD}/data/validate_soft.txt", newLine: true)


        // ch_fail.map { it ->
        //         String p = it[1].parent
        //         p.replace(params.local_dir, 'ftp://')
        //     }.set {ch_url}
        // download(ch_url)
}