'''
Prepare GEO data, which will be used for downloading and labaling
'''
import os
import json
from utils import Utils
from slicer import Slicer

class LabelData:
    http = 'https://www.ncbi.nlm.nih.gov/geo'
    attrs = ['disease', 'tissue', 'cell_type', 
            'cell_line', 'treated', 'cultivation']

    def __init__(self, data_dir:str=None):
        self.data_dir = data_dir if data_dir else \
            '/home/yuan/bio/scrnaseq_reference/data'

    def load(self, geo:str, sample_ids:list=None):
        curr = self.from_json(geo)
        if curr:
            return curr
        return self.create(geo, sample_ids)

    def create(self, geo:str, sample_ids:list=None):
        data = {
            'GEO': geo,
            'samples': {},
            'http': f"{self.http}/query/acc.cgi?acc={geo}"
        }
        if sample_ids:
            for sample_id in sample_ids:
                rec = {i:'' for i in self.attrs}
                data['samples'][sample_id] = rec
        return data

    def from_json(self, geo:str):
        '''
        retrieve data given a GEO from local json
        '''
        data = {}
        geo_key = Slicer.GEO(geo)[0]
        indir = Utils.init_dir(self.data_dir, [geo_key,])
        infile = os.path.join(indir, f"{geo}.json")
        data = Utils.from_json(infile)
        return data

    def save(self, data:dict):
        '''
        save save to the local path in json format
        '''
        geo = data['GEO']
        geo_key = Slicer.GEO(geo)[0]
        outdir = Utils.init_dir(self.data_dir, [geo_key,])
        outfile = Utils.to_json(data, outdir, f"{geo}.json")
        return outfile
    

