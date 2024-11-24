from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)
CORS(app)


def get_database_connection(config):
    """Establish database connection using config parameters."""
    return Neo4jGraph(
        url=config['neo4j_uri'],
        username=config['neo4j_username'],
        password=config['neo4j_password']
    )


def get_llm(config):
    """Initialize the LLM with configuration."""
    return ChatOpenAI(
        model_name='',
        openai_api_key=config['llm_api_key'],
        openai_api_base=config.get('llm_api_base'),
        temperature=0.2
    )


def generate_search_query(search_terms):
    """Generate a Cypher query based on search terms."""
    query = """
    MATCH (a:Article)
    WHERE toLower(a.abstract) CONTAINS toLower($search_term)
        OR toLower(a.title) CONTAINS toLower($search_term)
    WITH a
    MATCH (auth:Author)-[:AUTHORED]->(a)
    OPTIONAL MATCH (a)-[:HAS_KEYWORD]->(k:Keyword)
    RETURN DISTINCT 
        a.title as title,
        a.pmid as pmid,
        a.abstract as abstract,
        collect(DISTINCT auth.first_name + ' ' + auth.last_name) as authors,
        collect(DISTINCT k.name) as keywords
    LIMIT 5
    """
    return query, {"search_term": search_terms[0]}


def extract_search_terms(question):
    """Extract relevant search terms from the question."""
    tokens = word_tokenize(question.lower())
    stop_words = set(stopwords.words('english'))
    search_terms = [word for word in tokens
                    if word.isalnum()
                    and word not in stop_words
                    and len(word) > 3]
    return search_terms


def generate_result_explanation(question, results, llm):
    """Generate an LLM explanation of the search results."""
    if not results:
        return "No relevant papers were found matching your query."

    explanation_prompt = PromptTemplate(
        template="""You are a helpful research assistant explaining PubMed search results. 
        The user asked: {question}

        Based on this question, I found {num_results} papers. Here are the key details about what I found:

        {result_details}

        Please provide a concise but informative explanation of:
        1. Why these papers were selected and how they relate to the user's question
        2. The main themes or findings across the papers
        3. Any particularly noteworthy papers from the set

        Keep your response conversational but professional, and highlight the most relevant aspects for the user's query.
        """,
        input_variables=["question", "num_results", "result_details"]
    )

    # Format paper details for the LLM
    result_details = []
    for i, paper in enumerate(results, 1):
        paper_detail = f"""Paper {i}:
        Title: {paper['title']}
        Keywords: {', '.join(paper['keywords'])}
        Key points from abstract: {paper['abstract'][:200]}...
        Authors: {', '.join(paper['authors'])}
        """
        result_details.append(paper_detail)

    # Generate explanation
    explanation = llm.invoke(
        explanation_prompt.format(
            question=question,
            num_results=len(results),
            result_details="\n\n".join(result_details)
        )
    )

    return explanation.content


@app.route('/check-database', methods=['POST'])
def handle_database_request():
    try:
        # Validate request
        params = request.json
        if not params or "messages" not in params:
            return jsonify({'status': "error", 'response': "Must include messages in request"})

        # Get the user's question
        question = params["messages"][-1]['content']

        # Load configuration
        with open('config.json') as config_file:
            config = json.load(config_file)

        # Extract search terms from question
        search_terms = extract_search_terms(question)
        if not search_terms:
            return jsonify({
                'status': "error",
                'response': "Could not extract meaningful search terms from the question"
            })

        # Initialize LLM
        llm = get_llm(config)

        # Generate and execute query
        graph = get_database_connection(config)
        query, params = generate_search_query(search_terms)
        results = graph.query(query, params=params)

        if not results:
            return jsonify({
                'status': "success",
                'response': f"No papers found matching the terms: {', '.join(search_terms)}"
            })

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result['title'],
                'pmid': result['pmid'],
                'abstract': result['abstract'],
                'authors': result['authors'],
                'keywords': result['keywords']
            })

        # Generate explanation of results
        explanation = generate_result_explanation(question, formatted_results, llm)

        return jsonify({
            'status': "success",
            'response': {
                'explanation': explanation,
                'papers': formatted_results
            }
        })

    except Exception as e:
        return jsonify({
            'status': "error",
            'response': f"An error occurred: {str(e)}"
        })


if __name__ == '__main__':
    # Initialize NLTK downloads
    nltk.download('punkt')
    nltk.download('stopwords')
    app.run(debug=True)