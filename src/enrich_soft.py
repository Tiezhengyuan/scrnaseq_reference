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
                    _sample['characteristics'] = self.sample_characteristics(v)
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

    def sample_characteristics(self, values:list):
        '''
        stanadardize terminology of Sample_characteristics
        '''
        cht = {}
        for val in values:
            k, v = val.split(': ', 1)
            k = k.lower().replace(' ', '_')
            cht[k] = v

        # combine keys
        cht = Utils.rename_key(cht, 'cell_type', 'cell_subsets')
        cht = Utils.rename_key(cht, 'tissue', 'organ')
        cht = Utils.rename_key(cht, 'tissue', 'engraftment')
        cht = Utils.rename_key(cht, 'disease_state', 'disease')
        cht = Utils.rename_key(cht, 'disease_state', 'infection')
        cht = Utils.rename_key(cht, 'disease_state', 'infectious_agent')
        cht = Utils.rename_key(cht, 'disease_state', 'subject_status')
        cht = Utils.rename_key(cht, 'time_point', 'time')
        cht = Utils.rename_key(cht, 'time_point', 'time_point_post_infection')
        cht = Utils.rename_key(cht, 'technology', '10x_chromium_encapsulation_kit')
        cht = Utils.rename_key(cht, 'group', 'patient_group')
        # delete some keys
        for k in ('patient_origin', 'sample_id', 'passage'):
            if k in cht:
                del cht[k]
        return cht

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
        