from data_utilities import load_authors,load_citations,load_metadata,get_all_categories
from tqdm import tqdm
from collections import namedtuple
import re
#from neo4j import GraphDatabase

#driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "arxiv123"))

def generate_bulk_entry_csvs():
    categories = get_all_categories()
    authors = load_authors()
    _,metadata = load_metadata()
    citations = load_citations()
    categoryDict={}
    i=0
    for category in categories:
        i+=1
        categoryDict[category]="cat" + str(i).zfill(len(str(len(categories))))
    Author = namedtuple("Author", ["lastname", "firstnames","suffix"])
    uniqueAuthors={}
    i=0
    for key,items in authors.items():
        for author in items:
            authorTuple=Author(author[0],author[1],author[2])
            if authorTuple not in uniqueAuthors:
                i+=1
                uniqueAuthors[authorTuple]="aut" + str(i).zfill(len(str(len(authors))))

    #generate the csvs in the temp directory
    with open('temp/metadata.csv','w') as f:
        f.write('researchPaperID:ID@Date@Title\n')
        for key,value in metadata.items():
            f.write(value['id']+"@"+value['date']+"@"
                    +re.sub(' +', ' ', value['title'].replace('\n',' '))+'\n')

    with open('temp/categories.csv','w') as f:
        f.write("categoryIdD:ID@CategoryName\n")
        for key,value in categoryDict.items():
            f.write(str(value)+"@"+key+'\n')

    with open('temp/authors.csv','w') as f:
        f.write("authorID:ID@LastName@FirstNames@Suffix\n")
        for key,value in uniqueAuthors.items():
            f.write(str(value)+"@"+key[0]+"@"+key[1]+"@"+key[2]+'\n')

    with open('temp/papers-categories-rule.csv','w') as f:
        f.write(':START_ID@:END_ID@:TYPE\n')
        for key, value in metadata.items():
            for category in value['categories']:
                f.write(key+'@'+categoryDict[category]+"@INCATEGORY\n")

    with open('temp/papers-authors-rule.csv','w') as f:
        f.write(':START_ID@:END_ID@:TYPE\n')
        for key, value in metadata.items():
            for author in authors[key]:
                authorKey=Author(author[0],author[1],author[2])
                f.write(key+'@'+uniqueAuthors[authorKey]+"@WRITTENBY\n")

    with open('temp/papers-citations-rule.csv','w') as f:
        f.write(':START_ID@:END_ID@:TYPE\n')
        for key in metadata:
            for citationkey in citations:
                if key==citationkey or citationkey not in metadata:
                    continue
                f.write(key+'@'+citationkey+'@CITES\n')

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
#        tx.run("MATCH(a: ResearchPaper), (b:ResearchAuthor) "
#               "WHERE a.id = $research_id AND b.lastname = $lastname and b.firstnames = $firstnames and b.suffix = $suffix "
#               "CREATE(b) - [r: WROTE]->(a)",
#               research_id=researchPaper['id'], lastname=author[0], firstnames=author[1], suffix=author[2])

def add_research_category_relationship(tx,researchPaper):
    for category in researchPaper['categories']:
        tx.run("MATCH(a: ResearchPaper), (b:ResearchCategory) "
               "WHERE a.id = $research_id AND b.name = $category_name "
               "CREATE(a) - [r: RESEARCHCATEGORY]->(b)",
               research_id=researchPaper['id'],category_name=category)
#        tx.run("MATCH(a: ResearchPaper), (b:ResearchCategory) "
#               "WHERE a.id = $research_id AND b.name = $category_name "
#               "CREATE(b) - [r: CONTAINSRESEARCH]->(a)",
#               research_id=researchPaper['id'], category_name=category)

def add_research_citation_relationship(tx,researchPaper,citationPaper):
    tx.run("MATCH(a: ResearchPaper), (b: ResearchPaper) "
           "WHERE a.id = $research_id and b.id = $citation_id "
           "CREATE (a) - [r: CITES]->(b)",
           research_id=researchPaper['id'], citation_id=citationPaper['id'])
#    tx.run("MATCH(a: ResearchPaper), (b: ResearchPaper) "
#           "WHERE a.id = $research_id and b.id = $citation_id "
#           "CREATE (b) - [r: CITEDBY]->(a)",
#           research_id=researchPaper['id'], citation_id=citationPaper['id'])

def add_all_categories():
    categories=get_all_categories()
    with driver.session() as session:
        for category in tqdm(categories):
            session.write_transaction(create_category_entry,category)


def populate_graph():
    add_all_categories()
    metadata = load_metadata()
    citations=load_citations()

    #sub_metadata = {}
    #for key, value in tqdm(metadata.items()):
    #    if 'cs.AI' in value['categories']:
    #        sub_metadata[key] = value
    #metadata=sub_metadata

    authors=load_authors()
    with driver.session() as session:
        for key,value in tqdm(metadata.items()):
            #create entry
            session.write_transaction(create_research_entry,value)
            #create relationship to categories
            session.write_transaction(add_research_category_relationship,value)
            #create author and relationship to authors
            if value['id'] in authors:
                author_data=authors[value['id']]
                for author in author_data:
                    session.write_transaction(create_author_entry,author)
                session.write_transaction(add_research_author_relationship,value,author_data)
        #now create citations
        for key,value in tqdm(metadata.items()):
            if key in citations:
                citationlist=citations[key]
                for item in citationlist:
                    if key!=item:
                        if item in metadata:
                            session.write_transaction(add_research_citation_relationship,value,metadata[item])



if __name__=='__main__':
    generate_bulk_entry_csvs()