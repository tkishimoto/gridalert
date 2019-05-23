from gensim.models.doc2vec import Doc2Vec
from fastText import load_model

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


def get_data_from_fasttext(text_path, model_path):
    # return data and tag in fasttext model

    model = load_model(model_path)

    data = [] 
    tags = []
    for line in open(text_path):
        tags.append(line.split(',')[0])
        tmp_data = ','.join(line.split(',')[1:])
        tmp_data = tmp_data.replace('\n', '')

        predict = model.get_sentence_vector(tmp_data)
        print (predict)
