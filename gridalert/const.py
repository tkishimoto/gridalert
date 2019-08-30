from logging import DEBUG, INFO, WARN, ERROR, CRITICAL

class Const:
    LOG_LEVEL = [CRITICAL, ERROR, WARN, INFO, DEBUG]

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

    # Template fixed parameters
    LOGPARAMS = ['host', 'date', 'service', 'metadata',
                   'data', 'label']

    # tuning parameters
    MLVECPARAMS = ['vector_dm', 
                'vector_size',
                'vector_window',
                'vector_alpha',
                'vector_min_alpha',
                'vector_seed',
                'vector_min_count',
                'vector_sample',
                'vector_workers', 
                'vector_epochs',
                'vector_hs',
                'vector_negative',
                'vector_ns_exponent',
                'vector_dm_mean',
                'vector_dm_concat',
                'vector_dm_tag_count',
                'vector_dbow_words',
                'vector_model',
                'vector_min_count_label',
                'vector_minn',
                'vector_maxn',
                'vector_word_ngrams',
                'vector_loss',
                'vector_bucket',
                'vector_lr_update_rate',]

    MLCLSPARAMS = ['cluster_n_estimators', 
                'cluster_max_samples',
                'cluster_contamination',
                'cluster_max_features',
                'cluster_bootstrap',
                'cluster_n_jobs', 
                'cluster_behaviour',
                'cluster_random_state', 
                'cluster_eps', 
                'cluster_min_samples',
                'cluster_metric',
                'cluster_algorithm',
                'cluster_leaf_size']      

    MLPARAMS = MLVECPARAMS + MLCLSPARAMS         
