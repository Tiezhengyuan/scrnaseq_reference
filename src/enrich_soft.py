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
from label_sample import LabelSample


class EnrichSoft:
    http = 'https://www.ncbi.nlm.nih.gov/geo'

    def __init__(self, data:dict):
        self.data = data
        self.GEO()    
    
    def __call__(self):
        return {
            'GEO': self.geo,
            'local_soft_file': self.data['local_soft_file'],
            'geo_http': f"{self.http}/query/acc.cgi?acc={self.geo}",
            'title': ' '.join(self.title()),
            'summary': self.summary(),
            'PMID': self.PMID(),
            'taxid': self.taxid(),
            'platform': self.platform(),
            'samples': self.samples(),
        }

    
    def GEO(self):
        self.geo = self.data['GEO']
    
    def PMID(self):
        return self.data['SERIES'][0].get('Series_pubmed_id')

    def title(self):
        return self.data['SERIES'][0].get('Series_title')

    def sample_ids(self):
        return self.data['SERIES'][0].get('Series_sample_id')

    def taxid(self):
        taxid = [i.get('Series_platform_taxid', []) for i in self.data['SERIES']]
        return sum(taxid, [])
    
    def summary(self):
        series_summary = self.data['SERIES'][0].get('Series_summary', [])
        return ' '.join(series_summary)

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
            _sample = {
                'sample_id': sample_id,
                'sample_title': sample['Sample_title'][0] if sample.get('Sample_title') else None,
                'protocol': [],
                'characteristics': {},
                'labels': {},
            }
            for k,v in sample.items():
                if k.startswith('Sample_taxid'):
                    _sample['sample_taxid'] = v[0]
                elif k.startswith('Sample_characteristics'):
                    self.sample_characteristics(_sample['characteristics'], v)
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
                    _sample[k] = ' '.join(v)
                elif k.startswith('Sample_source'):
                    _sample['sample_source'] = v
                    if v:
                        _sample['characteristics']['tissue'] = v[0].lower()
                elif '_protocol' in k or '_data_processing' in k:
                    self.sample_protocol(_sample['protocol'], v)
            # retrieve protocol from sample_title
            self.sample_protocol(_sample['protocol'], sample.get('Sample_title', []))
            _sample['protocol'] = list(set(_sample['protocol']))

            # add 'labels' into _sample
            self.sample_labels(_sample)
            LabelSample(self.geo, _sample)()

            res[sample_id] = _sample

            # print(_sample['sample_title'], _sample['labels'])
            # break
        return res


    def sample_labels(self, sample):
        '''
        data labels used for ML
        most labels are defined in sample['characteristics']
        '''
        cht = sample['characteristics']
        lb = sample['labels']
        # combine keys
        pool = {
            'disease_state': ('disease_state', 'disease_condition', \
                'infectious_agent', 'subject_status', \
                'diagnosis', 'disease_diagnosis', 'infection'),
            'tissue': ('tissue', 'organ', 'engraftment'),
            'disease': ('disease', ),
            'cell_line': ('cell_line',),
            'treatment': ('treatment', 'treated'),
            'cell_type': ('cell_type', 'cell_subsets'),
            'group': ('group', 'patient_group', 'tissue_type'),
        }
        for key, keywords in pool.items():
            for k in keywords:
                if cht.get(k):
                    lb[key] = cht[k].lower()
                    break

        '''
        label values
        disease: healthy, <disease name>
        disease_state: 
        group: control, patient, <other names>
        '''
        # healthy control
        healthy_alias = ["healthy donor", "health donors", \
            "normal/healthy donor", "healthy control"]
        if lb.get('disease_state') in healthy_alias:
            lb['disease'] = 'healthy'
            lb['group'] = 'control'
            del lb['disease_state']
        elif lb.get('disease_state') == 'control':
            lb['group'] = 'control'
            del lb['disease_state']

    def sample_protocol(self, protocol:list, values:list):
        '''
        protocol = _sample['protocol']
        standardize keywords
        '''
        v = ' '.join(values).lower().replace('  ', ' ')

        # detect scRNA-seq
        pattern = ['single-cell rna-seq', 'single cell rna-seq', \
            'single cell rnaseq', 'scrna-seq', 'scrnaseq']
        if re.findall('|'.join(pattern), v):
            # print(self.geo, re.findall('|'.join(pattern), v))
            protocol.append('scrna-seq')
        if re.findall(r'single-cell|single cell|single cells', v):
            protocol.append('single cell')

        # retrieve keywords
        pattern = ['cdna', 'sequencing', 'gdna', 'rna-seq', \
            'total rna', 'rna', 'genomic dna',]
        pattern = '|'.join(pattern)
        res = re.findall(pattern, v)
        [protocol.append(i) for i in res if i not in protocol]

    def sample_characteristics(self, cht:dict, values:list):
        '''
        stanadardize terminology of Sample_characteristics
        arggs: cht: _sample['characteristics']
        Note: cht is updated inplace
        '''
        for val in values:
            k, v = val.lower().split(': ', 1)
            k = k.replace(' ', '_')
            if v == 'n/a':
                v = None
            cht[k] = v

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
        