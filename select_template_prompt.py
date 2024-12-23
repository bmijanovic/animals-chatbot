from langchain_core.prompts.prompt import PromptTemplate

CUSTOM_SPARQL_GENERATION_SELECT_TEMPLATE = """Task: Generate a SPARQL SELECT statement for querying a graph database.
For instance, to find all email addresses of John Doe, the following query in backticks would be suitable:
```
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?email
WHERE {{
    ?person foaf:name "John Doe" .
    ?person foaf:mbox ?email .
}}
```
Instructions:
Use only the node types and properties provided in the schema.
Do not use any node types and properties that are not explicitly provided.
Include all necessary prefixes.
Object characteristics is connected with animal by the property hasCharacteristics.
All properties are in caracteristics node.
Use only the node types and properties provided in the schema.
taxonomy is connected with animal by the property hasTaxonomy.
kingdom, phylum. class, order, family, genus, taxonomy are connected with next one by the property belongsTo.
For every characristic use OPTIONAL clause.

Schema:
{schema}

Note: Be as concise as possible.
Do not include any explanations or apologies in your responses.
Do not respond to any questions that ask for anything else than for you to construct a SPARQL query.
Do not include any text except the SPARQL query generated.

The question is:
{prompt}"""

CUSTOM_SPARQL_GENERATION_SELECT_PROMPT = PromptTemplate(
    input_variables=["schema", "prompt"], template=CUSTOM_SPARQL_GENERATION_SELECT_TEMPLATE
)