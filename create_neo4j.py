from neo4j import GraphDatabase
from lxml import etree


def create_citation(tx, citing_pmid, cited_pmid):
    """
    Creates a CITES relationship between two articles and updates the citation count
    """
    tx.run("""
    MATCH (citing:Article {pmid: $citing_pmid})
    MATCH (cited:Article {pmid: $cited_pmid})
    MERGE (citing)-[:CITES]->(cited)
    WITH cited
    SET cited.citation_count = COALESCE(cited.citation_count, 0) + 1
    """, citing_pmid=citing_pmid, cited_pmid=cited_pmid)


def update_citation_counts(tx):
    """
    Updates the citation_count property for all articles based on incoming CITES relationships
    """
    tx.run("""
    MATCH (a:Article)
    SET a.citation_count = size((a)<-[:CITES]-())
    """)


def process_citations_from_xml(file_path, driver):
    # Parse the XML file
    with open(file_path, 'rb') as f:
        tree = etree.parse(f)

    root = tree.getroot()

    # Iterate through PubMed articles
    for article in root.xpath('//PubmedArticle'):
        citing_pmid = article.xpath('.//PMID')[0].text

        # Find references in the article
        # Look for citations in different possible XML locations
        reference_lists = article.xpath('.//ReferenceList/Reference') + \
                          article.xpath('.//CitationList/Citation')

        print(f"Processing citations for PMID: {citing_pmid}")

        for reference in reference_lists:
            # Extract cited PMID if available
            cited_pmid_elements = reference.xpath('.//ArticleId[@IdType="pubmed"]/text()')
            if cited_pmid_elements:
                cited_pmid = cited_pmid_elements[0]
                print(f"Found citation: {citing_pmid} -> {cited_pmid}")

                # Create citation relationship
                with driver.session() as session:
                    try:
                        session.execute_write(create_citation, citing_pmid, cited_pmid)
                    except Exception as e:
                        print(f"Error processing citation {citing_pmid} -> {cited_pmid}: {e}")


def main():
    # Use the same Neo4j connection settings as your original code
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

    try:
        file_path = 'pubmed24n0001.xml'  # Update this to your file path
        process_citations_from_xml(file_path, driver)

        # Update all citation counts at the end
        with driver.session() as session:
            session.execute_write(update_citation_counts)

        print("Citation update complete.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()