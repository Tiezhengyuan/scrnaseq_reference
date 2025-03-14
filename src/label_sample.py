'''
manually label data
customize sample.labels
'''

class LabelSample:
    def __init__(self, sample):
        self.sample = sample
        self.lb = sample['labels']

    def _update(self, key:str, value:str):
        self.sample['labels'][key] = value
    
    def _healthy_control(self):
        self.sample['labels']['disease'] = 'healthy'
        self.sample['labels']['group'] = 'control'
        if 'disease_state' in self.lb:
            del self.sample['labels']['disease_state']

    def _disease(self, disease_name:str):
        self.sample['labels']['disease'] = disease_name

    def _disease_patient(self, disease_name:str, disease_state:str=None):
        self.sample['labels']['disease'] = disease_name
        self.sample['labels']['group'] = 'patient'
        if disease_state:
            self.sample['labels']['disease_state'] = disease_state
    
    def _protocol(self, *args):
        '''
        *args: values
        '''
        if 'protocol' not in self.sample:
            self.sample['protocol'] = []
        for val in args:
            if val not in self.sample['protocol']:
                self.sample['protocol'].append(val.lower())

    def _tissue(self, *args):
        self._key('tissue', *args)

    def _key(self, name, *args):
        '''
        args: name could be protocol or tissue etc.
        *args: values
        '''
        if key not in self.sample:
            self.sample[key] = []
        for val in args:
            if val not in self.sample[key]:
                self.sample[key].append(val.lower())

    @property
    def desc(self):
        return self.sample.get('Sample_description', '')

    @property
    def title(self):
        return self.sample.get('sample_title', '')
    
    @property
    def cell_line(self):
        return self.sample['labels'].get('cell_line', '').lower()
    
    @property
    def cell_type(self):
        return self.sample['labels'].get('cell_type', '').lower()

    @property
    def tissue(self):
        return self.sample['labels'].get('tissue', '').lower()

    @property
    def disease(self):
        return self.sample['labels'].get('disease', '').lower()

    @property
    def disease_state(self):
        return self.sample['labels'].get('disease_state', '').lower()

    @property
    def group(self):
        return self.sample['labels'].get('group', '').lower()

###################
    def filter(self, name:str):
        match name:
            case 'scrnaseq_lung_cell_line':
                return self.filter_scrnaseq_lung_cell_line()
            case 'scrnaseq_lung_tissue_healthy':
                return self.filter_scrnaseq_lung_tissue_healthy()
            case 'scrnaseq_lung_tissue_patient':
                return self.filter_scrnaseq_lung_tissue_patient()
            case 'scrnaseq_breast_tissue_patient':
                return self.filter_scrnaseq_breast_tissue_patient()


    def filter_human(self):
        if self.sample['sample_taxid'] == '9606':
            return True
        return False

    def filter_scrnaseq(self):
        if 'scrna-seq' in self.sample.get('protocol', []):
            if 'BioSample' in self.sample:
                return True
        return False

    def filter_scrnaseq_lung_cell_line(self) -> bool:
        if self.filter_scrnaseq() and self.filter_human():
            if 'lung' in self.cell_type:
                return True
        return False

    def filter_scrnaseq_lung_tissue_healthy(self) -> bool:
        if self.filter_scrnaseq() and self.filter_human():
            if 'lung' in self.tissue and ('cell_line' not in self.lb) \
                and self.disease == 'healthy':
                    return True
        return False

    def filter_scrnaseq_lung_tissue_patient(self) -> bool:
        if self.filter_scrnaseq() and self.filter_human():
            if 'lung' in self.tissue and ('cell_line' not in self.lb) \
                and self.disease != 'healthy':
                return True
        return False

    def filter_scrnaseq_breast_tissue_patient(self) -> bool:
        if self.filter_scrnaseq() and self.filter_human():
            if 'breast' in self.tissue and ('cell_line' not in self.lb) \
                and self.disease != 'healthy':
                return True
        return False