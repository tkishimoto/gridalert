
def model_vec_path(cl_conf, service):
    model = '%s.%s.%s.vec.model' % (cl_conf['name'],
                                    service,
                                    cl_conf['vector_type'])
    return cl_conf['model_dir'] + '/' + model

def model_cls_path(cl_conf, service):
    model = '%s.%s.%s.%s.cls.model' % (cl_conf['name'],
                                    service,
                                    cl_conf['vector_type'],
                                    cl_conf['cluster_type'])
    return cl_conf['model_dir'] + '/' + model

def model_scl_path(cl_conf, service):
    model = '%s.%s.%s.%s.scl.model' % (cl_conf['name'],
                                    service,
                                    cl_conf['vector_type'],
                                    cl_conf['cluster_type'])
    return cl_conf['model_dir'] + '/' + model

def model_result_path(cl_conf, service):
    model = '%s.%s.%s.%s.result.db' % (cl_conf['name'],
                                    service,
                                    cl_conf['vector_type'],
                                    cl_conf['cluster_type'])
    return cl_conf['model_dir'] + '/' + model

def plot_path(cl_conf, service):
    plot = '%s.%s.%s.%s.svg' % (cl_conf['name'],
                                 service,
                                 cl_conf['vector_type'],
                                 cl_conf['cluster_type'])
    return cl_conf['plot_dir'] + '/' + plot

def plot_tree_path(cl_conf, service):
    plot = '%s.%s.%s.%s.tree.png' % (cl_conf['name'],
                                 service,
                                 cl_conf['vector_type'],
                                 cl_conf['cluster_type'])
    return cl_conf['plot_dir'] + '/' + plot

def plot_scan_path(cl_conf, service):
    plot = '%s.%s.%s.%s.scan.png' % (cl_conf['name'],
                                 service,
                                 cl_conf['vector_type'],
                                 cl_conf['cluster_type'])
    return cl_conf['plot_dir'] + '/' + plot

def model_paths(cl_conf, service):
    paths = {'vec' : model_vec_path(cl_conf, service),
             'cls' : model_cls_path(cl_conf, service),
             'scl' : model_scl_path(cl_conf, service),
             'result' : model_result_path(cl_conf, service)}
    return paths

def plot_paths(cl_conf, service):
    paths = {'cls' : plot_path(cl_conf, service),
            'scan' : plot_scan_path(cl_conf, service),
            'tree' : plot_tree_path(cl_conf, service)}
    return paths
