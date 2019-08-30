from logging import getLogger

logger = getLogger(__name__)

import os
import sys
import pickle
import tqdm
import pprint
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from io import StringIO
from itertools import product
from multiprocessing import Pool

from .text_vectorizer import *
from .vector_cluster import *

from .const import Const as const
from .util import hash as util_hash
from .util import path as util_path

class ScanHelper:

    def __init__(self, conf, cluster):

        self.conf       = conf
        self.cl_conf    = conf[cluster]
        self.cluster    = cluster

    def scan(self):
        conf = self.conf
        params = []

        for param in const.MLVECPARAMS:
            params.append(self.cl_conf[param].split(','))

        counter = 0
        args = []

        for param in product(*params):
            counter += 1

        for param in product(*params):
            for ii, value in enumerate(param):
                self.conf.set(self.cluster,
                              const.MLVECPARAMS[ii],
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
            plot_acc0 = []
            plot_acc1 = []
            plot_x    = []
            counters  = 1

            print('inf> ranking of %s' % key)
            for acc in acc_sort:
                plot_acc0.append(acc['acc0'])
                plot_acc1.append(acc['acc1'])
                plot_x.append(counters) 

                message = 'inf> acc (normal)=%s, acc (anomaly)=%s, ' % ('{:.3f}'.format(acc['acc1']),
                                                                        '{:.3f}'.format(acc['acc0']))
                message += 'time=%ss (%ss, %ss)' % ('{:.1f}'.format(acc['vector_time'] + acc['cluster_time']),
                                                 '{:.1f}'.format(acc['vector_time']),
                                                 '{:.1f}'.format(acc['cluster_time']))
                counters += 1
                print(message)
                pprint.pprint(acc)

            plt.plot(plot_x, plot_acc0, label='Accuracy of anomaly events', marker='o')
            plt.plot(plot_x, plot_acc1, label='Accuracy of normal events', marker='o')
            plt.xlabel('Ranking of hyper parameters')
            plt.ylabel('Accuracies')
            plt.grid(True)
            plt.legend(loc = 'upper right')


            plot_path = util_path.plot_scan_path(self.cl_conf, key)
            plt.savefig(plot_path) 

    def scan_wrapper(self, args):
        return self.scan_process(*args)


    def scan_process(self, param, conf, cluster):
        for ii, value in enumerate(param):
            key = const.MLVECPARAMS[ii]
            logger.info('%s : %s' % (key, conf[cluster][key]))

        os.makedirs(conf[cluster]['model_dir'], exist_ok=True)

        myconf = {}
        for section in conf.sections():
            myconf[section] = conf[section]
        myconf['DEFAULT'] = conf['DEFAULT']
        myconf['cl'] = conf[cluster]


        tv = TextVectorizer(myconf)
        tv.vectorize()
        tv_time = tv.get_time()

        clsparams = []

        for clsparam in const.MLCLSPARAMS:
            clsparams.append(self.cl_conf[clsparam].split(','))

        args = []
        acc = []

        for clsparam in product(*clsparams):
            for ii, value in enumerate(clsparam):
                conf.set(cluster,
                         const.MLCLSPARAMS[ii],
                         value)
            myconf['cl'] = conf[cluster]

            vc = VectorCluster(myconf)
            vc.clustering()
            vc_time = vc.get_time()

            for ii, acc_tmp in enumerate(vc.get_accuracy()):
                acc_tmp['vector_time'] = tv_time[ii]['time']      
                acc_tmp['cluster_time'] = vc_time[ii]['time']      
                acc.append(acc_tmp)

        shutil.rmtree(conf[cluster]['model_dir'])       
  
        return acc

