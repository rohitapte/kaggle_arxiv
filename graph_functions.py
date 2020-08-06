from data_utilities import load_authors,load_citations,load_metadata
from tqdm import tqdm
from neo4j import GraphDatabase
import re

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "arxiv123"))

def add_citation(tx, researchPaper, citationPaper):
    tx.run("MERGE (a:ResearchPaper {id: $id, title: $title}) "
           "MERGE (a)-[:CITES]->(paper:ResearchPaper {id: $citation_id,title: $citation_title})",
           id=researchPaper['id'], title=re.sub(' +', ' ', researchPaper['title'].replace('\n',' ')),
           citation_id=citationPaper['id'], citation_title=re.sub(' +', ' ', citationPaper['title'].replace('\n',' ')))

def generate_graph():
    metadata=load_metadata()
    authors=load_authors()
    citations=load_citations()

    #generate authors->articles
    #Author = namedtuple('Author', ['lastname', 'firstinitials','suffix'])
    #uniqueAuthors=defaultdict(list)
    #for key,valueList in authors.items():
    #    for value in valueList:
    #        author=Author(lastname=value[0],firstinitials=value[1],suffix=value[2])
    #        uniqueAuthors[author].append(key)
    with driver.session() as session:
        for key,value in tqdm(metadata.items()):
            for subkey in citations:
                if key!=subkey:
                    citationdata=metadata[subkey]
                    session.write_transaction(add_citation, value, citationdata)



if __name__=='__main__':
    generate_graph()