from logging import getLogger

logger = getLogger(__name__)

from ..util import text as util_text

class BaseVector:

    def __init__(self, cl_conf):

        self.cl_conf = cl_conf


    def create_model(self):
        return 

    def add_dimensions(self, data, docs):

        results = []
        arbitrary_words = self.cl_conf['cluster_arbitrary_words'].split(',')
        for vector, doc in zip(data, docs):
            vector_tmp = vector.tolist()

            for arbitrary_word in arbitrary_words:
                if arbitrary_word == '':
                    continue

                vector_tmp.append(doc.count(arbitrary_word))

            if self.cl_conf['cluster_count_int'] == 'True':
                counter = util_text.count_int(doc)
                vector_tmp.append(counter)

            if self.cl_conf['cluster_count_word'] == 'True':
                vector_tmp.append(len(doc.split()))

            results.append(vector_tmp)

        return results

