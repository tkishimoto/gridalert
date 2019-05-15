from gensim.models.doc2vec import Doc2Vec

def get_data_from_doc2vec(model_path):
    # return data and tag in doc2vec model

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

