from logging import getLogger

logger = getLogger(__name__)

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from .base_vector import *

class Doc2vecVector(BaseVector):

    def __init__(self, cl_conf):
        super().__init__(cl_conf)


    def create_model(self, data, tags, model_path):

        trainings = []
        for doc, tag in zip(data, tags):
            trainings.append(TaggedDocument(words=doc.split(),
                             tags=[tag]))

        cl_conf = self.cl_conf
    
        update = False
        if cl_conf['vector_update'] == 'True':
            update = True

        if update:
            model = Doc2Vec.load(model_path)
        
        else:
            model = Doc2Vec(dm = int(cl_conf['vector_dm']),
                        vector_size = int(cl_conf['vector_size']),
                        window = int(cl_conf['vector_window']),
                        alpha = float(cl_conf['vector_alpha']),
                        min_alpha = float(cl_conf['vector_min_alpha']),
                        seed = int(cl_conf['vector_seed']),
                        min_count = int(cl_conf['vector_min_count']),
                        sample = float(cl_conf['vector_sample']),
                        workers = int(cl_conf['vector_workers']),
                        epochs = int(cl_conf['vector_epochs']),
                        hs = int(cl_conf['vector_hs']),
                        negative = int(cl_conf['vector_negative']),
                        ns_exponent = float(cl_conf['vector_ns_exponent']),
                        dm_mean = int(cl_conf['vector_dm_mean']),
                        dm_concat = int(cl_conf['vector_dm_concat']),
                        dm_tag_count = int(cl_conf['vector_dm_tag_count']),
                        dbow_words = int(cl_conf['vector_dbow_words']))

        model.build_vocab(trainings, update=update)
        model.train(trainings,
                    total_examples=model.corpus_count,
                    epochs=model.epochs)

        model.save(model_path)

        return


    def get_vector(self, docs, model_path):
        data = []

        model = Doc2Vec.load(model_path)
        model.random.seed(int(self.cl_conf['vector_seed']))

        for doc in docs:
            tmp_doc = doc.replace('\n', '').split()

            vector = model.infer_vector(tmp_doc).tolist()
            model.random.seed(int(self.cl_conf['vector_seed']))

            data.append(vector)

        return data

