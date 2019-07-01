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




def get_data_from_fasttext(model_path, docs, cl_conf):
    # return data and tag from fasttext model

    model = load_model(model_path)
    arbitrary_words = cl_conf['cluster_arbitrary_words'].split(',')

    data = [] 
    for doc in docs:
        if cl_conf['vector_jp_num'] == 'True':
            doc = util_text.filter_doc(doc)

        tmp_doc = doc.replace('\n', '')

        vector = model.get_sentence_vector(tmp_doc).tolist()

        for arbitrary_word in arbitrary_words:
            if arbitrary_word == '':
                continue             

            vector.append(doc.count(arbitrary_word))

        if cl_conf['cluster_count_int'] == 'True':
            counter = util_text.count_int(doc)  
            vector.append(counter)

        if cl_conf['cluster_count_word'] == 'True':
            vector.append(len(tmp_doc))

        data.append(vector)

    return data


def get_data_from_scdvword2vec(model_path, docs, scdv, cl_conf):
    # return data and tag from fasttext model
    data = scdv.get_vector(docs, model_path, train=False)
    data = data.tolist()
    return data

