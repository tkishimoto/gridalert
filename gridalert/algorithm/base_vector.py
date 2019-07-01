from logging import getLogger

logger = getLogger(__name__)

class BaseVector:

    def __init__(self, cl_conf):

        self.cl_conf = cl_conf


    def create_model(self):
        return 

    def add_dimensions(self, docs):

        data = []
        arbitrary_words = self.cl_conf['cluster_arbitrary_words'].split(',')

        for doc in docs:
            data_tmp = doc

            for arbitrary_word in arbitrary_words:
                if arbitrary_word == '':
                    continue

                data_tmp.append(doc.count(arbitrary_word))

            if self.cl_conf['cluster_count_int'] == 'True':
                counter = util_text.count_int(doc)
                data_tmp.append(counter)

            if self.cl_conf['cluster_count_word'] == 'True':
                data_tmp.append(len(tmp_doc))

            data.append(data_tmp)

        return data

