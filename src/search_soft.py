import os
import gzip
import json
import re
from typing import Iterable
from utils import Utils

class SearchSoft:
    def __init__(self, soft_file:str):
        '''
        soft_file should be *.gz format
        '''
        self.infile = soft_file

    def line_iter(self):
        return Utils.gz_iter(self.infile)

    def split_row(self, line) -> tuple:
        items = line[1:].split(" = ", 1)
        key = items[0]
        val = items[1] if len(items) == 2 else ''
        return key, val



    def taxid(self):
        taxid, organism = None, None
        try:
            with gzip.open(self.infile, 'rt') as f:
                for line in f:
                    line = str(line.rstrip())
                    if line.startswith('!Platform_taxid'):
                        taxid = self.split_row(line)[-1]
                    elif line.startswith('!Platform_organism'):
                        organism = self.split_row(line)[-1]
                    if taxid and organism:
                        return {
                            'taxid': taxid,
                            'organism': organism,
                            'key': organism + '_' + taxid,
                        }
        except Exception as e:
            print(f"error={e}, path={self.infile}")
        return None

    def human_series_type(self):
        '''
        human taxid=9606
        '''
        taxid, series_type, summary = None, None, None
        try:
            with gzip.open(self.infile, 'rt') as f:
                for line in f:
                    line = str(line.rstrip())
                    if line.startswith('!Platform_taxid'):
                        taxid = self.split_row(line)[-1]
                        if taxid != '9606':
                            taxid = False
                            break
                    elif line.startswith('!Series_type'):
                        series_type = self.split_row(line)[-1]
                    elif line.startswith('!Series_summary'):
                        summary = self.split_row(line)[-1]
                    if taxid and series_type and summary:
                        return {
                            'series_type': series_type,
                            'series_summary': summary,
                            'key': self.get_type(series_type, summary),
                        }
        except Exception as e:
            print(f"error={e}, path={self.infile}")
        return None

    def get_type(self, series_type:str, summary:str):
        _summary = summary.lower()
        _type = series_type.lower()

        if 'single-cell rna' in _summary and 'expression' in _type:
            if 'cell line' in _summary:
                return 'scrna-seq cell line'
            return 'scrna-seq other'

        pool = ('array', 'expression', 'methylation', 'genome binding',
            'genome variation', 'non-coding', 'sequencing')
        for i in pool:
            if i in _type:
                return i
        return 'other'

    def samples(self) -> tuple:
        '''
        search soft file given a GEO accession
        GEO accession GEOxxxxxx
        sample GEO accession: GSMxxxxxxx
        SRA: SRXxxxxxxxx
        Biosample: SAMNxxxxxxxx
        '''
        geo, _samples, curr = None, [], {}
        for line in self.line_iter():
            if line.startswith('!Series_geo_accession'):
                geo = self.split_row(line)[-1]
            elif line.startswith('^SAMPLE'):
                if curr:
                    _samples.append(curr)
                    curr = {}
                curr['sample'] = self.split_row(line)[-1]
            elif line.startswith('!Sample_relation'):
                if 'BioSample:' in line:
                    curr['SAMN'] = re.findall(r'SAMN\d*', line)
                if 'SRA:' in line:
                    curr['SRA'] = re.findall(r'SRX\d*', line)
        if curr:
            _samples.append(curr)
            curr = {}
        return geo, _samples

    def sample_id(self) -> tuple:
        '''
        get GEO, and sample_id
        '''
        geo, _ids = None, []
        for line in self.line_iter():
            if line.startswith('!Series'):
                if line.startswith('!Series_geo_accession'):
                    geo = self.split_row(line)[-1]
                elif line.startswith('!Series_sample_id'):
                    sample_id = self.split_row(line)[-1]
                    if sample_id not in _ids:
                        _ids.append(sample_id)
            elif line.startswith('^PLATFORM'):
                break
        return geo, _ids

    def pmid(self) -> tuple:
        '''
        get GEO, and pubmed_id
        '''
        geo, pmid = None, ''
        for line in self.line_iter():
            if line.startswith('!Series'):
                if line.startswith('!Series_geo_accession'):
                    geo = self.split_row(line)[-1]
                elif line.startswith('!Series_pubmed_id'):
                    pmid = self.split_row(line)[-1]
                    if geo:
                        return geo, pmid
            elif line.startswith('^PLATFORM'):
                break
        return geo, pmid

    def pmid_sampleid(self) -> tuple:
        '''
        pubmed_id ~ sample_id
        '''
        pmid, samples = None, []
        for line in self.line_iter():
            if line.startswith('!Series'):
                if line.startswith('!Series_pubmed_id'):
                    pmid = self.split_row(line)[-1]
                elif line.startswith('!Series_sample_id'):
                    sample_id = self.split_row(line)[-1]
                    samples.append(sample_id)
            elif line.startswith('^PLATFORM'):
                break
        return pmid, samples


    def filter_data(self, func=None) -> tuple:
        '''
        if return None, data, there is not such data meeting conditions
        '''
        file_name = os.path.basename(self.infile)
        data = {
            'GEO': file_name.split('_')[0],
            'local_soft_file': self.infile,
        }
        # parse data row by row
        if func:
            data = func(data)
        return data

    def parse_rows(self, data) -> list:
        '''
        infile is *.soft.gz
        '''
        key, rec = '', {}
        # names = ['DATABASE', 'SERIES', 'PLATFORM']
        for line in self.line_iter():
            if line.startswith('^'):
                # push rec to data before 
                if key not in data:
                    data[key] = []
                data[key].append(rec)
                # get new rec
                item = self.split_row(line)
                key = item[0]
                rec = {key: item[1]}
            elif line.startswith("!"):
                item = self.split_row(line)
                if item[0] not in rec:
                    rec[item[0]] = []
                rec[item[0]].append(item[1])
            else:
                if not line.startswith('#'):
                    k, v = rec[-1]
                    rec[-1] = (k, v + line)
        return data

    def print(self, data):
        for k, v in data.items():
            print(f"{k}\t{v}")