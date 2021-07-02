import requests
import json
from GensimResearchCorpus import ResearchCorpus, GensimResearchCorpus
import gensim
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from globals import es_host, es_port, gensim_model,gensim_model_dims, filterCategory
from data_utilities import get_all_categories

es = Elasticsearch([{
    'host':es_host,
    'port': es_port
}])
model = gensim.models.doc2vec.Doc2Vec.load(gensim_model)

def deleteIndices():
    url="http://"+es_host+":"+str(es_port)+"/uniquecategories"
    payload = {}
    headers = {}
    response = requests.request("DELETE", url, headers=headers, data=payload)
    print(response.text)
    url="http://"+es_host+":"+str(es_port)+"/arxiv"
    response = requests.request("DELETE", url, headers=headers, data=payload)
    print(response.text)

def createIndices():
    url = "http://" + es_host + ":" + str(es_port) + "/uniquecategories"
    payload = json.dumps({
        "settings": {
            "number_of_shards": 1
        },
        "mappings": {
            "properties": {
                "categoryname": {
                    "type": "text"
                }
            }
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)

    url = "http://" + es_host + ":" + str(es_port) + "/arxiv"
    payload = json.dumps({
        "settings": {
            "number_of_shards": 1
        },
        "mappings": {
            "properties": {
                "id": {
                    "type": "text"
                },
                "submitter": {
                    "type": "text"
                },
                "update_date": {
                    "type": "date"
                },
                "authors": {
                    "type": "text"
                },
                "title": {
                    "type": "text"
                },
                "journalref": {
                    "type": "text"
                },
                "doi": {
                    "type": "text"
                },
                "categories": {
                    "type": "text"
                },
                "abstract": {
                    "type": "text"
                },
                "abstract_vector": {
                    "type": "dense_vector",
                    "dims": gensim_model_dims
                }
            }
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)

def populateCategories():
    categorycounts = get_all_categories()
    data = []
    for item in categorycounts:
        mydict = {
            'categoryname': item,
        }
        data.append(mydict)
    bulk(es, data, index="uniquecategories")

def populateElasticSearch():
    data = []
    for researchItem in ResearchCorpus(filterCategory=filter):
        doc2vec_vector = model.infer_vector(researchItem['tokens'])
        mydict = {
            'id': researchItem['id'],
            'submitter': researchItem['submitter'],
            'update_date': researchItem['update_date'],
            'authors': researchItem['authors'],
            'title': researchItem['title'],
            'journalref': researchItem['journal-ref'],
            'doi': researchItem['doi'],
            'categories': researchItem['categories'],
            'abstract': researchItem['abstract'],
            'abstract_vector': doc2vec_vector,
        }
        data.append(mydict)
        if len(data) >= 1000:
            bulk(es, data, index="arxiv")
            data = []
    bulk(es, data, index="arxiv")

if __name__=='__main__':
    deleteIndices()
    createIndices()
    populateCategories()
    populateElasticSearch()