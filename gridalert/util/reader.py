from gensim.models.doc2vec import Doc2Vec
from fastText import load_model
from sklearn import preprocessing

def get_data_from_sqlite3(db, where, cl_conf):

    data = []
    tags = []

    fields = db.select(where=where, base_match=cl_conf)

    for counter, docs in enumerate(fields):
        data.append(docs['data'])
        tags.append(docs['tag'])

    return data, tags


def get_data_from_doc2vec(model_path, docs, cl_conf):
    # return data and tag from doc2vec model

    model = Doc2Vec.load(model_path) 
    arbitrary_words = cl_conf['cluster_arbitrary_words'].split(',')

    data = [] 
    for doc in docs:
        tmp_doc = doc.replace('\n', '').split()

        vector = model.infer_vector(tmp_doc).tolist()

        for arbitrary_word in arbitrary_words:
            if arbitrary_word == '':
                continue             

            vector.append(doc.count(arbitrary_word))

        data.append(vector)

    if cl_conf['cluster_normalize']:
        mm = preprocessing.MinMaxScaler()
        data = mm.fit_transform(data).tolist()

    return data

    #model = Doc2Vec.load(model_path)

    #data = []
    #tags = []
    #for ii in range(len(model.docvecs)):
    #    tmp_data = []

    #    for jj in range(len(model.docvecs[ii])):        
    #        tmp_data.append(model.docvecs[ii][jj])  

    #    data.append(tmp_data)
    #    tags.append(model.docvecs.index_to_doctag(ii).tolist())

    #return data,tags


def get_data_from_fasttext(model_path, docs, cl_conf):
    # return data and tag from fasttext model

    model = load_model(model_path)
    arbitrary_words = cl_conf['cluster_arbitrary_words'].split(',')

    data = [] 
    for doc in docs:
        tmp_doc = doc.replace('\n', '')

        vector = model.get_sentence_vector(tmp_doc).tolist()

        for arbitrary_word in arbitrary_words:
            if arbitrary_word == '':
                continue             

            vector.append(doc.count(arbitrary_word))

        data.append(vector)

    if cl_conf['cluster_normalize']:
        mm = preprocessing.MinMaxScaler()
        data = mm.fit_transform(data).tolist()
    
    return data


