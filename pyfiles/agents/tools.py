### pyfiles.agents.tools
## This file creates the tools to pass to the agent.
## The tools created are as follows:
##  - A SearXNG metasearch engine tool
##  - A document retriever tool to obtain information from a Milvus vectorstore

## External imports
from os import getenv
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools.simple import Tool
from langchain_core.messages import SystemMessage
from langchain_core.retrievers import BaseRetriever
from langchain_classic.tools.retriever import create_retriever_tool
from langchain_core.tools import StructuredTool
from langchain_community.utilities import SearxSearchWrapper
from langchain_milvus import Milvus
from typing import List, Tuple, Dict

## Internal exports
from pyfiles.agents.models import Models
from pyfiles.bases.logger import logger

## Get model parameters from environment
load_dotenv()
searxng_url: str = getenv("SEARXNG_URL", "http://localhost:8080")

### Vectorstore retrieval tools
## Structured output for query enhancement
class EnhancedQuery(BaseModel):
    """
    The base model to use for creating a query for vectorstore retrieval.
    """
    query: str = Field(
        description = "Enhanced query."
    )
    source: str = Field(
        description = "Name of the file to be queried."
    )

## Prompt for the LLM to enhance the user's query
def _get_enhance_query_prompt(
    query: str
) -> str:
    """
    This creates a prompt to enhance the user's query to be used for vectorstore retrieval.

    Args
    ------------
        query: str
            The query to enhance.

    Returns
    ------------
        str:
            The prompt to pass to the LLM to enhance the query.
    """
    prompt = """
    You are an AI assistant that specializes in enhancing queries to better obtain relevant documents from a vectorstore.
    Your job is to take a user query and output base elements and an enhanced query. 
    The elements you can extract are document file names (for code documents).
    If elements are extracted from the user query, do not also include their name in the query. 
    For example, if the user asks `How can I optimize file1.py?`, an example output would be: 
    {
        "query": "Overview of architecture and points of time and memory consumption",
        "source": "file_1.py"
    }
    If the user asks `What methods use async in the file_2.py?`, an example output would be:
    {
        "query": "Async methods",
        "source": "file_2.py"
    }
    """ + f"""Here is the user query: {query}"""
    return prompt

## Structure the LLM's output for query enhancement
def _get_structured_llm(
    query: str, 
    models
):
    """
    This creates an LLM model with structured output to be used for enhancing the user's query.

    Args
    ------------
        query: str
            The query to enhance.
        models: Models
            The models manager class that houses the LLM.

    Returns
    ------------
        Tuple[BaseChatModel, str]:
            A tuple of LLM with structured output and the system prompt to pass to the LLM.
        
    """
    system_content: str = _get_enhance_query_prompt(query)
    llm = models.llm.with_structured_output(EnhancedQuery)
    return llm, system_content

## Get content from invoking LLM with structured output
def _return_structured_content(
    codebase_name, 
    result
):
    """
    This returns the formatted structured output from the LLM.

    Args
    ------------
        codebase_name: str
            The user's selected codebase.
        result: EnhancedQuery
            The structured output from the LLM.

    Returns
    ------------
        Tuple[str, Dict[str, str]]:
            A tuple of the formatted elements to return from the structured output.
        
    """
    code_elements = {
        "source": result.source,
    }
    return f"[{codebase_name}] {result.query}", code_elements

## Enhance the user's query synchronously
def _enhance_query(
    query: str, 
    codebase_name: str, 
    models
) -> Tuple[str, Dict[str, str]]:
    """
    This invokes the LLM to return the structured output for an enhanced query synchronously.

    Args
    ------------
        query: str
            The query to enhance.
        codebase_name: str
            The user's selected codebase.
        models: Models
            The models manager class that houses the LLM.

    Returns
    ------------
        Tuple[str, Dict[str, str]]:
            A tuple of the formatted elements to return for the enhanced query.
        
    """
    try:
        llm, system_content = _get_structured_llm(query=query, models=models)
        result = llm.invoke([SystemMessage(content=system_content)])
        return _return_structured_content(codebase_name=codebase_name, result=result)
    except Exception as e:
        logger.error(f'❌ Problem enhancing user query: `{str(e)}`')
        raise

## Enhance the user's query asynchronously
async def _aenhance_query(
    query: str, 
    codebase_name: str, 
    models
) -> Tuple[str, Dict[str, str]]:
    """
    This invokes the LLM to return the structured output for an enhanced query asynchronously.

    Args
    ------------
        query: str
            The query to enhance.
        codebase_name: str
            The user's selected codebase.
        models: Models
            The models manager class that houses the LLM.

    Returns
    ------------
        Tuple[str, Dict[str, str]]:
            A tuple of the formatted elements to return for the enhanced query.
        
    """
    try:
        llm, system_content = _get_structured_llm(query=query, models=models)
        result = await llm.ainvoke([SystemMessage(content=system_content)])
        return _return_structured_content(codebase_name=codebase_name, result=result)
    except Exception as e:
        logger.error(f'❌ Problem enhancing user query: `{str(e)}`')
        raise

## Update the vectorstore retriever tool
def _update_retriever_args(
    codebase_name: str, 
    code_elements: Dict[str, str]
):
    """
    This updates the vectorstore retriever tool based on the enhanced query elements.

    Args
    ------------
        codebase_name: str
            The user's selected codebase.
        code_elements: Dict[str, str]
            The code elements resulting from the enhanced query.

    Returns
    ------------
        str:
            The expression to pass to the vectorstore retrieval tool for searching.
        
    """
    ## Get search expression for given codebase and code elements
    filters = []
    for field, value in code_elements.items():
        if value:
            filters.append(f'{field} == "{value}"')
    group_filter = f'group == "{codebase_name}_code_part"'
    if filters:
        dynamic_expr = f"{group_filter} AND ({' AND '.join(filters)})"
    else:
        dynamic_expr = group_filter
    return dynamic_expr

## The base retriever tool
def general_retriever_tool(
    vectorstore: Milvus, 
    name: str, 
    description: str, 
    expr: str, 
    num_results: int
) -> Tool:
    """
    This updates the vectorstore retriever tool based on the enhanced query elements.

    Args
    ------------
        vectorstore: Milvus
            The Milvus vectorstore from which to retrieve information.
        name: str
            The name of the retriever tool.
        description: str
            The description of the retriever tool.
        expr: str
            The search expression to pass to the retriever.
        num_results: int 
            The number of results to obtain.

    Returns
    ------------
        Tool:
            The base retriever tool.

    Raises
    ------------
        Exception: 
            If creating the base retriever tools fails, error is logged and raised.
    """
    try:
        ## Base retriever searches using dense and sparse vectors
        retriever: BaseRetriever = vectorstore.as_retriever(
            search_kwargs={
                "k": num_results, 
                "params": {
                    "anns_field": "dense",
                    "topk": num_results,
                },
                "sparse_params": {
                    "anns_field": "sparse",
                    "topk": num_results, 
                },
                "ranker_type": "weighted",                  
                "ranker_params": {"weights": [0.8, 0.2]}, 
                "expr": expr
            }
        )
        return create_retriever_tool(
            retriever,
            name,
            description,
        )
    except Exception as e:
        logger.error(f'❌ Problem creating base retriever tool: `{str(e)}`')
        raise

## Enhance the base retriever tool
def enhanced_retriever_tool(
    original_tool, 
    codebase_name: str,
    models
) -> Tool:
    """
    This enhances the base retriever tool to add relevant information for searching.

    Args
    ------------
        original_tool: Tool
            The base retriever tool.
        codebase_name: str
            The user's selected codebase.
        models: Models
            The models manager that houses the LLM.

    Returns
    ------------
        Tool:
            The enhanced retriever tool.

    Raises
    ------------
        Exception: 
            If creating the enhanced retriever tools fails, error is logged and raised.
    """
    try:
        ## Enhance the original tool synchronously
        def enhanced_func(query: str) -> str:
            try:
                enhanced_query, code_elements = _enhance_query(query, codebase_name, models)
                dynamic_expr = _update_retriever_args(codebase_name=codebase_name, code_elements=code_elements)
                original_tool.dict()['func'].keywords['retriever'].search_kwargs["expr"] = dynamic_expr
                results = original_tool.func(enhanced_query)
                return results
            except Exception as e:
                logger.error(f'Failed to enhance retriever tool {str(e)}')
    
        ## TODO: Async milvus search not working with pymilvus 2.6.2
        ## Enhance the original tool asynchronously
        async def aenhanced_func(query: str) -> str:
            try:
                enhanced_query, code_elements = await _aenhance_query(query, codebase_name, models)
                dynamic_expr = _update_retriever_args(codebase_name=codebase_name, code_elements=code_elements)
                original_tool.dict()['func'].keywords['retriever'].search_kwargs["expr"] = dynamic_expr
                results = await original_tool.coroutine(enhanced_query)
                return results
            except Exception as e:
                logger.error(f'Failed to enhance retriever tool (async) {str(e)}')

        return Tool(
            name=original_tool.name,
            func=enhanced_func,
            coroutine=aenhanced_func,
            description=original_tool.description,
            args_schema=original_tool.args_schema
        )
    except Exception as e:
        logger.error(f'❌ Problem creating enhanced retriever tool: `{str(e)}`')
        raise


### Metasearch engine tools
class SearchInput(BaseModel):
    """
    The base model to use for creating a query for metasearch.
    """
    query: str = Field(description="search query")
    num_results: int = Field(description="number of search results")

def _get_searx_wrapper(
) -> SearxSearchWrapper:
    """
    This creates the SearxSearchWrapper from which the metasearch tool will be created.

    Returns
    ------------
        SearxSearchWrapper:
            The SearxSearchWrapper.

    Raises
    ------------
        Exception: 
            If creating the SearxSearchWrapper fails, error is logged and raised.
    """
    return SearxSearchWrapper(searx_host=searxng_url)

def _searx_search(
    query: str, 
    num_results: int
) -> List[dict]:
    """
    Search the web using Searx synchronously.

    Args
    ------------
        query: str
            The query to search.
        num_results: int
            The maximum number of results to obtain.

    Returns
    ------------
        List[dict]:
            A list of results.

    Raises
    ------------
        Exception: 
            If searching the web fails, error is logged and raised.
    """
    try:
        searx_search: SearxSearchWrapper = _get_searx_wrapper()
        results: List[dict] = searx_search.results(
            query=query, 
            num_results=num_results
        )
        return results
    except Exception as e:
        logger.error(f'❌ Problem searching the web: `{str(e)}`')
        raise

async def _searx_asearch(
    query: str, 
    num_results: int
) -> List[dict]:
    """
    Search the web using Searx asynchronously.

    Args
    ------------
        query: str
            The query to search.
        num_results: int
            The maximum number of results to obtain.

    Returns
    ------------
        List[dict]:
            A list of results.

    Raises
    ------------
        Exception: 
            If searching the web fails, error is logged and raised.
    """
    try:
        searx_search: SearxSearchWrapper = _get_searx_wrapper()
        results: List[dict] = await searx_search.aresults(
            query=query, 
            num_results=num_results
        )
        return results
    except Exception as e:
        logger.error(f'❌ Problem searching the web: `{str(e)}`')
        raise

## Create the metasearch tool
searx_search_tool: StructuredTool = StructuredTool.from_function(
    func = _searx_search,
    coroutine = _searx_asearch,
    name="searx_search",
    description="Search the web using Searx",
    args_schema=SearchInput
)