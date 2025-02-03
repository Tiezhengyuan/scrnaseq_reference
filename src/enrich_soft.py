'''
Enrich soft data
'''
import os
import gzip
import json
import re
import requests

from typing import Iterable
from utils import Utils


class EnrichSoft:
    http = 'https://www.ncbi.nlm.nih.gov/geo'

    def __init__(self, data:dict):
        self.data = data
    
    def __call__(self):
        geo = self.GEO()
        enriched = {
            'GEO': geo,
            'geo_http': f"{self.http}/query/acc.cgi?acc={geo}",
            'title': ' '.join(self.title()),
            'PMID': self.PMID(),
            'taxid': self.taxid(),
            'platform': self.platform(),
            'samples': self.samples(),
        }
        return enriched
    
    def GEO(self):
        return self.data['GEO']
    
    def PMID(self):
        return self.data['SERIES'][0].get('Series_pubmed_id')

    def title(self):
        return self.data['SERIES'][0].get('Series_title')

    def sample_ids(self):
        return self.data['SERIES'][0].get('Series_sample_id')

    def taxid(self):
        return self.data['SERIES'][0].get('Series_platform_taxid')[0]

    def platform(self):
        res = []
        for item in self.data['PLATFORM']:
            res.append({
                'platform_id': item['PLATFORM'],
                'platform_title': item['Platform_title'][0],
                'platform_technology': item['Platform_technology'][0],
            })
        return res
    
    def samples(self) ->dict:
        res = {}
        for sample in self.data.get('SAMPLE', []):
            sample_id = sample['SAMPLE']
            res[sample_id] = {
                'sample_id': sample_id,
            }
            _sample = {}
            for k,v in sample.items():
                if k.startswith('Sample_characteristics'):
                    sub = dict([tuple(i.split(': ', 1)) for i in v])
                    _sample['characteristics'] = sub
                elif k.startswith('Sample_relation'):
                    sub = dict([tuple(i.split(': ', 1)) for i in v])
                    if 'SRA' in sub:
                        sub['SRA_url'] = sub['SRA']
                        sub['SRA'] = re.findall(r'SRX\d*', sub['SRA'])[0]
                    if 'BioSample' in sub:
                        sub['BioSample_url'] = sub['BioSample']
                        sub['BioSample'] = re.findall(r'SAMN\d*', sub['BioSample'])[0]
                    _sample.update(sub)
                elif k.startswith('Sample_description'):
                    _sample[k] = v
                elif '_protocol' in k:
                    v = ' '.join(v).lower()
                    _sample['scrnaseq'] = True if 'single-cell' in v else False
            res[sample_id].update(_sample)
        return res

    def SRR(self, SRA_url):
        '''
        Accorcding to SRA url,
        retrieve the runn accession SRRxxxxx
        '''
        try:
            res = requests.get(SRA_url)
            _s = re.findall(r'SRR\d*', res.txt)
            return list(set(_s))
        except Exception as e:
            pass
        return []
        