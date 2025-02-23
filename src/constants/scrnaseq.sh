#!/usr/bin/bash
nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker \
   --input samplesheet.csv \
   --genome_fasta /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Sequence/WholeGenomeFasta/genome.fa \
   --gtf /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Annotation/Genes/genes.gtf \
   --protocol 10XV2 --aligner cellranger \
    --outdir ./
   
