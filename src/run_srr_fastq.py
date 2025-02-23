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
    # version 1
    file_name = 'srr_fastq_urls_1.json'
    json_file = os.path.join(outdir, file_name)
    data = Utils.from_json(json_file)

    # initialize or update keys of the first layers
    if not data:
        root_pool = RetrieveUrl.scan(['/vol1/fastq',], 'SRR')
        RetrieveUrl.merge(data, root_pool)
        n = len(data['vol1']['fastq'])
        print('Number of prefix of SRR accessions:', n)

    #epochs: retrieve and merge URLs of *.fastq.gz into data    
    print(f"Try to update data", end=": ")
    for i in range(1_000):
        query_pool = []
        try:
            # get query keys
            Utils.depth_first_scan(data, '', query_pool)
            if not query_pool:
                break
            # retrieve
            next_pool = RetrieveUrl.scan(query_pool)
            #  update
            RetrieveUrl.merge(data, next_pool)
            print(len(next_pool), end=', ')    

            #save
            if next_pool:
                outfile = Utils.to_json(data, outdir, file_name)
                print(f"The file {outfile} is updated.")
        except Exception as e:
            print(f"Warning: Iteration of retrieval stopped at {i}! error={e}.")



if __name__ == "__main__":
    main()

