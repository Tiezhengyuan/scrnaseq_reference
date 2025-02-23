# scrnaseq_reference
References for cell type annotations from scRNA-Seq


### prepare refereces
install aws
```
sudo snap install aws-cli --classic
aws --version
```

download human genome NCBI-GRCh38
```
cd ~/results/references
aws s3 --no-sign-request --region eu-west-1 \
    sync s3://ngi-igenomes/igenomes/Homo_sapiens/NCBI/GRCh38 \
    ./Homo_sapiens/NCBI/GRCh38/
```

seqtk seq -1 SRR9304774.fastq.gz > SRR9304774_1.fastq.gz
seqtk seq -2 SRR9304774.fastq.gz > SRR9304774_2.fastq.gz


download fastq based on SRR accession
```
fastq-dump --outdir fastq --skip-technical  --readids --read-filter pass \
    --dumpbase --split-3 --clip --gzip SRR9304774
```

<!-- fastq1 -->
fastq-dump --outdir fastq1 --skip-technical  --readids \
    --dumpbase --split-files --clip --gzip SRR9304774

<!-- fastq2 -->
fastq-dump --outdir fastq2 --skip-technical --split-files --gzip SRR9304774


fastq-dump --skip-technical --split-files --gzip SRR8933535






<!-- pass -->

nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker --input samplesheet.csv --outdir ./ \
    --protocol 10XV2 --genome GRCh38


nextflow run nf-core/scrnaseq -r 3.0.0 -profile docker --input samplesheet.csv --outdir ./ \
    --protocol 10XV2 --genome GRCh38


nextflow run nf-core/scrnaseq -c params.config


nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker --input samplesheet.csv --outdir ./ \
    --skip_multiqc --skip_fastqc --protocol 10XV2 --aligner cellranger --genome GRCh38


#
nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker --input samplesheet.csv --outdir ./ \
    --skip_multiqc --skip_fastqc \
    --protocol 10XV2 --aligner cellranger --genome GRCh38 \
    --fasta /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Sequence/WholeGenomeFasta/genome.fa \
    --gtf /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Annotation/Genes/genes.gtf 
    



nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker \
    --input samplesheet.csv --outdir ./ --protocol 10XV2 --aligner star \
    --star_index /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Sequence/STARIndex \
    --fasta /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Sequence/WholeGenomeFasta/genome.fa \
    --gtf /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Annotation/Genes/genes.gtf








nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker \
   --input samplesheet.csv \
   --fasta /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Sequence/WholeGenomeFasta/genome.fa \
   --gtf /home/yuan/results/references/Homo_sapiens/NCBI/GRCh38/Annotation/Genes/genes.gtf \
   --protocol 10XV2 --aligner cellranger \
    --outdir ./


nextflow run nf-core/scrnaseq -r 2.7.0 -profile docker \
   --input samplesheet.csv \
   --genome GRCh38 \
   --protocol 10XV2 --aligner cellranger \
    --outdir ./
   