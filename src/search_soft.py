import os
import gzip
import json
from typing import Iterable

class SearchSoft:
    def __init__(self, soft_file:str):
        '''
        soft_file should be *.gz format
        '''
        self.infile = soft_file

    def split_row(self, line) -> tuple:
        items = line[1:].split(" = ", 1)
        key = items[0]
        val = items[1] if len(items) == 2 else ''
        return key, val

    def line_iter(self):
        '''
        '''
        try:
            with gzip.open(self.infile, 'rt') as f:
                for line in f:
                    line = str(line.rstrip())
                    yield line
        except Exception as e:
            print(infile)

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
            item = func(path)
            if item:
                data.update(item)
                return data
        return data

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
            # print(f"error={e}, path={self.infile}")
            pass
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

    def sample_ids(self):
        '''
        search soft file given a GEO accession
        geo: GEO accession
        return SRR
        '''
        samples = []
        for line in self.line_iter():
            if line.startswith('!Series_sample_id'):
                sample_id = self.split_row(line)[-1]
                if sample_id not in samples:
                    samples.append(sample_id)
        return samples

    def pmid(self):
        '''
        get GEO, and pubmed_id
        '''
        geo, pmid = None, ''
        for line in self.line_iter():
            if line.startswith('!Series_geo_accession'):
                geo = self.split_row(line)[-1]
            elif line.startswith('!Series_pubmed_id'):
                pmid = self.split_row(line)[-1]
                if geo:
                    return geo, pmid
        return geo, pmid

    def parse_rows(self, data) -> list:
        '''
        infile is *.soft.gz
        '''
        n =0
        names = ['DATABASE', 'SERIES', 'PLATFORM', 'SAMPLES']
        with gzip.open(self.infile, 'rt') as f:
            rec = []
            for line in f:
                n+=1
                if n%1000==0:
                    print(n, end=', ')
                if names == []:
                    break
                line = str(line.rstrip())
                if line.startswith('^'):
                    # push rec to data before 
                    rec = dict(rec)
                    for i in names:
                        if i in rec:
                            data[i] = rec
                            names.remove(i)
                            break
                    # get new rec
                    item = self.split_row(line)
                    rec = [item,]
                elif line.startswith("!"):
                    item = self.split_row(line)
                    rec.append(item)
                else:
                    if not line.startswith('#'):
                        k, v = rec[-1]
                        rec[-1] = (k, v + line)
        return data