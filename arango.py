from pyArango.connection import *
import re
from tqdm import tqdm
from data_utilities import load_authors,load_citations,load_metadata,get_all_categories
conn = Connection(username="root", password="q")
db = conn["arXiv"]

def populate_graph():
    categories=get_all_categories()
    _,metadata = load_metadata()
    citations=load_citations()
    authors=load_authors()

    #add metadata
    researchDataCollection = db.createCollection(name="researchData")
    for key,value in tqdm(metadata.items()):
        doc = researchDataCollection.createDocument()
        doc["researchId"] = value['id']
        doc['date']=value['date']
        doc['title']=re.sub(' +', ' ', value['title'].replace('\n',' '))
        doc.save()
if __name__=='__main__':
    populate_graph()