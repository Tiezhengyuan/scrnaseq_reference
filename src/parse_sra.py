'''
ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab

Accession       Submission      Status  Updated Published       
Received        Type    Center  Visibility      Alias   
Experiment      Sample  Study   Loaded  Spots   Bases   
Md5sum  BioSample       BioProject      ReplacedBy

'''
import re
import os
import json
import subprocess
from typing import Iterable


from utils import Utils
from slicer import Slicer

class ParseSra:

    def __init__(self, local_dir:str, outdir:str):
        self.local_dir = local_dir
        self.outdir = outdir


    def line_iter(self) -> Iterable:
        '''
        read SRA_Accessions.tab
        '''
        url = 'ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/SRA_Accessions.tab'
        infile = os.path.join(self.local_dir, url)
        with open(infile, 'r') as f:
            first_line = next(f)
            for line in f:
                line = line.rstrip()
                items = line.split('\t')
                yield items

    def srx_samn(self) -> tuple:
        '''
        SRXxxxx ~ SAMNxxxx
        '''
        res1, res2 = {}, {}
        for items in self.line_iter():
            acc, biosample = items[0], items[17]
            if acc.startswith('SRX') and biosample.startswith('SAMN'):
                acc_keys = Slicer.SRX(acc)
                res1 = Utils.key_update(res1, acc_keys, [biosample,])
                biosample_keys = Slicer.BioSample(biosample)
                res2 = Utils.key_update(res2, biosample_keys, [acc,])
        # export
        file_sra = Utils.to_json(res1, self.outdir, 'srx_samn.json')
        file_bio = Utils.to_json(res2, self.outdir, 'samn_srx.json')
        return file_sra, file_bio

    def srr_samn(self) -> tuple:
        '''
        SRRxxxx ~ SAMNxxxx
        '''
        res1, res2 = {}, {}
        for items in self.line_iter():
            acc, biosample = items[0], items[17]
            if acc.startswith('SRR') and biosample.startswith('SAMN'):
                acc_keys = Slicer.SRR(acc)
                res1 = Utils.key_update(res1, acc_keys, [biosample,])
                biosample_keys = Slicer.BioSample(biosample)
                res2 = Utils.key_update(res2, biosample_keys, [acc,])
        # export
        file_sra = Utils.to_json(res1, self.outdir, 'srr_samn.json')
        file_bio = Utils.to_json(res2, self.outdir, 'samn_srr.json')
        return file_sra, file_bio           

    def search(self, ix:int, val:str):
        header = [
            'Accession', 'Submission', 'Status', 'Updated', 'Published',
            'Received', 'Type', 'Center', 'Visibility', 'Alias', 'Experiment',
            'Sample', 'Study', 'Loaded', 'Spots', 'Bases', 'Md5sum', 
            'BioSample', 'BioProject', 'ReplacedBy',
        ]
        for items in self.line_iter():
            if val in items[ix]:
                rec = {k:v for k,v in zip(header, items)}
                print(rec)
    
    @staticmethod
    def parse_srr(enriched_data:dict, samn_srr:dict, fastq_dir:str=None):
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
                    fq_path = Utils.fastq_gz_path(srr_acc, fastq_dir)
                    srr_info[srr_acc] = fq_path if fq_path else ''
                samples[sample_id]['SRR'] = srr_info
        return enriched_data
    
    def move_srr_fastq(self):
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
