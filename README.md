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