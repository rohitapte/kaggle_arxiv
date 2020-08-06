import json

DATA_DIR='data/'

def get_all_categories():
    """
    Identify and return unique categories.
    The categories are as a single item in a list split by spaces
    :return: set of unique categories
    """
    categories=set()
    with open(DATA_DIR+'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data=json.loads(line)
            categories.update(data['categories'][0].split(' '))
    return categories

def load_metadata():
    return_data={}
    unique_ids={}
    with open(DATA_DIR+'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data=json.loads(line)
            if data['id'] not in unique_ids:
                unique_ids[data['id']]=1
                newitem={
                    'id': data['id'],
                    'title': data['title'],
                    'categories': data['categories'][0].split(' '),
                }
                return_data[data['id']]=newitem
    return return_data

def load_citations():
    with open(DATA_DIR+'internal-citations.json') as f:
        citationdict=json.loads(f.read())
    return citationdict

def load_authors():
    with open(DATA_DIR+'authors-parsed.json') as f:
        authordict=json.loads(f.read())
    return authordict

if __name__=='__main__':
    #return_data=load_metadata()
    #rint(len(return_data))
    citationdict=load_authors()
    print(len(citationdict))