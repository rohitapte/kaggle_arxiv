import json
import gensim
from nltk import word_tokenize
from data_utilities import clean_text, DATA_DIR


class GensimResearchCorpus(object):
    def __init__(self, tokens_only=False):
        self.tokens_only = tokens_only

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
                data['abstract'] = data['abstract'].strip().replace('\n', ' ')
                data['abstract_cleaned'] = clean_text(data['abstract'])
                tokens = word_tokenize(data['abstract_cleaned'])
                if self.tokens_only:
                    yield tokens
                else:
                    yield gensim.models.doc2vec.TaggedDocument(tokens, [i])
