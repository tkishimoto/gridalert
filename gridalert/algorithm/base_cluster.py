from logging import getLogger

logger = getLogger(__name__)

class BaseCluster:

    def __init__(self, cl_conf):

        self.cl_conf = cl_conf


    def create_model(self):
        return 

