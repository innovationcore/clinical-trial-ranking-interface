from neo4j import GraphDatabase
import argparse
import json
from tabulate import tabulate
from typing import List, Dict, Any
import textwrap


class PubMedVerifier:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_article_by_pmid(self, pmid: str) -> Dict[str, Any]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Article {pmid: $pmid})
                OPTIONAL MATCH (auth:Author)-[:AUTHORED]->(a)
                OPTIONAL MATCH (a)-[:HAS_KEYWORD]->(k:Keyword)
                RETURN 
                    a.title as title,
                    a.pmid as pmid,
                    a.abstract as abstract,
                    collect(DISTINCT auth.first_name + ' ' + auth.last_name) as authors,
                    collect(DISTINCT k.name) as keywords
                """, pmid=pmid)
            record = result.single()
            if record:
                return {
                    'title': record['title'],
                    'pmid': record['pmid'],
                    'abstract': record['abstract'],
                    'authors': record['authors'],
                    'keywords': record['keywords']
                }
            return None

    def get_multiple_articles(self, pmids: List[str]) -> List[Dict[str, Any]]:
        results = []
        for pmid in pmids:
            article = self.get_article_by_pmid(pmid)
            if article:
                results.append(article)
        return results

    def print_article_details(self, article: Dict[str, Any], detailed: bool = False):
        if not article:
            print("No article found with this PMID")
            return

        # Basic info table
        basic_info = [
            ["PMID", article['pmid']],
            ["Title", textwrap.fill(article['title'], width=60)],
            ["Authors", ", ".join(article['authors'])],
            ["Keywords", ", ".join(article['keywords'])]
        ]

        print("\n" + tabulate(basic_info, tablefmt="grid"))

        # Print abstract if detailed view is requested
        if detailed and article['abstract']:
            print("\nABSTRACT:")
            print("-" * 80)
            print(textwrap.fill(article['abstract'], width=80))
            print("-" * 80)

    def compare_articles(self, pmids: List[str]):
        articles = self.get_multiple_articles(pmids)

        # Create comparison table
        headers = ["", *[f"PMID: {article['pmid']}" for article in articles]]
        rows = []

        # Compare titles
        row = ["Title"]
        row.extend([textwrap.fill(article['title'], width=30) for article in articles])
        rows.append(row)

        # Compare author counts
        row = ["# Authors"]
        row.extend([len(article['authors']) for article in articles])
        rows.append(row)

        # Compare keyword counts
        row = ["# Keywords"]
        row.extend([len(article['keywords']) for article in articles])
        rows.append(row)

        print("\nArticle Comparison:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))


def main():
    parser = argparse.ArgumentParser(description='Verify PubMed records in Neo4j database')
    parser.add_argument('pmids', nargs='+', help='One or more PMIDs to look up')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--detailed', action='store_true', help='Show detailed output including abstracts')
    parser.add_argument('--compare', action='store_true', help='Compare multiple PMIDs')

    args = parser.parse_args()

    # Load configuration
    try:
        with open(args.config) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Config file {args.config} not found. Using default localhost configuration.")
        config = {
            'neo4j_uri': "bolt://localhost:7687",
            'neo4j_username': "neo4j",
            'neo4j_password': "password"
        }

    verifier = PubMedVerifier(
        config['neo4j_uri'],
        config['neo4j_username'],
        config['neo4j_password']
    )

    try:
        if args.compare and len(args.pmids) > 1:
            verifier.compare_articles(args.pmids)
        else:
            for pmid in args.pmids:
                article = verifier.get_article_by_pmid(pmid)
                print(f"\nArticle Details for PMID: {pmid}")
                verifier.print_article_details(article, detailed=args.detailed)
    finally:
        verifier.close()


if __name__ == "__main__":
    main()