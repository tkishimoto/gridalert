from . import text  as util_text

def get_data_from_sqlite3(db, where, cl_conf):

    data = []
    tags = []

    fields = db.select(where=where, base_match=cl_conf)

    for counter, docs in enumerate(fields):
        doc = docs['data']

        if cl_conf['vector_numsimword'] == 'True':
            doc = util_text.filter_doc(doc,
                                       int(cl_conf['vector_numsimword_digit']),
                                       int(cl_conf['vector_numsimword_bit']))

        if cl_conf['vector_split_dot'] == 'True':
            doc = ' '.join(doc.split('.'))

        data.append(doc)
        tags.append(docs['tag'])

    return data, tags

