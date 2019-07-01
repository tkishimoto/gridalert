from logging import getLogger

logger = getLogger(__name__)

from fastText import train_unsupervised
from fastText import load_model

from .base_vector import *

class FasttextVector(BaseVector):

    def __init__(self, cl_conf):
        super().__init__(cl_conf)


    def create_model(self, data, tags, model_path):

        text_path = self.cl_conf['model_dir'] + '/fasttext.tmp'

        trainings = open(text_path, 'w', errors='replace')

        for doc, tag in zip(data, tags):
            trainings.write('%s\n' % doc)

        trainings.close()

        cl_conf = self.cl_conf
        verbose = 2
        if int(cl_conf['log_level']) <= 1:
            verbose = 0

        model = train_unsupervised(text_path,
                        model = cl_conf['vector_model'],
                        lr = float(cl_conf['vector_alpha']),
                        dim = int(cl_conf['vector_size']),
                        ws = int(cl_conf['vector_window']),
                        epoch = int(cl_conf['vector_epochs']),
                        minCount = int(cl_conf['vector_min_count']),
                        minCountLabel = int(cl_conf['vector_min_count_label']),
                        minn = int(cl_conf['vector_minn']),
                        maxn = int(cl_conf['vector_maxn']),
                        neg = int(cl_conf['vector_negative']),
                        wordNgrams = int(cl_conf['vector_word_ngrams']),
                        loss = cl_conf['vector_loss'],
                        bucket = int(cl_conf['vector_bucket']),
                        lrUpdateRate = int(cl_conf['vector_lr_update_rate']),
                        thread = int(cl_conf['vector_workers']),
                        t = float(cl_conf['vector_sample']),
                        verbose = verbose)

        model.save_model(model_path)


    def get_vector(self, docs, model_path):

        model = load_model(model_path)
    
        data = []
        for doc in docs:

            tmp_doc = doc.replace('\n', '')
            vector = model.get_sentence_vector(tmp_doc).tolist()

            data.append(vector)
 
        return data

