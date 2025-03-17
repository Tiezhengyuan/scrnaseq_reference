import os
import json
import shutil
from typing import Iterable

from utils import Utils
from slicer import Slicer

class CreateConfig:
    src_dir = os.path.dirname(__file__)

    def __init__(self, outdir:str, geo:str):
        self.outdir = Utils.init_dir(outdir, [geo,])
        self.geo = geo

    @staticmethod
    def get_biosamples(meta_dir:str) -> Iterable:
        '''
        get sample_id for download fastq
        '''
        indir = os.path.join(meta_dir, 'labels')
        for data in Utils.json_iter(indir):
            geo = data['GEO']
            biosamples = []
            samples = data.get('samples', {})
            for sample_id, info in samples.items():
                # SRX accessions should exist
                if 'SRA' in info:
                    biosamples.append(info['BioSample'])
            if biosamples:
                yield geo, biosamples

    def fetch_biosample(self, sample_iter) -> str:
        '''
        build two files
        ids used for nf-core/fetchngs
        '''
        # ids.csv
        n, biosamples = 0, []
        for sample in sample_iter:
            n += 1
            if 'SRA' in sample:
                biosamples.append(sample['BioSample'])
        print('Number of biosamples: ', n)
        print('Number of biosamples with SRR: ', len(biosamples))
        self.to_text(biosamples, 'ids.csv')
        
        # copy params.config
        constants_dir = os.path.join(CreateConfig.src_dir, 'constants')
        default_config = os.path.join(constants_dir, "ids_params.config")
        shutil.copy(default_config, self.outdir)

        # bash file
        cmd = [
            'cd ' + self.outdir,
            'nextflow run nf-core/fetchngs -r 1.12.0 \\',
            '  -profile docker -c ids_params.config',
        ]
        bash_file = self.to_text(cmd, 'fetch1.sh')

    def fetch_ebi_srr(self, sample_iter):
        '''
        urls.csv for nextflow download
        '''
        # urls.csv
        urls = []
        for sample in sample_iter:
            for srr_acc in sample.get('SRR', {}):
                if not sample['SRR'][srr_acc].get('local_fastq'):
                    keys = Slicer.SRR(srr_acc)
                    url = 'ftp://ftp.sra.ebi.ac.uk/vol1/fastq/' + '/'.join(keys)
                    urls.append(url)
        print('Number of SRR: ', len(urls))
        self.to_text(urls, 'urls.csv')
        
        # bash file
        nf_dir = os.path.join(os.path.dirname(CreateConfig.src_dir), 'nf')
        cmd = [
            'cd ' + self.outdir,
            'nextflow ' + os.path.join(nf_dir, 'wget_urls.nf'),
        ]
        bash_file = self.to_text(cmd, 'fetch2.sh')

    def fetch_ebi_srr_verify(self, sample_iter):
        '''
        run wget directly instead of nextflow script for verification
        '''
        cmd_pool = []
        outdir = os.path.join(self.outdir, 'fastq')
        for sample in sample_iter:
            for srr_acc in sample.get('SRR', {}):
                keys = Slicer.SRR(srr_acc)
                url = 'ftp://ftp.sra.ebi.ac.uk/vol1/fastq/' + '/'.join(keys)
                cmd = f"wget -c -r -v -np -nd {url} -P {outdir} || true"
                cmd_pool.append(cmd)
        print('Number of SRR: ', len(cmd_pool))
        # bash file
        bash_file = self.to_text(cmd_pool, 'fetch2_wget.sh')


    def fetch_srr(self, sample_iter):
        '''
        srr_ids.csv for nextflow download using fastq-dump
        '''
        pool = []
        for sample in sample_iter:
            for srr_acc in sample.get('SRR', {}):
                if not sample['SRR'][srr_acc].get('local_fastq'):
                    pool.append(srr_acc)
        print('Number of SRR: ', len(pool))
        self.to_text(pool, 'srr_ids.csv')
        
        # bash file
        nf_dir = os.path.join(os.path.dirname(CreateConfig.src_dir), 'nf')
        cmd = [
            'cd ' + self.outdir,
            'nextflow ' + os.path.join(nf_dir, 'fastq_dump.nf'),
        ]
        bash_file = self.to_text(cmd, 'fetch3.sh')

    def to_text(self, cmd:list, file_name:str):
        '''
        create a bash file
        '''
        outfile = os.path.join(self.outdir, file_name)
        with open(outfile, 'w') as f:
            f.write('\n'.join(cmd))
        if file_name.endswith('.sh'):
            print(f"cd {self.outdir} && bash {file_name}")
        return outfile
