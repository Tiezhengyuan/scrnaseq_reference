'''
customize sample.labels
'''

class LabelSample:
    def __init__ (self, geo:str, sample:dict):
        '''
        _sample would be updated
        '''
        self.geo = geo
        self.sample = sample
        self.lb = self.sample['labels']

    def __call__(self):
        func = {
            "GSE112274": self.GSE112274,
            'GSE122960': self.GSE122960,
            "GSE121309": self.GSE121309,
            'GSE130148': self.GSE130148,
            'GSE132771': self.GSE132771,
            "GSE135851": self.GSE135851,
            'GSE135893': self.GSE135893,
            'GSE136831': self.GSE136831,
            'GSE140819': self.GSE140819,
            "GSE144357": self.GSE144357,
            "GSE145926": self.GSE145926,
            'GSE148071': self.GSE148071,
            'GSE148729': self.GSE148729,
            'GSE158055': self.GSE158055,
            'GSE162498': self.GSE162498,
            'GSE162499': self.GSE162499,
            'GSE162500': self.GSE162500,
            "GSE162936": self.GSE162936,
            'GSE164829': self.GSE164829,
            "GSE166037": self.GSE166037,
            "GSE166059": self.GSE166059,
            'GSE168710': self.GSE168710,
            'GSE180864': self.GSE180864,
            'GSE190510': self.GSE190510,
            'GSE280041': self.GSE280041,
            "GSE286399": self.GSE286399,
        }
        if self.geo in func:
            func[self.geo]()
        return None

    def _update(self, key:str, value:str):
        self.sample['labels'][key] = value

    def _healthy_control(self):
        self.sample['labels']['disease'] = 'healthy'
        self.sample['labels']['group'] = 'control'
        if 'disease_state' in self.lb:
            del self.sample['labels']['disease_state']

    def _disease_patient(self, disease_name:str, disease_state:str=None):
        self.sample['labels']['disease'] = disease_name
        self.sample['labels']['group'] = 'patient'
        if disease_state:
            self.sample['labels']['disease_state'] = disease_state

    def _protocol(self, value:str=None):
        if value is None:
            value = 'scrna-seq'
        if value not in self.sample['protocol']:
            self.sample['protocol'].append(value)

###################
    def GSE112274(self):
        if self.lb['cell_line'] == 'pc9':
            self._update('tissue', 'lung')


    def GSE122960(self):
        if self.lb['disease_state'] == 'donor':
            self._healthy_control()
        else:
            self._disease_patient('pulmonary fibrosis lung disease')
    
    def GSE121309(self):
        if self.lb['cell_line'] == 'h1299':
            self._update('tissue', 'lung')

    def GSE130148(self):
        self._protocol()
        self._protocol('dropseq')
        self._disease_patient('lung cancer')

    def GSE132771(self):
        self._protocol()
        if self.lb.get('disease_state') == 'normal':
            self._healthy_control()
        else:
            self._disease_patient('pulmonary fibrosis lung disease')
        self._update('technology', "10x3v2")

    def GSE135851(self):
        self._disease_patient('lymphangioleiomyomatosis lung disease')

    def GSE135893(self):
        self._protocol()
        if self.lb.get('disease_state'):
            self._disease_patient('pulmonary fibrosis lung disease')
        else:
            self._healthy_control()
        tech = "10x5\'" if 'VUILD53' in self.sample['sample_title'] else "10x3v2"
        self._update('technology', tech)

    def GSE136831(self):
        if self.lb.get('disease') == 'copd':
            self._disease_patient('chronic obstructive pulmonary lung disease')
        elif self.lb.get('disease') == 'ipf':
            self._disease_patient('idiopathic pulmonary fibrosis lung disease')
        elif self.lb.get('disease') == 'control':
            self._healthy_control()
        self._update('technology', "10x3v2")

    def GSE140819(self):
        title = self.sample['sample_title']
        if title.startswith('CLL'):
            self._disease_patient('chronic lymphocytic leukemia blood cancer')
        elif title.startswith('CY'):
            self._disease_patient('melanoma skin cancer')
        elif title.startswith('GBM'):
            self._disease_patient('glioblastoma brain cancer')
        elif title.startswith('HTAPP'):
            self._disease_patient('neuroblastoma')
        elif title.startswith('MBC'):
            self._disease_patient('metastatic breast cancer')
        elif title.startswith('MGH'):
            self._disease_patient('glioma brain cancer')
        elif title.startswith('NSCLC'):
            self._disease_patient('non-small cell lung cancer')

    def GSE144357(self):
        if self.lb['cell_line'] == "wi38-htert":
            self._update('cell_line', 'wi38')
            self._update('tissue', 'lung')
        elif self.lb['cell_line'] == 'nci-h1299':
            self._update('cell_line', 'h1299')
            self._update('tissue', 'lung')

    def GSE145926(self):
        if 'healthy' in self.lb['group']:
            self._healthy_control()
        else:
            if 'severe' in self.lb['group']:
                self._disease_patient('covid-19 infection', 'severe')
            else:
                self._disease_patient('covid-19 infection', self.lb['group'])

    def GSE148071(self):
        self._disease_patient('non-small cell lung cancer')

    def GSE148729(self):
        if self.lb.get('cell_line') == 'h1299':
            self._update('cell_type', "lung cancer cell line")
            self._update('tissue', "lung")
        elif self.lb.get('cell_line') == 'calu3':
            self._update('cell_type', "lung cancer cell line; adenocarcinoma")
            self._update('tissue', "lung")
        elif self.lb.get('cell_line') == 'caco2':
            self._update('cell_type', "colon cancer cell line; colorectal adenocarcinoma")
            self._update('tissue', 'large intestine; colon')

    def GSE158055(self):
        self._protocol()
        if self.sample['sample_title'].startswith('S-HC'):
            self._healthy_control()
        else:
            self._disease_patient('covid-19 infection', self.sample['characteristics'].get('covid-19_severity'))

    def GSE162498(self):
        self._disease_patient('non-small cell lung cancer', 'advanced')
        if self.lb['tissue'] == "nsclc tumor tissue":
            self._update('tissue', "lung; tumor tissue")
        elif self.lb['tissue'] == "nsclc juxta tissue":
            self._update('tissue', "lung; normal tissue")

    def GSE162499(self):
        self._disease_patient('non-small cell lung cancer', 'early')

    def GSE162500(self):
        self._disease_patient('non-small cell lung cancer')

    def GSE162936(self):
        self._protocol()
        if self.lb['cell_line'] == "rues2 human embryonic stem cell":
            self._update('cell_line', 'rues2')
        
    def GSE164829(self):
        self._healthy_control()
        self._protocol()

    def GSE166037(self):
        self._disease_patient('idiopathic pulmonary fibrosis lung disease')

    def GSE166059(self):
        # update cell_type
        if self.lb.get('cell_type') == 'nhbe':
            self._update('cell_type', 'normal human bronchial epithelial cells')
        elif self.lb.get('cell_type') == 'bec':
            self._update('cell_type', 'basal epithelial cells')
        elif self.lb.get('cell_type') == 'saec':
            self._update('cell_type', 'small airway epithelial cells')
        # disease
        if self.lb.get('disease') == 'normal':
            self._healthy_control()
        elif self.lb.get('disease') == 'ipf':
            self._disease_patient('idiopathic pulmonary fibrosis lung disease')

    def GSE168710(self):
        self._protocol()

    def GSE180864(self):
        self._protocol()

    def GSE190510(self):
        if 'patient' in self.lb.get('disease_state', ''):
            self._disease_patient('anti-synthetase syndrome-interstitial lung disease ')
        else:
            self._healthy_control()

    def GSE280041(self):
        self._protocol()
        self._update('kit', 'SMARTer Stranded Total RNA-seq kit v3 (TaKaRa Bio)')
        if self.lb.get('cell_line') in ('a549', 'h1299', 'h23', 'h358', 'hcc44'):
            self._update('cell_type', "lung cancer cell line")
        elif self.lb.get('cell_line') in ('a2058'):
            self._update('cell_type', "melanoma cell line")

    def GSE286399(self):
        if self.lb['cell_line'] == 'nci-h226':
            self._update('cell_line', 'h226')
            self._update('tissue', 'lung')
        elif self.lb['cell_line'] == 'nci-h1299':
            self._update('cell_line', 'h1299')
            self._update('tissue', 'lung')


        
       




