import os

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from SPARQLWrapper import SPARQLWrapper
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.graphs import RdfGraph

from core.qa_chain import SparqlQAChain
from core.schemas import UserInput
from core.select_template_prompt import CUSTOM_SPARQL_GENERATION_SELECT_PROMPT

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
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
    os.remove(temp_rdf_file)


@app.get("/", response_class=HTMLResponse)
def serve_main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def ask_question(request: UserInput):
    input = {"query": request.question}
    output = chain._call(input)
    return {"answer": output['result']}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
