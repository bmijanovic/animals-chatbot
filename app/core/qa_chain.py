from __future__ import annotations
from typing import Any, Dict, List
from SPARQLWrapper import SPARQLWrapper, JSON
from langchain.chains.base import Chain
from langchain_community.chains.graph_qa.prompts import (
    SPARQL_GENERATION_SELECT_PROMPT,
    SPARQL_QA_PROMPT,
)
from langchain_community.graphs import RdfGraph
from langchain.prompts.base import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence


class SparqlQAChain(Chain):
    sparql_generation_select_chain: RunnableSequence
    qa_chain: RunnableSequence
    graph: RdfGraph
    sparql: SPARQLWrapper
    input_key: str = "query"
    output_key: str = "result"

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    @classmethod
    def setup(cls,
        llm: BaseLanguageModel,
        graph: RdfGraph,
        sparql: SPARQLWrapper,
        sparql_select_prompt: BasePromptTemplate = SPARQL_GENERATION_SELECT_PROMPT,
        sparql_qa_prompt: BasePromptTemplate = SPARQL_QA_PROMPT,
        **kwargs
        ) -> SparqlQAChain:
        sparql_generation_select_chain = sparql_select_prompt | llm | StrOutputParser()
        qa_chain = sparql_qa_prompt | llm | StrOutputParser()
        return cls(
            sparql_generation_select_chain=sparql_generation_select_chain,
            qa_chain=qa_chain,
            graph=graph,
            sparql=sparql,
            **kwargs
        )

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = inputs[self.input_key]
        # print("Prompt:", prompt)
        generated_sparql_query = self.sparql_generation_select_chain.invoke(
            {"prompt": prompt, "schema": self.graph.get_schema})
        generated_sparql_query = generated_sparql_query.replace("`", "").replace("sparql", "")
        # print("SPARQL Query:", generated_sparql_query)

        self.sparql.setQuery(generated_sparql_query)
        self.sparql.setReturnFormat(JSON)
        sparql_results = self.sparql.query().convert()
        # print("SPARQL Results:", sparql_results)

        answer = self.qa_chain.invoke({"prompt": prompt, "context": sparql_results})
        # print("Answer:", answer)

        return {self.output_key: answer}
