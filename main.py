import requests
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from qa_chain import SparqlQAChain
from langchain.graphs.rdf_graph import RdfGraph
from select_template_prompt import CUSTOM_SPARQL_GENERATION_SELECT_PROMPT

load_dotenv()

VIRTUOSO_URL = "http://localhost:8890/sparql"
GRAPH_IRI = "http://www.semanticweb.org/tehno-trube/ontologies/2024/11/animals_ontology.owl"
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
sparql = SPARQLWrapper(VIRTUOSO_URL)
app = FastAPI()

graph = RdfGraph(
    source_file="./ontology/mega_populated_ontology.rdf",
    standard="owl",
    serialization="xml"
)
graph.load_schema()

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    streaming=True,
)

chain = SparqlQAChain.setup(llm, graph, sparql, sparql_select_prompt=CUSTOM_SPARQL_GENERATION_SELECT_PROMPT, verbose=True)

class UserInput(BaseModel):
    question: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Animals Chatbot API"}


@app.post("/")
async def ask_question(request: UserInput):
    question = request.question
    # query is to get all triplets
    query = {
        "query": question,
    }
    answer = chain._call(query) 
    return answer


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


