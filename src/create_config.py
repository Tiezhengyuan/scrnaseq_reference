import os
import json

class CreateConfig:
    def __init__(self, config_dir:str):
        self.config_dir = config_dir

    def fetch_geo(self, geo:list, samples:list, results_dir:str) -> str:
        '''
        ids used for nf-core/fetchngs
        '''
        outdir = os.path.join(self.config_dir, 'ids')
        if outdir is not None:
            if not os.path.isdir(outdir):
                os.mkdir(outdir)

        # build two files
        # ids file
        id_file = os.path.join(outdir, f"{geo}.csv")
        with open(id_file, 'w') as f1:
            f1.write('\n'.join(samples))
        # config file
        config_file = os.path.join(outdir, f"{geo}.config")
        raw_dir = os.path.join(results_dir, geo)
        with open(config_file, 'w') as f2:
            lines = [
                "process.ignoreAnyError.errorStrategy = \'ignore\'",
                f"params.input = \"{os.path.abspath(id_file)}\"",
                f"params.outdir = \"{raw_dir}\"",
            ]
            f2.write('\n'.join(lines))

        bash_file = os.path.join(outdir, f"{geo}.sh")
        with open(bash_file, 'w') as f3:
            cmd = "nextflow run nf-core/fetchngs -r 1.12.0 -profile docker -resume"
            cmd += ' -c ' + os.path.abspath(config_file)
            f3.write(cmd)
        return cmd
