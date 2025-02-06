import gzip
import os
import json
import re
from typing import Iterable

class Utils:

    @staticmethod
    def init_dir(outdir:str, names:list=None):
        '''
        create nested directories
        '''
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        for name in names:
            outdir = os.path.join(outdir, name)
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
        return outdir

    @staticmethod
    def file_iter(indir:str) -> Iterable:
        '''
        scann entire download directory
        '''
        n = 0
        for root, dirs, files in os.walk(indir):
            for file in files:
                n += 1
                path = os.path.join(root, file)
                if n % 5_000 == 0:
                    print(n, end=', ')
                yield path

    @staticmethod
    def file_pattern_iter(indir:str, pattern:str) -> Iterable:
        '''
        scann entire download directory
        '''
        n = 0
        for root, dirs, files in os.walk(indir):
            for file in files:
                if file.endswith(pattern):
                    n += 1
                    path = os.path.join(root, file)
                    if n % 5_000 == 0:
                        print(n, end=', ')
                    yield path

    @staticmethod
    def gz_iter(infile):
        '''
        iterate lines of gz file
        '''
        try:
            with gzip.open(infile, 'rt') as f:
                for line in f:
                    line = str(line.rstrip())
                    yield line
        except Exception as e:
            # print(infile)
            pass

    @staticmethod
    def fastq_gz_path(acc:str, local_dir:str=None) -> dict:
        '''
        search ge file give accession.
        for example: acc = 'GEO10405' -> GEO10405.fastq.gz
        '''
        fastq = {}
        name1, name2 = acc + '.fastq.gz', acc + '.fq.gz'
        for path in Utils.file_iter(local_dir):
            file_name = os.path.basename(path)
            if name1 in file_name or name2 in file_name:
                if '_R2' in file_name:
                    if 'R2' in fastq:
                        fastq['R2'] += ',' + path
                    else:
                        fastq['R2'] = path
                else:
                    if 'R1' in fastq:
                        fastq['R1'] += ',' + path
                    else:
                        fastq['R1'] = path
        return fastq

    def json_iter(data_dir:str):
        '''
        scan all data from json
        '''
        file_iter = Utils.file_pattern_iter(data_dir, '.json')
        for path in file_iter:
            yield Utils.from_json(path)                
        
    @staticmethod
    def to_json(data, outdir, file_name):
        '''
        save data into json
        '''
        try:
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
            outfile = os.path.join(outdir, file_name)
            with open(outfile, 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
            return outfile
        except Exception as e:
            print(f"Error: Failure in export data to json {outfile}, error={e}")
        return None

    @staticmethod
    def from_json(infile):
        '''
        get data from json
        '''
        try:
            with open(infile, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error: Failure in load data from json {infile}, error={e}")
        return None


    @staticmethod
    def key_update(data:dict, keys:list, values:list) -> dict:
        '''
        assign values into nested dict
        '''
        _data = data
        if len(keys) > 1:
            for key in keys[:-1]:
                if key not in _data:
                    _data[key] = {}
                _data = _data[key]
        # update value
        last = keys[-1]
        if last in _data:
            _data[last] += values
        else:
            _data[last] = values
        return data

    @staticmethod
    def key_get(data:dict, keys:list):
        '''
        get value from nested dictionary
        '''
        if not keys:
            return data
        key = keys[0]
        if key not in data:
            return []
        _data = data[key]
        return Utils.key_get(_data, keys[1:])

    @staticmethod
    def rename_key(data:dict, key1:str, key2:str):
        '''
        rename key2 to key1
        '''
        if key2 in data:
            data[key1] = data[key2]
            del data[key2]
        return data