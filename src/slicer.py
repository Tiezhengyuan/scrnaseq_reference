'''
slice accession numbers for performance index
'''
import re


class Slicer:

    @staticmethod
    def GEO(acc:str):
        '''
        start with GEO follwed by 6-7 digits
        https://ftp.ncbi.nlm.nih.gov/geo/series
        '''
        prefix = acc[:-3] + 'nnn'
        return [prefix, acc]

    @staticmethod
    def SRR(acc:str):
        '''
        start with SRR followed by 6-8 digits
        https://ftp.sra.ebi.ac.uk/vol1/fastq
        '''
        prefix = acc[:6] 
        mid = acc[9:].zfill(3)
        return [prefix, mid, acc]

    @staticmethod
    def BioSample(acc:str):
        '''
        BioSample accession
        start with SAM followed by 1 alphabeical and 6-7 digits
        '''
        prefix = acc[:6] 
        mid = acc[9:].zfill(3)
        return [prefix, mid, acc]

    @staticmethod
    def SRX(acc:str):
        '''
        start with SRX followed by 6-7 digits
        '''
        prefix = acc[:6] 
        return [prefix, acc]

    @staticmethod
    def PMID(acc):
        '''
        6-8 digits
        '''
        acc = str(acc)
        prefix = acc[:3] 
        return [prefix, acc]