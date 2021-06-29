import json
import gensim
from nltk import word_tokenize
from data_utilities import clean_text, DATA_DIR


class GensimResearchCorpus(object):
    def __init__(self, tokens_only=False, filterCategory=None):
        self.tokens_only = tokens_only
        self.filterCategory = filterCategory

    def __iter__(self):
        """
        loads the arxiv metadata from file. there are duplicate entries if there has been an update.
        seems like the later entries are more current
        :return:
            unique_id_count - count of duplicates
            return_data - dictionary hashed by id of metadata
        """
        with open(DATA_DIR + 'arxiv-metadata-oai-snapshot.json') as f:
            for i, line in enumerate(f):
                data = json.loads(line)
                if self.filterCategory is not None:
                    if self.filterCategory not in data['categories']:
                        continue
                data['abstract'] = data['abstract'].strip().replace('\n', ' ')
                data['abstract_cleaned'] = clean_text(data['abstract'])
                tokens = word_tokenize(data['abstract_cleaned'])
                if self.tokens_only:
                    yield tokens
                else:
                    yield gensim.models.doc2vec.TaggedDocument(tokens, [i])

class ResearchCorpus(object):
    def __init__(self, tokens_only=False, filterCategory=None):
        self.filterCategory = filterCategory

    def __iter__(self):
        """
        loads the arxiv metadata from file. there are duplicate entries if there has been an update.
        seems like the later entries are more current
        :return:
            unique_id_count - count of duplicates
            return_data - dictionary hashed by id of metadata
        """
        with open(DATA_DIR + 'arxiv-metadata-oai-snapshot.json') as f:
            for i, line in enumerate(f):
                data = json.loads(line)
                if self.filterCategory is not None:
                    if self.filterCategory not in data['categories']:
                        continue
                data['title'] = data['title'].strip().replace('\n', ' ')
                data['abstract'] = data['abstract'].strip().replace('\n', ' ')
                data['abstract_cleaned'] = clean_text(data['abstract'])
                data['tokens'] = word_tokenize(data['abstract_cleaned'])
                yield data

if __name__=='__main__':
    vector_size=300
    min_count=5
    filterCategory = None
    model = gensim.models.doc2vec.Doc2Vec(workers=8,
                                          vector_size=50,
                                          min_count=5,
                                          epochs=40)
    mycorpus = GensimResearchCorpus(filterCategory=filterCategory)
    model.build_vocab(mycorpus)
    model.train(mycorpus, total_examples=model.corpus_count, epochs=model.epochs)
    sFilterCategory = 'None'
    if filterCategory is not None:
        sFilterCategory=filterCategory
    model.save('doc2vec.model_'+str(vector_size)+'_'+str(min_count)+'_'+sFilterCategory)