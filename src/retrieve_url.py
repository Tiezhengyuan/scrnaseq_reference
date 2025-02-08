'''
retrive URLs
'''
import ftplib
import json
import re
import os
import subprocess
from typing import Iterable

from utils import Utils
from slicer import Slicer

class RetrieveUrl:
    url = 'ftp.sra.ebi.ac.uk'

    @staticmethod
    def ftp_sra_ebi(srr_acc:str) -> list:
        '''
        arg: SRR accession
        parse SRRxxxx ~ URLs of fastq files
        retrun URLs of *.fastq.gz files
        '''
        ftp = ftplib.FTP(
            host=RetrieveUrl.url,
            user='anonymous',
            passwd='anonymous',
            encoding='utf-8'
        )

        gz = []
        keys = Slicer.SRR(srr_acc)
        path = ['vol1', 'fastq'] + keys
        try:
            # change directory
            ftp.cwd('/'.join(path))
            # retrieve gz names
            gz = ftp.nlst()
            endpoint = RetrieveUrl.url + str(ftp.pwd())
            gz = [os.path.join(endpoint, i) for i in gz]
        except Exception as e:
            print(e)
        
        ftp.quit()
        return gz

    @staticmethod
    def get_gz(ftp, srr_acc) -> list:
        '''
        ftp: ftp object created by ftplib.FTP
        srr_acc: SRR accessions as endpoint
        '''
        ftp.cwd(srr_acc)
        gz = ftp.nlst()
        endpoint = RetrieveUrl.url + ftp.pwd()
        gz = [f"{endpoint}/{i}" for i in gz]
        ftp.cwd('..')
        return gz

    @staticmethod
    def scan_sra_ebi(data:dict):
        '''
        SRR accession ~ FTP URLs of *.gz files
        '''
        try:
            ftp = ftplib.FTP(
                host=RetrieveUrl.url,
                encoding='utf-8',
                user='anonymous',
                passwd='anonymous'
            )
            ftp.cwd('/vol1/fastq')
            for prefix in ftp.nlst():
                if prefix.startswith('SRR'):
                    data[prefix] = {}
                    ftp.cwd(prefix)
                    for postfix in ftp.nlst():
                        if postfix.startswith('SRR'):
                            data[prefix][postfix] = RetrieveUrl.get_gz(ftp, postfix)
                        else:
                            ftp.cwd(postfix)
                            for srr_acc in ftp.nlst():
                                data[prefix][srr_acc] = RetrieveUrl.get_gz(ftp, srr_acc)
                            ftp.cwd('..')
                    ftp.cwd('..')
            ftp.quit()
        except Exception as e:
            print(f"error={e}")

    @staticmethod
    def scan(endpoints_pool:list, pattern:str=None):
        '''
        retrieve endpoints given its path in FTP
        '''
        res = []
        try:
            ftp = ftplib.FTP(
                host=RetrieveUrl.url,
                encoding='utf-8',
                user='anonymous',
                passwd='anonymous'
            )
            for path in endpoints_pool:
                ftp.cwd(path)
                items = ftp.nlst() if pattern is None else \
                    [i for i in ftp.nlst() if i.startswith(pattern)]
                res.append((path,items))
        except Exception as e:
            print(f"error={e}, path={path}")
        return res

    @staticmethod
    def merge(data:dict, endpoints_pool:list):
        '''
        merge contents of direcotries into data.
        The contents = file name -> value of data
        The content = directory name -> key of data
        '''
        # path is expressed in list type rather than string
        for path, endpoints in endpoints_pool:
            keys = [i for i in path.split('/') if i]
            gz = []
            for end in endpoints:
                # the end is file name
                if end.endswith('.fastq.gz'):
                    gz.append(end)
                else:
                    Utils.key_update(data, keys + [end,], {})
            if gz:
                Utils.key_update(data, keys, gz)