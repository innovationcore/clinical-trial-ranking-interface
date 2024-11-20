from lxml import etree

# Parse the XML file
with open('pubmed24n0001.xml', 'rb') as f:
    tree = etree.parse(f)

# Get the root element
root = tree.getroot()

# Example: iterate through PubMed articles
for article in root.xpath('//PubmedArticle'):
    title = article.xpath('.//ArticleTitle')[0].text
    pmid = article.xpath('.//PMID')[0].text
    print(f"Title: {title}, PMID: {pmid}")
    authors = article.xpath('.//AuthorList/Author')
    for author in authors:
        last_name = author.xpath('.//LastName')[0].text
        first_name = author.xpath('.//ForeName')[0].text
        print(f"Author: {first_name} {last_name}, Article PMID: {pmid}")
