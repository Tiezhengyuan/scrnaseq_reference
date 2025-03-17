# scrnaseq_reference
This study builds reference data sets based on GEO public ssRNA-seq data, and create a model for cell type annotations from normal tissue, tumor tissue, biopsy or cell lines of
lung disease, or breast cancer.


## introduction
Compared with bulk mRNA-seq, spatial transcriptomics requires clustering or cell type identifications before step into further bioinformatics analysis. In lab reseach or clinical cohort study, one or multiple biosamples from the tissues of healthy donors, or tumor cell lines are included as references. However, in some cases, for example, some clinical sequencing trails collect spatial lung tissues without knowning about tumor or normal. In such cases, inclusion of multiple standard biosamples as references cost much. Therefore, employ standard references is an alternative approach. Compared with biomarker approach, the input data is entire expression profile of a single cell results in higher resolution of cell type identification.


## build reference datasets

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

### prepare raw data *fastq.gz

split one fastq into r1/r2 if possible
```
seqtk seq -1 SRR9304774.fastq.gz > SRR9304774_1.fastq.gz
seqtk seq -2 SRR9304774.fastq.gz > SRR9304774_2.fastq.gz
```

download fastq based on SRR accession
```
fastq-dump --outdir fastq --skip-technical  --readids --read-filter pass \
    --dumpbase --split-3 --clip --gzip SRR9304774
```


## standardsize scRNA-seq pipeline

```
nextflow run nf-core/scrnaseq -r 3.0.0 -profile docker -c params.config
```

Here are examples of params.config
```
params {
	input = "./samplesheet.csv"
	outdir = "./"
	protocol = "10XV2"
	genome = "GRCh38"
	fasta = "~/results/references/Homo_sapiens/NCBI/GRCh38/Sequence/WholeGenomeFasta/genome.fa"
	gtf = "~/results/references/Homo_sapiens/NCBI/GRCh38/Annotation/Genes/genes.gtf"
	skip_emptydrops = true
}


process {
	maxErrors = 10
	resourceLimits = [
		memory: 128.GB,
		max_cpus: 8,
	    time: 128.h
	]
}
docker {
	enabled = true
}
executor {
    retry {
        maxAttempt = 5
    }
}
```

## datasets for references

- cell lines of lung cancer; "GSE121309", "GSE286399"
- healthy lung tissue: "GSE135893", "GSE136831", "GSE164829"
- lung disease: "GSE135893", "GSE136831", "GSE145926", "GSE166037"
- breast cancer: xxx

Note:
- the number of 28 datasets related to lung disease are unavailable.
- the number of 9 datasets related to breast cancer are unavailable.


Reasons of failure of scRNA-seq data analysis:
- Raw data are not released by the authors till now.
- Technical reads are missing. there are only biological reads.
- There are no index codes for spatial transcriptomics seq data. there are only biological reads.
- Can't label data because Annotations in some fields in GEO are confusing.
- Some records in fastq.gz files are incorrect. Such samples have to be deprecated.
 