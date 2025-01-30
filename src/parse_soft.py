import os
import gzip
import json
from typing import Iterable

from search_soft import SearchSoft

class ParseSoft:
    def __init__(self, local_dir):
        self.local_dir = local_dir
        self.url = 'ftp.ncbi.nlm.nih.gov/geo/series'
        self.soft_dir = os.path.join(self.local_dir, self.url)

    def file_iter(self) -> str:
        '''
        scann entire download directory
        '''
        n = 0
        for root, dirs, files in os.walk(self.soft_dir):
            for file in files:
                if file.endswith('.soft.gz'):
                    n += 1
                    path = os.path.join(root, file)
                    if n % 5_000 == 0:
                        print(n, end=', ')
                    yield path

    def soft_local_path(self, geo:str):
        '''
        given GEO accession, return path of local soft file
        '''
        i = geo[3:]
        k = i[:-3] if len(i) > 3 else ''
        k = "GSE" + k + 'nnn'
        local_path = os.path.join(self.soft_dir, k, geo, 'soft')
        for file_name in os.listdir(local_path):
            if file_name.endswith('.soft.gz'):
                return os.path.join(local_path, file_name)
        return None

    def geo_pmid(self, outdir:str) -> str:
        '''
        pubmed_id to GEO accession
        '''
        outfile = os.path.join(outdir, 'geo_pmid.csv')
        with open(outfile, 'w') as f:
            f.write("GEO,PMID\n")
            for infile in self.file_iter():
                softer = SearchSoft(infile)
                geo, pmid = softer.pmid()
                if geo:
                    f.write(f"{geo},{pmid}\n")
        return outfile

    def validate_soft(self, outfile:str):
        '''
        scan all soft*.gz and validate those readable
        if not, delete and download them again.
        return shell commands to outfile
        '''
        if os.path.isfile(outfile):
            os.remove(outfile)
        
        for infile in self.file_iter():
            cmd = None
            softer = SearchSoft(infile)
            try:
                with gzip.open(infile, 'rt') as f:
                    for line in f:
                        line = str(line.rstrip())
            except:
                _path = infile.replace(self.local_dir, '')
                cmd = ['rm', infile, '&&', 'wget', '-c', '-r',
                    f'ftp://{_path}', self.local_dir, '\n']
            finally:
                if cmd:
                    with open(outfile, 'a') as f:
                        f.write(' '.join(cmd))




