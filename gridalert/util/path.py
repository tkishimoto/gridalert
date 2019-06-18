
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

def plot_scan_path(cl_conf, service):
    plot = '%s.%s.%s.%s.scan.png' % (cl_conf['name'],
                                 service,
                                 cl_conf['vector_type'],
                                 cl_conf['cluster_type'])
    return cl_conf['plot_dir'] + '/' + plot
