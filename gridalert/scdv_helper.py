from logging import getLogger

logger = getLogger(__name__)

import numpy as np

from gensim.models import Word2Vec
from sklearn.mixture import GaussianMixture
from sklearn.feature_extraction.text import TfidfVectorizer,HashingVectorizer

from .util import text as util_text

class ScdvHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]

        self.num_clusters = int(self.cl_conf['vector_clusters'])
        self.num_features = int(self.cl_conf['vector_size'])


    def create_model(self, data):

        docs_list = []
        docs      = []

        for doc in data:
            if self.cl_conf['vector_jp_num'] == 'True':
                doc = util_text.filter_doc(doc)

            docs_list.append(doc.split())
            docs.append(doc)

        cl_conf = self.cl_conf
        model = Word2Vec(docs_list, 
                         workers=int(cl_conf['vector_workers']), 
                         hs = int(cl_conf['vector_hs']), 
                         negative = int(cl_conf['vector_negative']), 
                         iter = int(cl_conf['vector_epochs']),
                         size=int(cl_conf['vector_size']), 
                         min_count=int(cl_conf['vector_min_count']), 
                         window=int(cl_conf['vector_window']), 
                         sample=float(cl_conf['vector_sample']), 
                         seed=int(cl_conf['vector_seed']))


        model.init_sims(replace=True)
        
        word_vectors = model.wv.syn0
        idx, idx_proba = self.cluster_GMM(self.num_clusters,
                                          word_vectors)
        word_id_map = dict(zip(model.wv.index2word, idx))
        word_prob_map = dict(zip(model.wv.index2word, idx_proba))

        tfv = TfidfVectorizer(dtype=np.float32)
        tfidfmatrix_traindata = tfv.fit_transform(docs)
        featurenames = tfv.get_feature_names()
        idf = tfv._tfidf.idf_

        word_idf_dict = {}
        for pair in zip(featurenames, idf):
            word_idf_dict[pair[0]] = pair[1]

        prob_wordvecs = self.get_probability_word_vectors(featurenames, 
                                                     word_id_map, 
                                                     self.num_clusters, 
                                                     word_idf_dict)

        shelve_dict = {'word_id_map': word_id_map,
                       'word_prob_map': word_prob_map,
                       'word_idf_dict': word_idf_dict,
                       'prob_wordvecs': prob_wordvecs}

        return shelve_dict


    def get_vector(self, data):
        gwbowv = np.zeros(data, 
                          self.num_clusters*serlf.num_features, 
                          dtype="float32")
  
        counter = 0
        min_no = 0
        max_no = 0

        for doc in data:
            gwbowv[counter] = create_cluster_vector_and_gwbowv(doc.split(), train=True)
            counter += 1

    def cluster_GMM(self, num_clusters, word_vectors):
        clf =  GaussianMixture(n_components=num_clusters,
                    covariance_type="tied", init_params='kmeans', max_iter=50)
        clf.fit(word_vectors)
        idx = clf.predict(word_vectors)
        idx_proba = clf.predict_proba(word_vectors)
        return (idx, idx_proba)


    def get_probability_word_vectors(self,featurenames, 
                                     word_centroid_map, 
                                     num_clusters, 
                                     word_idf_dict):

        prob_wordvecs = {}
        for word in word_centroid_map:
            prob_wordvecs[word] = np.zeros(self.num_clusters * self.num_features, dtype="float32" )
            for index in range(0, num_clusters):
                try:
                    prob_wordvecs[word][index*num_features:(index+1)*num_features] = model[word] * word_centroid_prob_map[word][index] * word_idf_dict[word]
                except:
                    continue

        return prob_wordvecs


    def create_cluster_vector_and_gwbowv(wordlist, train=False):
        bag_of_centroids = np.zeros(self.num_clusters * self.num_features, dtype="float32")


