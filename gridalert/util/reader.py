from gensim.models.doc2vec import Doc2Vec
from fastText import load_model

from . import text  as util_text

def get_data_from_sqlite3(db, where, cl_conf):

    data = []
    tags = []

    fields = db.select(where=where, base_match=cl_conf)

    for counter, docs in enumerate(fields):
        doc = docs['data']

        if cl_conf['vector_jp_num'] == 'True':
            doc = util_text.filter_doc(doc)

        data.append(doc)
        tags.append(docs['tag'])

    return data, tags

