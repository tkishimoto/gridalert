from logging import getLogger

logger = getLogger(__name__)

import pickle
import numpy as np

from sklearn.cluster import DBSCAN

from .base_cluster import *

class DbscanCluster(BaseCluster):

    def __init__(self, cl_conf):
        super().__init__(cl_conf)


    def create_model(self, data, tags, model_path):
        data = np.array(data)

        cl_conf = self.cl_conf
        model = DBSCAN(eps=float(cl_conf['cluster_eps']),
                       min_samples=int(cl_conf['cluster_min_samples']),
                       metric=cl_conf['cluster_metric'],
                       algorithm=cl_conf['cluster_algorithm'],
                       leaf_size=int(cl_conf['cluster_leaf_size']),
                       n_jobs=int(cl_conf['cluster_n_jobs']))
        model.fit(data)
        pred_data = model.labels_

        pickle.dump(model, open(model_path, 'wb'))
    
        return pred_data


    def predict(self, data, model_path):

        model = pickle.load(open(model_path, 'rb'))
        pred_data = cluster_model.labels_

        return pred_data

