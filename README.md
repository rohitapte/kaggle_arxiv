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