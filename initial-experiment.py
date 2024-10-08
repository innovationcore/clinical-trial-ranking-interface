from dotenv import load_dotenv
import os

from langchain_caai.caai_emb_client import caai_emb_client
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

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


def main():
    test_query = "Explain to me what cancer is."
    print(f'Question: {test_query}')
    print(f'Response: {process_query(test_query)}')
    return


if __name__ == "__main__":
    main()