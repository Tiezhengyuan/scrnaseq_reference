'''
parse SRA data into GEO data
ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab
'''
import ftplib
import re
import os
import subprocess
from typing import Iterable

from utils import Utils
from slicer import Slicer
from retrieve_url import RetrieveUrl

class ParseSra:

    def __init__(self, local_dir:str, outdir:str):
        self.local_dir = local_dir
        self.outdir = outdir

    def line_iter(self) -> Iterable:
        '''
        read SRA_Accessions.tab
        columns:
        Accession       Submission      Status  Updated Published       
        Received        Type    Center  Visibility      Alias   
        Experiment      Sample  Study   Loaded  Spots   Bases   
        Md5sum  BioSample       BioProject      ReplacedBy
        '''
        url = 'ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab'
        infile = os.path.join(self.local_dir, url)
        with open(infile, 'r') as f:
            first_line = next(f)
            for line in f:
                line = line.rstrip()
                items = line.split('\t')
                yield items

    def acc_samn(self, prefix:str, slicer_func) -> tuple:
        '''
        SRXxxxx ~ SAMNxxxx
        SRSxxxx ~ SAMNxxxx
        SRRxxxx ~ SAMNxxxx
        '''
        res1, res2 = {}, {}
        for items in self.line_iter():
            acc, biosample = items[0], items[17]
            if acc.startswith(prefix) and biosample.startswith('SAMN'):
                acc_keys = slicer_func(acc)
                res1 = Utils.key_update(res1, acc_keys, [biosample,])
                biosample_keys = Slicer.BioSample(biosample)
                res2 = Utils.key_update(res2, biosample_keys, [acc,])
        # export
        file_sra = Utils.to_json(res1, self.outdir, f'{prefix.lower()}_samn.json')
        file_bio = Utils.to_json(res2, self.outdir, f'samn_{prefix.lower()}.json')
        return file_sra, file_bio


    def search(self, key:str, val:str):
        header = [
            'Accession', 'Submission', 'Status', 'Updated', 'Published',
            'Received', 'Type', 'Center', 'Visibility', 'Alias', 'Experiment',
            'Sample', 'Study', 'Loaded', 'Spots', 'Bases', 'Md5sum', 
            'BioSample', 'BioProject', 'ReplacedBy',
        ]
        for items in self.line_iter():
            rec = {k:v for k,v in zip(header, items)}
            if val in rec.get(key):
                print(rec)
    
    @staticmethod
    def parse_srr(enriched_data:dict, samn_srr:dict):
        '''
        parse SRR given biosample accession
        '''
        samples = enriched_data['samples']
        for sample_id, sample in samples.items():
            key = sample.get('BioSample')
            if key:
                if 'SRR' not in samples[sample_id]:
                    sample['SRR'] = {}
                biosample_keys = Slicer.BioSample(key)
                values = Utils.key_get(samn_srr, biosample_keys)
                for srr_acc in values:
                    if srr_acc not in sample['SRR']:
                        sample['SRR'][srr_acc] = {}
        return enriched_data
    
    @staticmethod
    def parse_ftp_fastq(data:dict, srr_fastq:dict, overwrite=False):
        '''
        parse urls of *.fastq.gz with biosamples and bioruns
        '''
        url = 'ftp.sra.ebi.ac.uk'
        print(f"Start {data['GEO']}...", end='\t')
        n = m = 0
        samples = data['samples']
        for sample_id, sample in samples.items():
            SRR = sample.get('SRR', {})
            for srr_acc in list(SRR):
                n += 1
                # force overwrrite or the key url doesn't exists
                if overwrite == True or url not in SRR[srr_acc]:
                    SRR[srr_acc][url] = []
                    # firstly, check if srr_acc exists in srr_fastq
                    keys = Utils.SRR(srr_acc)
                    values = Utils.keys_get(srr_fastq, keys)
                    if values:
                        SRR[srr_acc][url] = values
                        m += 1
                    #try to retrieve fastq urls in FTP
                    else:
                        fastq_url = RetrieveUrl.ftp_sra_ebi(srr_acc)
                        if fastq_url:
                            SRR[srr_acc][url] = fastq_url
                            m += 1
        print(f"{m} out of {n} SRR are updated.")
        return data


    #TODO
    @staticmethod
    def parse_srr_fastq(enriched_data:dict, samn_srr:dict, fastq_dir:str=None):
        '''
        parse SRR given biosample accession
        '''
        samples = enriched_data['samples']
        for sample_id in samples:
            key = samples[sample_id].get('BioSample')
            if key:
                biosample_keys = Slicer.BioSample(key)
                values = Utils.key_get(samn_srr, biosample_keys)
                srr_info = {}
                for srr_acc in values:
                    srr_info[srr_acc] = Utils.fastq_gz_path(srr_acc, fastq_dir)
                samples[sample_id]['SRR'] = srr_info
        return enriched_data

    def move_srr_fastq(self):
        '''
        Organize SRR FASTQ
        move SRR*.fastq.gz to a certain directory
        '''
        n = m = 0
        file_iter = Utils.file_pattern_iter(self.local_dir, '.fastq.gz')
        for path in file_iter:
            file_name = os.path.basename(path)
            srr_acc = re.findall(r'SRR\d*', file_name)[0]
            keys = Slicer.SRR(srr_acc)
            new_outdir = Utils.init_dir(self.outdir, keys[:-1])
            new_name = f"{srr_acc}.fastq.gz"
            outfile = os.path.join(new_outdir, new_name)
            if os.path.isfile(outfile):
                print(f"Warning: skip moving. {path} exists in {outfile}")
            else:
                # run command
                try:
                    cmd = ['mv', path, outfile]
                    # print(cmd)
                    subprocess.run(cmd, check=True)
                    n += 1
                except Exception as e:
                    m += 1
        print(f"{n} files are moved to {self.outdir}.")
        if m > 0:
            print(f"Warning: Moving {m} files failed.")
