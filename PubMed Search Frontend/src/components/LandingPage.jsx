import {Container} from "react-bootstrap";

function LandingPage() {
    return(
        <Container>
            <div>
                Welcome to the PubMed Search Assistant. This is a search engine utilizing a Large Language Model and Retrieval
                Augmented Generation techniques to allow you to ask questions and get relevant responses related on the entire
                corpus of PubMed papers.
            </div>
            <br/>
            <div>
                This is done by loading in the abstracts, citations, and authors of the papers into a graph database (Neo4J).
                I used a python package NLTK to tokenize words found in the abstracts in order to created linkages between papers focusing on similar concepts.
                The graph connects authors to titles, titles to abstracts, citations to those papers, and then abstracts to their keywords.
            </div>
            <div>
                Conversations with the LLM are recorded for quality assurance and improvement.
            </div>
        </Container>
    );
}
export default LandingPage;