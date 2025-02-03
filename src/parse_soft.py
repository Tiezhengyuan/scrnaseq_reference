import os
import gzip
from utils import Utils

from search_soft import SearchSoft

class ParseSoft:
    def __init__(self, local_dir:str, outdir:str=None):
        self.local_dir = local_dir
        self.url = 'ftp.ncbi.nlm.nih.gov/geo/series'
        self.soft_dir = os.path.join(self.local_dir, self.url)
        self.outdir = outdir

    def file_iter(self):
        '''
        scann entire download directory
        '''
        return Utils.file_pattern_iter(self.soft_dir, '.soft.gz')

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
                        line = line.rstrip()
            except:
                _path = infile.replace(self.local_dir, '')
                cmd = ['rm', infile, '&&', 'wget', '-c', '-r',
                    f'ftp://{_path}', self.local_dir, '\n']
            finally:
                if cmd:
                    with open(outfile, 'a') as f:
                        f.write(' '.join(cmd))

    def soft_url(self, geo:str):
        '''
        given GEO, return the endpoint in FTP
        '''
        i = geo[3:]
        k = i[:-3] if len(i) > 3 else ''
        k = "GSE" + k + 'nnn'
        soft_url = f"ftp://{self.url}/{k}/{geo}/soft"
        return soft_url

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

    def geo_pmid(self) -> tuple:
        '''
        GEO accession ~ pubmed_id
        '''
        res_geo, res_pmid = {}, {}
        for infile in self.file_iter():
            softer = SearchSoft(infile)
            geo, pmid = softer.pmid()
            if geo and pmid:
                res_geo = Utils.geo_update(res_geo, geo, [pmid,])
                res_pmid = Utils.pmid_update(res_pmid, pmid, [geo,])
        # export to geo_pmid.json
        file_geo = Utils.to_json(res_geo, self.outdir, 'geo_pmid.json')
        # export to pmid_geo.json
        file_pmid = Utils.to_json(res_pmid, self.outdir, 'pmid_geo.json')
        return file_geo, file_pmid

    def geo_sample_id(self) -> str:
        '''
        GEO accession ~ sample_id accession
        '''
        res = {}
        for infile in self.file_iter():
            softer = SearchSoft(infile)
            geo, _ids = softer.sample_id()
            if geo and _ids:
                res = Utils.geo_update(res, geo, _ids)
        # export to json
        outfile = Utils.to_json(res, self.outdir, 'geo_sampleid.json')
        return outfile

    def geo_samples(self) -> str:
        '''
        GEO accession ~ samples
        '''
        res = {}
        for infile in self.file_iter():
            softer = SearchSoft(infile)
            geo, samples = softer.samples()
            if geo and samples:
                res = Utils.geo_update(res, geo, samples)
        # export to json
        outfile = Utils.to_json(res, self.outdir, 'geo_samples.json')
        return outfile

    def pmid_samples(self) -> str:
        '''
        PMID ~ sample_id accession
        '''
        res = {}
        for infile in self.file_iter():
            softer = SearchSoft(infile)
            pmid, sample_ids = softer.pmid_sampleid()
            if pmid and sample_ids:
                res = Utils.pmid_update(res, pmid, sample_ids)
        # export to json
        outfile = Utils.to_json(res, self.outdir, 'pmid_samples.json')
        return outfile


