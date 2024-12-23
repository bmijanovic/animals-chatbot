import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from SPARQLWrapper import SPARQLWrapper, RDF
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from qa_chain import SparqlQAChain
from langchain_community.graphs import RdfGraph
from select_template_prompt import CUSTOM_SPARQL_GENERATION_SELECT_PROMPT
import uvicorn

load_dotenv()
VIRTUOSO_SPARQL_URL = "http://localhost:8890/sparql"
GRAPH_IRI = "http://www.semanticweb.org/tehno-trube/ontologies/2024/11/animals_ontology.owl"
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

temp_rdf_file = "temp_data.rdf"
sparql = None
graph = None
llm = None
chain = None

app = FastAPI(
    lifespan=lambda _: lifespan_handler()
)


@asynccontextmanager
async def lifespan_handler():
    global sparql, graph, llm, chain

    # Startup code: Initialize SPARQL, RDF, LLM, and QA Chain
    # print("Initializing resources...")

    # Initialize SPARQL wrapper
    sparql = SPARQLWrapper(endpoint=VIRTUOSO_SPARQL_URL, defaultGraph=GRAPH_IRI)

    # Fetch RDF data and write to temp file
    sparql.setQuery("""
        CONSTRUCT { ?s ?p ?o }
        WHERE {
          ?s ?p ?o.
        }
    """)
    sparql.setReturnFormat("rdf+xml")
    rdf_data = sparql.query().convert()

    # Write the RDF data to a temporary file
    with open(temp_rdf_file, "wb") as file:
        rdf_data.serialize(destination=file, format="xml")

    # Initialize RDF graph
    graph = RdfGraph(
        source_file=temp_rdf_file,
        standard="owl",
        serialization="xml"
    )

    # Initialize the LLM
    llm = ChatGroq(
        model_name="llama3-70b-8192",
        temperature=0,
        max_tokens=1024,
        max_retries=2,
        streaming=True,
    )

    # Create the QA chain
    chain = SparqlQAChain.setup(llm, graph, sparql, sparql_select_prompt=CUSTOM_SPARQL_GENERATION_SELECT_PROMPT,
                                verbose=True)

    # print("Application has started and all resources have been initialized.")

    yield  # Yield control back to FastAPI to run the application

    # Shutdown code (cleanup)
    # print("Shutting down resources...")
    import os
    os.remove(temp_rdf_file)



class UserInput(BaseModel):
    question: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Animals Chatbot API"}


@app.post("/")
async def ask_question(request: UserInput):
    question = request.question
    query = {
        "query": question,
    }
    answer = chain._call(query)
    return answer


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
