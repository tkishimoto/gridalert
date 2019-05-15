from logging import getLogger

logger = getLogger(__name__)

class GridAlertConf:

    def __init__(self):
   
        self.work_dir   = ''     

        self.db_conf    = DatabaseConf()
        self.aa_conf    = AnomalyAlertConf()
 
        self.base_confs = []
        self.dc_confs   = []
        self.tv_confs   = []
        self.vc_confs   = []
        self.dv_confs   = []


    def get_base_names(self):
        return [base_conf.name for base_conf in self.base_confs]
        

class DatabaseConf:

    def __init__(self):

        self.path         = '' 
        self.type         = 'sqlite3'

        self.table_name   = 'data' 
        self.column_names = ['tag', 'cluster', 'host', 'date', 
                             'service', 'metadata', 'data', 'label',
                             'prediction', 'feature', 'diff']
        self.column_types = ['text unique', 'text', 'text', 'text',
                             'text', 'text', 'text', 'text',
                             'text', 'text', 'text'] 
        
    def get_data_index(self, column):
        return self.column_names.index(column)
        
    def get_grid_index(self, column):
        return self.column_names.index(column)


class BaseConf:

    def __init__(self):
   
        self.name       = 'cluster'
        self.hosts      = ['.*']
        self.services   = ['service']
        self.date_start = '2000-01-01 00:00:00'
        self.date_end   = '2030-01-01 00:00:00'


class DataConverterConf:

    def __init__(self):
        self.text_type  = 'logwatch'
        self.text_path  = ''


class TextVectorizerConf:

    def __init__(self):

        self.type       = 'doc2vec'
        self.dir        = ''

        self.dm          = 1
        self.vector_size = 4
        self.window      = 8
        self.min_count   = 1
        self.workers     = 1
        self.epochs      = 5000
        self.seed        = 1234


class VectorClusterConf:

    def __init__(self):

        self.type          = 'isolationforest'
        self.dir           = ''
        
        self.behaviour     = 'new'
        self.n_estimators  = 500
        self.contamination = 'auto'
        self.random_state  = 42
        self.max_samples   = 1000


class DataVisualizerConf:

    def __init__(self):

        self.html_dir     = ''
        self.plot_dir     = ''

        self.use_diff      = True

class AnomalyAlertConf:

    def __init__(self):

        self.alert_filter = ''
