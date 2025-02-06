import os
import json
import shutil
from typing import Iterable

from utils import Utils

class CreateConfig:
    constants_dir = os.path.join(os.path.dirname(__file__), 'constants')

    def __init__(self, meta_dir:str):
        self.meta_dir = meta_dir

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
    
    @staticmethod
    def fetch_geo(geo:str, samples:list, outdir:str) -> str:
        '''
        ids used for nf-core/fetchngs
        '''
        outdir = os.path.join(outdir, geo)
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        # build two files
        # ids file
        id_file = os.path.join(outdir, "ids.csv")
        with open(id_file, 'w') as f1:
            f1.write('\n'.join(samples))
        
        # copy params.config
        default_config = os.path.join(CreateConfig.constants_dir, "params.config")
        shutil.copy(default_config, outdir)

        # bash file
        bash_file = os.path.join(outdir, "run.sh")
        with open(bash_file, 'w') as f2:
            cmd = [
                'cd ' + outdir,
                'nextflow run nf-core/fetchngs -r 1.12.0 -profile docker -c params.config',
            ]
            f2.write('\n'.join(cmd))
        return bash_file
