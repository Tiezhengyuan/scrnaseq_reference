import os
import json
from utils import Utils

class LabelData:
    http = 'https://www.ncbi.nlm.nih.gov/geo'
    attrs = ['disease', 'tissue', 'cell_type', 
            'cell_line', 'treated', 'cultivation']

    def __init__(self, data_dir:str=None):
        self.data_dir = data_dir if data_dir else \
            '/home/yuan/bio/scrnaseq_reference/data'

    def json_iter(self):
        '''
        scan all data from json
        '''
        file_iter = Utils.file_pattern_iter(self.data_dir, '.json')
        for path in file_iter:
            yield Utils.from_json(path)

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
        data = {}
        infile = os.path.join(self.data_dir, f"{geo}.json")
        if os.path.isfile(infile):
            with open(infile, 'r') as f:
                data = json.load(f)
        return data

    def save(self, data:dict):
        geo = data['GEO']
        outfile = os.path.join(self.data_dir, f"{geo}.json")
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
        return outfile
    

