from data_utilities import load_authors,load_citations,load_metadata,get_all_categories
from tqdm import tqdm
from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "arxiv123"))

def create_research_entry(tx,researchPaper):
    tx.run("MERGE (a:ResearchPaper {id: $id, title: $title}) ",
           id=researchPaper['id'], title=researchPaper['title'])

def create_category_entry(tx,category):
    tx.run("MERGE (a:ResearchCategory {name: $name})",
           name=category)

def create_author_entry(tx,authorAsList):
    tx.run("MERGE (a:ResearchAuthor {lastname: $lastname, firstnames: $firstnames, suffix: $suffix})",
           lastname=authorAsList[0],firstnames=authorAsList[1],suffix=authorAsList[2])

def add_research_author_relationship(tx,researchPaper,authorList):
    for author in authorList:
        tx.run("MATCH(a: ResearchPaper), (b:ResearchAuthor) "
               "WHERE a.id = $research_id AND b.lastname = $lastname and b.firstnames = $firstnames and b.suffix = $suffix "
               "CREATE(a) - [r: WRITTENBY]->(b)",
               research_id=researchPaper['id'], lastname=author[0], firstnames=author[1], suffix=author[2])
        tx.run("MATCH(a: ResearchPaper), (b:ResearchAuthor) "
               "WHERE a.id = $research_id AND b.lastname = $lastname and b.firstnames = $firstnames and b.suffix = $suffix "
               "CREATE(b) - [r: WROTE]->(a)",
               research_id=researchPaper['id'], lastname=author[0], firstnames=author[1], suffix=author[2])

def add_research_category_relationship(tx,researchPaper):
    for category in researchPaper['categories']:
        tx.run("MATCH(a: ResearchPaper), (b:ResearchCategory) "
               "WHERE a.id = $research_id AND b.name = $category_name "
               "CREATE(a) - [r: RESEARCHCATEGORY]->(b)",
               research_id=researchPaper['id'],category_name=category)
        tx.run("MATCH(a: ResearchPaper), (b:ResearchCategory) "
               "WHERE a.id = $research_id AND b.name = $category_name "
               "CREATE(b) - [r: CONTAINSRESEARCH]->(a)",
               research_id=researchPaper['id'], category_name=category)


def add_all_categories():
    categories=get_all_categories()
    with driver.session() as session:
        for category in tqdm(categories):
            session.write_transaction(create_category_entry,category)


def add_apartial_metadata():
    add_all_categories()
    authors=load_authors()
    metadata=[]
    with open('arxiv-lite.json') as f:
        for line in f:
            data=json.loads(line)
            metadata.append(data)
    with driver.session() as session:
        for value in metadata:
            session.write_transaction(create_research_entry,value)
            session.write_transaction(add_research_category_relationship,value)
            if value['id'] in authors:
                author_data=authors[value['id']]
                for author in author_data:
                    session.write_transaction(create_author_entry,author)
                session.write_transaction(add_research_author_relationship,value,author_data)


if __name__=='__main__':
    #add_all_categories()
    add_apartial_metadata()