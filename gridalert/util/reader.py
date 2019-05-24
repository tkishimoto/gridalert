from gensim.models.doc2vec import Doc2Vec
from fastText import load_model

def get_data_from_sqlite3(db, where, cl_conf):

    data = []
    tags = []

    fields = db.select(where=where, base_match=cl_conf)

    for counter, docs in enumerate(fields):
        data.append(docs['data'])
        tags.append(docs['tag'])

    return data, tags


def get_data_from_doc2vec(model_path):
    # return data and tag from doc2vec model

    model = Doc2Vec.load(model_path)

    data = []
    tags = []
    for ii in range(len(model.docvecs)):
        tmp_data = []

        for jj in range(len(model.docvecs[ii])):        
            tmp_data.append(model.docvecs[ii][jj])  

        data.append(tmp_data)
        tags.append(model.docvecs.index_to_doctag(ii))

    return data,tags


def get_data_from_fasttext(model_path, docs):
    # return data and tag from fasttext model

    model = load_model(model_path)

    data = [] 
    for doc in docs:
        tmp_doc = doc.replace('\n', '')

        data.append(model.get_sentence_vector(tmp_doc))

    return data
