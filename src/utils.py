import gzip
import os
import json
import re
from typing import Iterable

class Utils:

    @staticmethod
    def init_dir(outdir:str, names:list=None):
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        while names:
            name = names.pop(0)
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
    def fastq_gz_path(acc:str, local_dir:str=None) -> str:
        try:
            name = acc + '.fastq.gz'
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    if name in file:
                        return os.path.join(root, file)
        except Exception as e:
            pass
        return None
                
        
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
    def geo_update(data:dict, key:str, value:list) -> dict:
        k1 = key[:-3]
        if k1 in data:
            if key not in data[k1]:
                data[k1][key] = value
            else:
                data[k1][key] +=  value
        else:
            data[k1] = {
                key: value
            }
        return data
    
    @staticmethod
    def geo_get(data:dict, geo:str):
        k1 = geo[:-3]
        if k1 in data:
            values = data[k1].get(geo, [])
            values.sort()
            return values
        return None

    @staticmethod
    def pmid_update(data:dict, key:str, value:list) -> dict:
        k1 = key[:3]
        if k1 in data:
            if key not in data[k1]:
                data[k1][key] = value
            else:
                data[k1][key] += value
        else:
            data[k1] = {
                key: value
            }
        return data

    @staticmethod
    def pmid_get(data:dict, pmid:str):
        pmid = str(pmid)
        k1 = pmid[:3]
        if k1 in data:
            values = data[k1].get(pmid, [])
            values.sort()
            return values
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
