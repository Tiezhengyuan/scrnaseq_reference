'''
Prepare GEO data, which will be used for downloading and labaling
'''
import os
import json
from typing import Iterable
from utils import Utils
from slicer import Slicer

class LabelData:
    http = 'https://www.ncbi.nlm.nih.gov/geo'

    def __init__(self, data_dir, name:str=None, outdir:str=None):
        self.data_dir = data_dir
        self.labels_dir = os.path.join(self.data_dir, 'labels')
        self.name = name
        self.outdir = outdir

    def sample_iter(self) -> Iterable:
        '''
        iterate biosamples defined in GEO
        '''
        for data in Utils.json_iter(self.labels_dir):
            geo = data['GEO']
            samples = data('samples', {})
            for sample_id, sample in samples.items():
                yield geo, sample

    def fastq_iter(self) -> Iterable:
        '''
        for sample_sheet
        '''
        for data in Utils.json_iter(self.labels_dir):
            geo = data['GEO']
            samples = data.get('samples', {})
            for sample_id, sample in samples.items():
                if sample.get('SRA') and sample.get('SRR'):
                    run_acc = sample['SRA']
                    fastq_sample = sample['labels']
                    fastq_sample['sample_sheet'] = []
                    for srr_acc, v in sample['SRR'].items():
                        if v.get('local_fastq'):
                            fq1, fq2, fq3 = [], [], []
                            for fq in v['local_fastq']:
                                if fq.endswith('_1.fastq.gz'):
                                    fq1.append(fq)
                                elif fq.endswith('_2.fastq.gz'):
                                    fq2.append(fq)
                                else:
                                    fq3.append(fq)
                            if not fq1:
                                fq1 = fq3
                            rec = {
                                'sample': f"{geo}_{run_acc}_{srr_acc}",
                                'fastq_1': ','.join(fq1),
                                'fastq_2': ','.join(fq2),
                            }
                            fastq_sample['sample_sheet'].append(rec)
                    if fastq_sample['sample_sheet']:
                        yield sample, geo, run_acc, fastq_sample

    def from_json(self, geo:str):
        '''
        retrieve data given a GEO from local json
        '''
        data = {}
        geo_key = Slicer.GEO(geo)[0]
        indir = Utils.init_dir(self.labels_dir, [geo_key,])
        infile = os.path.join(indir, f"{geo}.json")
        data = Utils.from_json(infile)
        return data

    def save(self, data:dict):
        '''
        save save to the local path in json format
        '''
        geo = data['GEO']
        geo_key = Slicer.GEO(geo)[0]
        outdir = Utils.init_dir(self.labels_dir, [geo_key,])
        outfile = Utils.to_json(data, outdir, geo)
        return outfile
    
    def count_meta(self, data):
        '''
        sample_type: names of cell_line or tissue
        '''

        sample_type, geo, biosample, run = [], [], [], 0
        for k1, v1 in data.items():
            sample_type.append(k1)
            for k2, v2 in v1.items():
                geo.append(k2)
                for k3,v3 in v2.items():
                    biosample.append(k3)
                    sample_sheet = v3['sample_sheet']
                    run += len(sample_sheet)
        # count
        sample_type = list(set(sample_type))
        geo = list(set(geo))
        info = {
            'num_sample_type': len(sample_type),
            'num_geo': len(geo),
            'num_biosample': len(list(set(biosample))),
            'num_runs': run,
            'sample_type': sorted(sample_type),
            'geo': sorted(geo),
        }
        print(f"Name of datasets: {self.name}")
        print('Count metadata:', json.dumps(info, indent=4))
        return None

    def to_json(self, data):
        outfile = Utils.to_json(data, self.data_dir, self.name)
        print('metadata: ', os.path.abspath(outfile))

    def to_sample_sheet(self, samples:dict):
        '''
        export to samplesheet_*.csv for nf-core/scrna-seq
        '''
        for geo, sample_sheet in samples.items():
            outdir = Utils.init_dir(self.outdir, [self.name, geo])
            sample_sheet = sorted(sample_sheet, key=lambda x: x['sample'])
            headers = ['sample', 'fastq_1', 'fastq_2']
            outfile = os.path.join(outdir, "samplesheet.csv")
            with open(outfile, 'w') as f:
                f.write(','.join(headers) + '\n')
                for item in sample_sheet:
                    rec = [item[i] for i in headers if i in item]
                    line = ','.join(rec) + '\n'
                    f.write(line)
            print('samplesheet: ', os.path.abspath(outfile))

    # def to_bash(self):
    #     '''
    #     '''
    #     cmd = [
    #         "nextflow run nf-core/scrnaseq -r \"
    #     ]
