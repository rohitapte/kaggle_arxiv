from data_utilities import load_authors,load_citations,load_metadata,get_all_categories
from tqdm import tqdm
from collections import namedtuple
import re
from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "arxiv123"))

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
                    +re.sub(' +', ' ', value['title'].replace('@','_at_').replace('"','').replace('\n',' '))+'\n')

    with open('temp/categories.csv','w') as f:
        f.write("categoryIdD:ID@CategoryName\n")
        for key,value in categoryDict.items():
            f.write(str(value)+"@"+key+'\n')

    with open('temp/authors.csv','w') as f:
        f.write("authorID:ID@LastName@FirstNames@Suffix\n")
        for key,value in uniqueAuthors.items():
            f.write(str(value)+"@"+key[0].replace('@','_at_').replace('"','')+"@"+key[1].replace('@','_at_').replace('"','')+"@"+key[2].replace('@','_at_').replace('"','')+'\n')

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
            if key in citations:
                for citationkey in citations[key]:
                    if key==citationkey or citationkey not in metadata:
                        continue
                    f.write(key+'@'+citationkey+'@CITES\n')


def populate_graph():
    print("Loading data")
    categories = get_all_categories()
    citations = load_citations()
    authors = load_authors()
    _, metadata = load_metadata()
    #get the unique authors list
    Author = namedtuple("Author", ["lastname", "firstnames", "suffix"])
    uniqueAuthors = {}
    i=0
    for key, items in authors.items():
        for author in items:
            authorTuple = Author(author[0], author[1], author[2])
            if authorTuple not in uniqueAuthors:
                i+=1
                uniqueAuthors[authorTuple] = "aut" + str(i).zfill(len(str(len(authors))))
    print("Loading data...done")
    print("Categories: "+str(len(categories)))
    print("Citations: "+str(len(citations)))
    print("Research Papers: "+str(len(metadata)))
    print("Unique Authors:"+str(len(uniqueAuthors)))
    with driver.session() as session:
        #add categories
        with session.begin_transaction() as tx:
            for category in tqdm(categories):
                tx.run("CREATE (a:ResearchCategory {name: $categoryName})",
                       categoryName=category)
            tx.commit()

        #add metadata
        i = 0
        tx=session.begin_transaction()
        for key,value in tqdm(metadata.items()):
            i += 1
            tx.run("CREATE (a:ResearchPaper {id: $researchId, title: $title}) ",
                   researchId=value['id'], title=value['title'])
            if i%100000==0:
                tx.commit()
                tx = session.begin_transaction()
        tx.commit()
        tx.close()

        # add unique authors
        i = 0
        tx=session.begin_transaction()
        for key,value in tqdm(uniqueAuthors.items()):
            i+=1
            tx.run("CREATE (a:ResearchAuthor {id: $catid, lastname: $lastname, firstnames: $firstnames, suffix: $suffix})",
                   catid="aut" + str(i).zfill(len(str(len(uniqueAuthors)))),lastname=key[0], firstnames=key[1], suffix=key[2])
            if i % 100000 == 0:
                tx.commit()
                tx = session.begin_transaction()
        tx.commit()
        tx.close()

        #tx = session.begin_transaction()
        #tx.run("CREATE INDEX FOR (n:ResearchCategory) ON (n.name)")
        #tx.run("CREATE INDEX FOR (n:ResearchPaper) ON (n.id)")
        #tx.run("CREATE INDEX FOR (n:ResearchAuthor) ON (n.id)")
        #tx.commit()
        #tx.close()


        with open('paper-author.csv','w') as f:
            f.write('research_id,author_id\n')
            for key, authorList in tqdm(authors.items()):
                for author in authorList:
                    authorTuple = Author(author[0], author[1], author[2])
                    f.write(key+','+uniqueAuthors[authorTuple]+'\n')

        with open('paper-categories.csv', 'w') as f:
            f.write('research_id,category_name\n')
            for key, value in tqdm(metadata.items()):
                for category in value['categories']:
                    f.write(key + ',' + category + '\n')

        with open('paper-citations.csv', 'w') as f:
            f.write('research_id,citation_id\n')
            for key, value in tqdm(metadata.items()):
                if key in citations:
                    for citation in citations[key]:
                        if citation != key and citation in metadata:
                            f.write(key + ',' + citation + '\n')
        """
        #author-research relationships
        i=0
        tx=session.begin_transaction()
        for key,authorList in tqdm(authors.items()):
            for author in authorList:
                i+=1
                tx.run("MATCH(a: ResearchPaper), (b:ResearchAuthor) "
                       "WHERE a.id = $research_id AND b.lastname = $lastname and b.firstnames = $firstnames and b.suffix = $suffix "
                       "CREATE(a) - [r: WRITTENBY]->(b)",
                       research_id=key, lastname=author[0], firstnames=author[1], suffix=author[2])
                if i % 100000 == 0:
                    tx.commit()
                    tx = session.begin_transaction()
        tx.commit()
        tx.close()

        #reseatch-category relationships
        i=0
        tx = session.begin_transaction()
        for key,value in tqdm(metadata.items()):
            for category in value['categories']:
                i+=1
                tx.run("MATCH(a: ResearchPaper), (b:ResearchCategory) "
                       "WHERE a.id = $research_id AND b.name = $category_name "
                       "CREATE(a) - [r: RESEARCHCATEGORY]->(b)",
                       research_id=key, category_name=category)
                if i % 100000 == 0:
                    tx.commit()
                    tx = session.begin_transaction()
        tx.commit()
        tx.close()

        #research-citations relationships
        i=0
        tx = session.begin_transaction()
        for key, value in tqdm(metadata.items()):
            if key in citations:
                for citationkey in citations[key]:
                    if citationkey!=key and citationkey in metadata:
                        i += 1
                        tx.run("MATCH(a: ResearchPaper), (b: ResearchPaper) "
                               "WHERE a.id = $research_id and b.id = $citation_id "
                               "CREATE (a) - [r: CITES]->(b)",
                               research_id=key, citation_id=citationkey)
                    if i % 100000 == 0:
                        tx.commit()
                        tx = session.begin_transaction()
        tx.commit()
        tx.close()
        """
if __name__=='__main__':
    #generate_bulk_entry_csvs()
    populate_graph()