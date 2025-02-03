import os
import gzip
import sys

class Validate:
    def __init__(self, infile):
        self.infile = infile

    def line_iter(self):
        '''
        '''
        try:
            with gzip.open(self.infile, 'rt') as f:
                for line in f:
                    line = str(line.rstrip())
                return True
        except Exception as e:
            return False


if __name__ == "__main__":
    res = False
    infile = sys.argv[1]
    if os.path.isfile(infile):
        cl = Validate(infile)
        res = cl.line_iter()
    # 
    print(res)
