'''
retrieve urls of fastq given SRR accessions
'''
import os
import json

from utils import Utils
from retrieve_url import RetrieveUrl

def main():
    # prepare dataset
    results_dir = os.path.dirname(os.path.dirname(__file__))
    outdir = os.path.join(results_dir, 'results')
    file_name = 'srr_fastq_urls_1.json'
    json_file = os.path.join(outdir, file_name)
    data = Utils.from_json(json_file)

    # initialize or update keys of the first layers
    if not data:
        root_pool = RetrieveUrl.scan(['/vol1/fastq',], 'SRR')
        RetrieveUrl.merge(data, root_pool)
        print('Number of prefix of SRR accessions:', len(data['vol1']['fastq']))

    #epochs: retrieve and merge URLs of *.fastq.gz into data
    print(f"Try to update data", end=": ")
    for _ in range(100):
        # get query keys
        query_pool = []
        Utils.depth_first_scan(data, '', query_pool)
        if not query_pool:
            break
        # retrieve
        next_pool = RetrieveUrl.scan(query_pool)
        #  update
        RetrieveUrl.merge(data, next_pool)
        print(len(next_pool), end=', ')    

    #save
    outfile = Utils.to_json(data, outdir, file_name)
    print(f"Finally, {outfile} is updated.")

if __name__ == "__main__":
    main()

