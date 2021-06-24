import re
import json
from collections import defaultdict
from nltk import word_tokenize
import gensim

DATA_DIR='data/'

latex_regex = re.compile("\$(.*?)\$")
numeric_regex = re.compile(r'^-?[0-9]+$')

def parse_id_for_datestring(arxiv_id):
    """
    convert the id to yy, mm and text
    upto march 2007 format was archive.subject_class/yymmnumber For example math.GT/0309136
    since april 2007 its YYMM.number
    :param id: id to parse
    :return: yymm
    """
    location=arxiv_id.find('/')
    if location==-1:
        datestring=arxiv_id[:4]
    else:
        datestring=arxiv_id[arxiv_id.find('/')+1:][:4]
    if datestring[0]=='9':
        datestring='19'+datestring
    else:
        datestring='20'+datestring
    return datestring

def get_all_categories():
    """
    Identify and return unique categories.
    The categories are as a single item in a list split by spaces
    :return: set of unique categories
    """
    categories=defaultdict(int)
    with open(DATA_DIR+'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data=json.loads(line)
            for item in data['categories'].split(' '):
                categories[item]+=1
    return categories

def load_metadata():
    """
    loads the arxiv metadata from file. there are duplicate entries if there has been an update.
    seems like the later entries are more current
    :return:
        unique_id_count - count of duplicates
        return_data - dictionary hashed by id of metadata
    """
    return_data={}
    unique_id_count=defaultdict(int)
    with open(DATA_DIR+'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data=json.loads(line)
            unique_id_count[data['id']]+=1
            newitem={
                'id': data['id'],
                'date': parse_id_for_datestring(data['id']),
                'title': data['title'],
                'categories': data['categories'].split(' '),
            }
            return_data[data['id']]=newitem
    return unique_id_count,return_data

def load_data():
    """
    loads the arxiv metadata from file. there are duplicate entries if there has been an update.
    seems like the later entries are more current
    :return:
        unique_id_count - count of duplicates
        return_data - dictionary hashed by id of metadata
    """
    return_data=[]
    unique_id_count=defaultdict(int)
    with open(DATA_DIR+'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data=json.loads(line)
            data['title'] = data['title'].strip().replace('\n', ' ')
            data['abstract']=data['abstract'].strip().replace('\n',' ')
            data['abstract_cleaned']=clean_text(data['abstract'])
            unique_id_count[data['id']]+=1
            return_data.append(data)
    return unique_id_count,return_data

def load_citations():
    """
    load citations from file
    :return: dictionary of citations by id
    """
    with open(DATA_DIR+'internal-citations.json') as f:
        citationdict=json.loads(f.read())
    if 'acc-phys/9607002' in citationdict:
        citationdict.pop('acc-phys/9607002')
    return citationdict

def generate_reverse_citations(citations,metadata):
    reverse_citation = defaultdict(list)
    for key, values in citations.items():
        for citation in values:
            if citation != key and citation in metadata:
                reverse_citation[citation].append(key)
    return reverse_citation

def load_authors():
    """
    load authors from file
    :return: dictionary of author by id
    """
    unique_authors={}
    with open(DATA_DIR+'authors-parsed.json',encoding='utf-8') as f:
        authordict=json.loads(f.read())
    return authordict

def print_metadata_diff_for_ids(list_of_ids):
    """
    get all the entries for a specific id
    print them out
    :param id: id for research article
    :return: None
    """
    found_items=defaultdict(list)
    with open(DATA_DIR + 'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data = json.loads(line)
            data['abstract']=data['abstract']
            if data['id'] in list_of_ids:
                found_items[data['id']].append(data)
    if len(found_items)>0:
        for arxiv_id in list_of_ids:
            print("Printing values for id "+arxiv_id)
            for key in found_items[arxiv_id][0].keys():
                mismatch=False

                currentValue=found_items[arxiv_id][0][key]
                for item in found_items[arxiv_id][1:]:
                    if currentValue!=item[key]:
                        mismatch=True
                if mismatch:
                    print(key)
                    currentValue = found_items[arxiv_id][0][key]
                    print(currentValue)
                    for item in found_items[arxiv_id][1:]:
                        if currentValue != item[key]:
                            print(item[key])
                    print("..........................................")
            print("__________________________________________")
    else:
        print("No items found for id "+' '.join(item for item in list_of_ids))

def clean_text(sText):
    """
    :param sText: text to clean
    :return: cleaned text

    since these are science papers, convert everything within $...$ to EQUATION
    convert numbers to NUMBER
    """
    formatted_text = numeric_regex.sub('_NUMBER_', latex_regex.sub('_EQUATION_', sText))
    return formatted_text.lower()


if __name__=='__main__':
    unique_ids,return_data=load_metadata()
    print(len(unique_ids))
    print(len(return_data))
    #i=0
    #find_list=[]
    #for id in unique_ids:
    ##    if unique_ids[id]>1:
    #        i+=1
    #        find_list.append(id)
    #        if i>10000:break
    #print_metadata_diff_for_ids(find_list)
