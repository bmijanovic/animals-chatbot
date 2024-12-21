from __future__ import annotations
from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains.graph_qa.prompts import (
    SPARQL_GENERATION_SELECT_PROMPT,
    SPARQL_QA_PROMPT,
)

from langchain.chains.llm import LLMChain
from langchain.graphs.rdf_graph import RdfGraph
from langchain.prompts.base import BasePromptTemplate
from langchain.pydantic_v1 import Field
from langchain.schema.language_model import BaseLanguageModel

from SPARQLWrapper import SPARQLWrapper, JSON


class SparqlQAChain(Chain):
    sparql_generation_select_chain: LLMChain
    qa_chain: LLMChain
    graph: RdfGraph
    sparql: SPARQLWrapper
    input_key: str = "query"
    output_key: str = "result"

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        _output_keys = [self.output_key]
        return _output_keys

    @classmethod
    def setup(cls, 
        llm: BaseLanguageModel,
        graph: RdfGraph,
        sparql: SPARQLWrapper,
        sparql_select_prompt: BasePromptTemplate = SPARQL_GENERATION_SELECT_PROMPT,
        sparql_qa_prompt: BasePromptTemplate = SPARQL_QA_PROMPT,
        **kwargs
        ) -> SparqlQAChain:
        sparql_generation_select_chain = LLMChain(llm=llm, prompt=sparql_select_prompt)
        qa_chain = LLMChain(llm=llm, prompt=sparql_qa_prompt)
        return cls(
            sparql_generation_select_chain=sparql_generation_select_chain,
            qa_chain=qa_chain,
            graph=graph,
            sparql=sparql,
            **kwargs
        )

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = inputs[self.input_key]
        print("Prompt:", prompt)
        _sparql_query = self.sparql_generation_select_chain.run(
            {"prompt": prompt, "schema": self.graph.get_schema})
        sparql_query = _sparql_query.replace("`", "")
        print("SPARQL Query:", sparql_query)

        self.sparql.setQuery(sparql_query)
        self.sparql.setReturnFormat(JSON)
        sparql_results = self.sparql.query().convert() 
        # print("SPARQL Results:", sparql_results)

        answer = self.qa_chain.run({"prompt": prompt, "context": sparql_results})
        print("Answer:", answer)

        return {self.output_key: answer}