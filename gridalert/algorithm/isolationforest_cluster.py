from logging import getLogger

logger = getLogger(__name__)

import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

from .base_cluster import *

class IsolationforestCluster(BaseCluster):

    def __init__(self, cl_conf):
        super().__init__(cl_conf)


    def create_model(self, data, tags, model_path):

        data = np.array(data)

        cl_conf = self.cl_conf

        max_samples = int(cl_conf['cluster_max_samples'])
        contamination = cl_conf['cluster_contamination']
        max_features = cl_conf['cluster_max_features']
        bootstrap = cl_conf['cluster_bootstrap']
        behaviour = cl_conf['cluster_behaviour']

        if max_samples > len(data):
            max_samples = len(data)
            logger.warn('max_samples set to %s' % len(data))

        if contamination != 'auto':
            contamination = float(contamination)

        if max_features.isdigit():
            max_features = int(max_features)
        else:
            max_features = float(max_features)

        if bootstrap == 'True':
            bootstrap = True
        else:
            bootstrap = False

        # not allowed
        if (contamination == 'auto') and (behaviour == 'old'):
            return

        model = IsolationForest(n_estimators=int(cl_conf['cluster_n_estimators']),
                                max_samples=max_samples,
                                contamination=contamination,
                                max_features=max_features,
                                bootstrap=bootstrap,
                                n_jobs=int(cl_conf['cluster_n_jobs']),
                                behaviour=cl_conf['cluster_behaviour'],
                                random_state=int(cl_conf['cluster_random_state']))
        model.fit(data)
        pred_data = model.predict(data)

        #self.dump_to_db(tags, pred_data, data)

        pickle.dump(model, open(model_path, 'wb'))

        return pred_data

