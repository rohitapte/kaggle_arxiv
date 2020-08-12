# kaggle_arxiv

### metadata has the following keys

id: identifier (text). Upto March 2007 was archive.subject_class/yearmonthnumber. For example math.GT/0309136.

Since April 2007 YYMM.number

submitter - text

authors - text but use separate file

title - text

comments - text

journal-ref - text

doi - text

abstract - text

report-no - text

categories - list

versions - list


### bulk import

neo4j-admin.bat import --nodes=ResearchPapers=d:\kaggle_arxiv\temp\metadata.csv --nodes=ResearchCategories=d:\kaggle_arxiv\temp\categories.csv --nodes=Authors=d:\kaggle_arxiv\temp\authors.csv --relationships=d:\kaggle_arxiv\temp\papers-authors-rule.csv --relationships=d:\kaggle_arxiv\temp\papers-categories-rule.csv --delimiter="@"


load csv with headers from "file:///paper-author.csv" as csvline
MATCH(a: ResearchPaper {id: csvline.research_id}), (b:ResearchAuthor {id: csvline.author_id}) 
CREATE(a) - [r: WRITTENBY]->(b)

load csv with headers from "file:///paper-categories.csv" as csvline
MATCH(a: ResearchPaper {id: csvline.research_id}), (b:ResearchCategory {name: csvline.category_name}) 
CREATE(a) - [r: INCATEGORY]->(b)

load csv with headers from "file:///paper-citations.csv" as csvline
MATCH(a: ResearchPaper {id: csvline.research_id}), (b:ResearchPaper {id: csvline.citation_id}) 
CREATE(a) - [r: CITES]->(b)


// Find the nodes you want to delete
MATCH (n) 
// Take the first 10k nodes and their rels (if more than 100 rels / node on average lower this number)
WITH n LIMIT 300000
DETACH DELETE n
RETURN count(*)

summary by category

MATCH (p:ResearchPaper)-[:INCATEGORY]->(c:ResearchCategory)
RETURN c.name,count(p)

citations for paper by id

MATCH (citepaper:ResearchPaper)<-[:CITES]-(p:ResearchPaper {id:'cond-mat/0406317'})
return p,count(citepaper)

paper, count of citations

MATCH (citepaper:ResearchPaper)<-[:CITES]-(p:ResearchPaper )
return p,count(citepaper)