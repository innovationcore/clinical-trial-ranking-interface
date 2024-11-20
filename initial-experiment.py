from dotenv import load_dotenv
import os

from langchain_caai.caai_emb_client import caai_emb_client
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

api_key = os.getenv('LLMF-API-KEY')
api_base = os.getenv('LLMF-API-BASE')
api_base_local = os.getenv('LLMF-API-BASE-LOCAL')

llm = ChatOpenAI(
    model_name="",
    openai_api_key=api_key,
    openai_api_base=api_base,
    verbose=True
)

embeddings = caai_emb_client(
    model="",
    api_key=api_key,
    api_url=api_base,
    max_batch_size=100,
    num_workers=10
)

def process_query(query):
    template = """Question: {question}
    Answer: Let's think step by step."""
    prompt = PromptTemplate.from_template(template)
    llm_chain = prompt | llm
    response = llm_chain.invoke(query)
    return response


# Query for Vector DB
def process_vector_query(query):
    raw_documents = TextLoader('arxiv-metadata-oai-snapshot.json').load()
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=10)
    documents = text_splitter.split_documents(raw_documents)
    db = FAISS.from_documents(documents, embeddings)

    # Similarity search
    docs = db.similarity_search(query)
    ss = docs[0].page_content

    # Similarity search by vector
    embedding_vector = embeddings.embed_query(query)
    docs = db.similarity_search_by_vector(embedding_vector)
    ssv = docs[0].page_content

    return ss, ssv


def standard_query_test():
    test_query = "Explain to me what cancer is."
    print(f'Question: {test_query}')
    print(f'Response: {process_query(test_query)}')
    return


def vector_db_query_test():
    try:
        query = "Can you find anything related to cancer?"
        ss, ssv = process_vector_query(query)
        print('text:', query)
        print('Similarity search:[', ss, ']')
        print('Similarity search by vector:[', ssv, ']')
    except Exception as e:
        print(e)
    return


def query_pubmed_eutils(query):
    pubmed_api = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'  # Eutils api base

    return


if __name__ == "__main__":
    vector_db_query_test()