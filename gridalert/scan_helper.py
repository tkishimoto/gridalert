from logging import getLogger

logger = getLogger(__name__)

import os
import sys
import pickle
import tqdm
import pprint
import shutil

from io import StringIO
from itertools import product
from multiprocessing import Pool

from .text_vectorizer import *
from .vector_cluster import *

from .const import Const as const
from .util import hash as util_hash

class ScanHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cluster    = cluster

        self.db_conf    = conf['db']
        self.cl_conf    = conf[cluster]


    def scan(self):
        params = []

        for param in const.MLPARAMS:
            params.append(self.cl_conf[param].split(','))

        counter = 0
        args = []

        for param in product(*params):
            counter += 1

        for param in product(*params):
            for ii, value in enumerate(param):
                self.conf.set(self.cluster,
                              const.MLPARAMS[ii],
                              value)
            hash = util_hash.md5([self.cluster] + list(param))
            hash_dir = self.cl_conf['base_dir'] + '/' + hash
            self.conf.set(self.cluster, 'model_dir', hash_dir)
            rep = pickle.dumps(self.conf)
            conf_tmp = pickle.loads(rep)
            args.append([param, conf_tmp, self.cluster])

        with Pool(int(self.cl_conf['scan_pool'])) as pool:
            results = list(tqdm.tqdm(pool.imap(self.scan_wrapper, args), total=counter))

        results_dict = {}
        for result in results:
            for service in result:
                name = service['service']
                if name in results_dict.keys():
                    results_dict[name].append(service)
                else:
                    results_dict[name] = [service]

        for key, value in results_dict.items():
            acc_sort = sorted(value, key=lambda x:-x['sort'])

            print('inf> ranking of %s' % key)
            for acc in acc_sort:
                message = 'inf> acc (normal)=%s, acc (anomaly)=%s, ' % ('{:.3f}'.format(acc['acc1']),
                                                                        '{:.3f}'.format(acc['acc0']))
                message += 'time=%ss (%ss, %ss)' % ('{:.1f}'.format(acc['vector_time'] + acc['cluster_time']),
                                                 '{:.1f}'.format(acc['vector_time']),
                                                 '{:.1f}'.format(acc['cluster_time']))

                print(message)
                pprint.pprint(acc)


    def scan_wrapper(self, args):
        return self.scan_process(*args)


    def scan_process(self, param, conf, cluster):
        for ii, value in enumerate(param):
            key = const.MLPARAMS[ii]
            logger.info('%s : %s' % (key, conf[cluster][key]))

        os.makedirs(conf[cluster]['model_dir'], exist_ok=True)

        tv = TextVectorizer(conf, cluster)
        vc = VectorCluster(conf, cluster)

        tv.vectorize()
        vc.clustering()

        tv_time = tv.get_time()
        vc_time = vc.get_time()

        acc = []
        for ii, acc_tmp in enumerate(vc.get_accuracy()):
            acc_tmp['vector_time'] = tv_time[ii]['time']      
            acc_tmp['cluster_time'] = vc_time[ii]['time']      
            acc.append(acc_tmp)

        shutil.rmtree(conf[cluster]['model_dir'])       
  
        return acc

