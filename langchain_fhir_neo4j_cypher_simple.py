#https://github.com/samschifman/RAG_on_FHIR/blob/main/RAG_on_FHIR_with_KG/FHIR_GRAPHS.ipynb

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
import json
from neo4j import GraphDatabase

with open('../config.json') as user_file:
    config = json.load(user_file)

llm = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=config["openai_api_key"],
    temperature=0
)

driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth = ('neo4j', 'password')) #Localhost

def get_database_localhost():
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = "password"

    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

    return graph

def get_relationship_types(tx, node_label):
    query = f"""
    MATCH (n:{node_label})-[r]-()
    RETURN DISTINCT type(r) AS relationship
    """
    result = tx.run(query)
    return [record['relationship'] for record in result]

def get_schema_for_node_types(node_labels):
    all_info = ""
    with driver.session() as session:
        for label in node_labels:
            query = f"""MATCH (n:{label})
                WITH n
                LIMIT 1 RETURN n"""
            result = session.run(query)
            results = [record.data() for record in result]
            if 'embedding' in results[0]['n'].keys():
                del results[0]['n']['embedding']
            if 'embedding_openai' in results[0]['n'].keys():
                del results[0]['n']['embedding_openai']
            info = label+": "+str(results[0]).replace('{', '(').replace('}', ')')

            relationships = str(session.read_transaction(get_relationship_types, label))

            all_info = all_info + info + ' Relationship types: '+relationships+ '\n'
    return all_info

def determine_relevant_nodes(question):
    template = """
    Task: The user input will concern a question related to a graph database, which contains many node types. Your job is to determine what node types are relevant
    to this particular user question. Your response should be a comma separated list of node types, if there are more than one, with no additional text.
    
    Here are the node types and when they are relevant:
    AllergyIntolerance: questions related to allergies or their severity/causes
    CarePlan: relevant for care plans, self management plans, or exercise therapies
    CareTeam: relevant for people, practitioners, organizations, and health centers associated with care plans
    Claim: related to billing, insurance, and pricing for procedures and encounters
    Condition: relevant for conditions and diagnoses
    Date: any question involving a date or time period should involve this node type
    Device: relevant for medical devices
    DiagnosticReport: relevant for diagnostic reports
    DocumentReference: relevant for clinical notes
    Encounter: related to specific patient visits and what a patient was there for
    ExplanationOfBenefit: relevant for Medicaid and insurance payors
    ImagingStudy: related to imaging, such as X-rays and radiology
    Immunization: relevant for vaccines and innoculations
    Location: relevant for addresses and locations of businesses or hospitals, but not relevant for patients
    Medication: relevant for medications and dosages
    MedicationAdministration: relevant for a specific instance of usage of medication
    MedicationRequest: relevant for practitioner requests for medications for certain conditions
    Observation: relevant for a particular measurement of a patient at a given time, such as vital signs or BMI
    Organization: relevant for addresses, phone numbers, and other information for organizations, such as healthcare providers
    Patient: relevant for questions relating to specific patients, including demographic info such as locations, DOBs, and other statuses
    Practitioner: related to specific practictioners and their location, name, and contact info
    PractionerRole: related to roles of practitioners at their given hospitals
    Procedure: relevant for specific procedures and when they were performed
    SupplyDelivery: relevant for the shipping of specific items and equipment
    
    Question: {question}"""

    prompt = PromptTemplate.from_template(template)

    llm_chain = prompt | llm

    response = llm_chain.invoke({'question': question})
    return response.content


if __name__ == '__main__':

    graph = get_database_localhost()

    #question = "What conditions does patient Arlette667 Kohler843 have?"
    #question = "How many patients have the condition 'Impacted molars'?"
    #question = "What are the taglines for the 3 matrix movies?"

    #question = "What is Arlette667 Kohler843's marital status?"

    #question = "How much did the colonoscopy on Aug. 13, 2021 cost?"

    #question = "What was the body weight of Adan632 Cassin499 on 10/09/2014."

    #question = "What is heart rate of Adan632 Cassin499 on their most recent measurement?"

    question = "How many patients are under the age of 30 by the end of 2021?"

    relevant_nodes = determine_relevant_nodes(question)
    relevant_nodes_list = relevant_nodes.replace(" ","").split(",")
    relevant_schema = get_schema_for_node_types(relevant_nodes_list)
    print(relevant_schema)

    cypher_prompt = """
    You are an assistant that generates valid Cypher queries based on the provided schema and examples.
    Use only the provided relationship types and properties in the schema.
    Do not use any other relationship types or properties that are not provided.
    Do not write any queries to create, edit, or delete nodes. You have read-only access to this database.
    Important: Return only the Cypher query, with no additional text or notes.
    Examples: Here are a few examples of generated Cypher statements for particular questions:
    # "How old was the patient with full name Aurelio227 Balistreri607 on the date 08/13/2021?"
       WITH date('2021-08-13') AS target_date
                     MATCH (p:Patient {{name: 'Aurelio227 Balistreri607'}})
                     WITH p, target_date, date(p.birth_date) AS birth_date
                     RETURN duration.between(birth_date, target_date).years AS age_at_target_date

    # "What city is Bradford382 from?"
       MATCH (p:Patient {{name_0_given_0: 'Bradford382'}})
                     RETURN p.address_0_city AS city
    Below are example nodes for the relevant node types, to aid in writing the query:
    """+relevant_schema+"""

    Generate a Cypher query to answer the following question: {question}
    """

    prompt_cypher = PromptTemplate(template=cypher_prompt, input_variables=['schema', 'question'])

    chain = GraphCypherQAChain.from_llm(llm, graph=graph, verbose=True, cypher_prompt=prompt_cypher)


    input = {"query":question}
    print(chain.invoke(input))





