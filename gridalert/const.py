
class Const:

    NORMAL = 1
    ABNORMAL = -1

    INVALID  = 9999

    # Database fixed parameters
    DB_TABLE_NAME = 'data'
    DB_COLUMN_NAMES = ['tag', 'cluster', 'host',
                       'date', 'service', 'metadata',
                       'data', 'label', 'prediction',
                       'feature', 'diff']

    DB_COLUMN_TYPES = ['text unique', 'text', 'text', 
                       'text', 'text', 'text', 
                       'text', 'text', 'text',
                        'text', 'text']

