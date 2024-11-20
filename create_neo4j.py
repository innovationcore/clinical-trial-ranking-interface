from neo4j import GraphDatabase
from lxml import etree
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Connect to Neo4j
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))


def create_article(tx, title, pmid, abstract):
    tx.run("MERGE (a:Article {pmid: $pmid}) SET a.title = $title, a.abstract = $abstract",
           title=title, pmid=pmid, abstract=abstract)


def create_author(tx, first_name, last_name, pmid):
    tx.run("""
    MATCH (a:Article {pmid: $pmid})
    MERGE (auth:Author {first_name: $first_name, last_name: $last_name})
    MERGE (auth)-[:AUTHORED]->(a)
    """, first_name=first_name, last_name=last_name, pmid=pmid)


def create_keyword(tx, keyword, pmid):
    tx.run("""
    MATCH (a:Article {pmid: $pmid})
    MERGE (k:Keyword {name: $keyword})
    MERGE (a)-[:HAS_KEYWORD]->(k)
    """, keyword=keyword, pmid=pmid)


def extract_keywords(abstract, n=5):
    words = word_tokenize(abstract.lower())  # tokenize, make tokens lowercase

    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalpha() and word not in stop_words]

    freq_dist = nltk.FreqDist(words)  # frequency distribution

    return [word for word, _ in freq_dist.most_common(n)]  # Return the n most common words as keywords


def process_xml_file(file_path):
    # Parse the XML file
    with open(file_path, 'rb') as f:
        tree = etree.parse(f)

    root = tree.getroot()

    # Iterate through PubMed articles contained in the Annual Baseline
    for article in root.xpath('//PubmedArticle'):
        title = article.xpath('.//ArticleTitle')[0].text
        pmid = article.xpath('.//PMID')[0].text
        abstract = ' '.join(article.xpath('.//AbstractText/text()'))

        print(f"Processing Article - Title: {title}, PMID: {pmid}")

        # Create article node from pubmed baseline
        with driver.session() as session:
            session.execute_write(create_article, title, pmid, abstract)

        # Process authors from pubmed baseline
        authors = article.xpath('.//AuthorList/Author')
        for author in authors:
            last_name = author.xpath('.//LastName')
            first_name = author.xpath('.//ForeName')

            if last_name and first_name:
                last_name = last_name[0].text
                first_name = first_name[0].text
                print(f"Processing Author: {first_name} {last_name}, Article PMID: {pmid}")

                # Create author node and assign relationship
                with driver.session() as session:
                    session.execute_write(create_author, first_name, last_name, pmid)

        # Extract and process keywords from paper abstracts
        if abstract:
            keywords = extract_keywords(abstract)
            for keyword in keywords:
                print(f"Processing Keyword: {keyword}, Article PMID: {pmid}")

                # Create keyword node and assign relationship(s)
                with driver.session() as session:
                    session.execute_write(create_keyword, keyword, pmid)


def main():
    file_path = 'pubmed24n0001.xml'  # Update this to your file path
    process_xml_file(file_path)
    print("Database population complete.")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.close()
