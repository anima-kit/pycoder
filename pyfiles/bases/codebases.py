### pyfiles.bases.codebases
## This file creates a codebase manager which manages documents and agents to interact with the documents. 

## External imports
from re import sub
from uuid import uuid4
from itertools import chain
from langchain_core.tools.simple import Tool
from langchain_core.tools import StructuredTool
from typing import List, Dict, Any, Tuple

## Internal imports
from pyfiles.agents.agent import Agent
from pyfiles.agents.models import Models
from pyfiles.agents.tools import (
    general_retriever_tool, 
    enhanced_retriever_tool, 
    searx_search_tool
)
from pyfiles.bases.logger import logger
from pyfiles.bases.threads import Threads
from pyfiles.databases.milvus import MilvusDB
from pyfiles.databases.sqlite import SQLiteDB
from pyfiles.docs.docs_handler import Docs

## Create the codebases handler
class Codebases:
    """
    A codebase class that handles the documents and agents for user codebases.

    Attributes
    ------------
        milvus_db: MilvusDB
            The Milvus DB to store code documents.
        sqlite_db: SQLiteDB
            The SQLite DB to store code and chat documents.
        models: Models
            The models manager that houses the LLM and embedding model.
        codebase_type: str
            The type of codebase.
            Can be `user` or `external`.
        selected_codebase_name (Optional): str
            The name of the codebase to select.
            If None, no main codebase will be selected.
        external_codebases_list (Optional): List[str] 
            The name of the external codebases to select.
            If None, no external codebases will be selected.
        selected_codebase: Threads
            The threads manager for the selected codebase.
    """
    def __init__(
        self,
        milvus_db: MilvusDB, 
        sqlite_db: SQLiteDB, 
        models: Models, 
        codebase_type: str = "user", 
        selected_codebase_name: str | None = None, 
        external_codebases_list: List[str] | None = None
    ):
        """
        Initialize the codebases handler.

        Args
        ------------
            milvus_db: MilvusDB
                The Milvus DB to store code documents.
            sqlite_db: SQLiteDB
                The SQLite DB to store code and chat documents.
            models: Models
                The models manager that houses the LLM and embedding model.
            codebase_type: str
                The type of codebase.
                Can be `user` or `external`.
            selected_codebase_name (Optional): str
                The name of the codebase to select.
                If None, no main codebase will be selected.
            external_codebases_list (Optional): List[str]
                The name of the external codebases to select.
                If None, no external codebases will be selected.
            
        Raises
        ------------
            Exception: 
                If initializing the codebases handler fails, error is logged and raised.
        """
        try:
            self.milvus_db = milvus_db
            self.sqlite_db = sqlite_db
            self.models = models
            self.codebase_type = codebase_type
            self.selected_codebase_name: str | None = None
            if selected_codebase_name!=None:
                self.selected_codebase_name = self._fix_name(selected_codebase_name)
            self.external_codebases_list = external_codebases_list
            self.selected_codebase: Threads | None = None
        except Exception as e:
            logger.error(f'❌ Problem initializing codebase handler: `{str(e)}`.')
            raise

    ## Fix the codebase name
    def _fix_name(
        self, 
        name: str
    ) -> str:
        """
        Fix the codebase name.

        Args
        ------------
            name: str
                The name to fix.

        Returns
        ------------
            str: 
                The fixed name.
            
        Raises
        ------------
            Exception: 
                If fixing the name fails, error is logged and raised.
        """
        try:
            for item in [" ", "-"]:
                name = name.replace(item, "_")
            name = sub(r'[^a-zA-Z0-9_]', '_', name)
            if name=='':
                name = 'unnamed'
            if name[-1]=='_':
                name = name[:len(name)-1]
            if name[:1].isdigit():
                name = '_' + name
            return name
        except Exception as e:
            logger.error(f'❌ Problem fixing name: `{str(e)}`.')
            raise

    ## Create the documents handler
    def _create_docs_handler(
        self, 
        config: Dict[str, Any]
    ) -> Docs:
        """
        Create a documents handler for the given DB components.

        Args
        ------------
            Dict[str, Any]: 
                A dictionary of arguments to pass to the documents handler.

        Returns
        ------------
            Docs: 
                The created documents handler.
            
        Raises
        ------------
            Exception: 
                If creating the documents handler fails, error is logged and raised.
        """
        try:
            params: Dict[str, Any] = {k: v for k, v in config.items()}
            return Docs(**params)
        except Exception as e:
            logger.error(f'❌ Problem creating DB component: `{str(e)}`.')
            raise

    ## Create the default documents for a codebase
    async def _create_codebase_docs(
        self, 
        codebase_name: str
    ) -> Tuple[Threads, List[str]]:
        """
        Create all default documents for a codebase.

        Args
        ------------
            codebase_name: str 
                The codebase name

        Returns
        ------------
            Tuple[Threads, List[str]]: 
                A tuple of the resulting threads handler and the resulting SQLite thread IDs for each document.
            
        Raises
        ------------
            Exception: 
                If creating the default documents fails, error is logged and raised.
        """
        try:
            ## Create threads handler for the selected codebase
            threads: Threads = self.get_current_codebase(codebase_name)
            ## Get all threads
            threads_list: List[Tuple[str, str]] = await threads.get_list(load_type="threads")
            ## If no threads exist, need to create docs
            if len(threads_list)==0:
                codebase_config: List[Dict[str, Any]] = [
                    {
                        "db": threads.vectorstore, 
                        "content_list" : [f'# {codebase_name}'],
                        "codebase_type": self.codebase_type,
                        "group": f"{codebase_name}_code",
                        "source": "README.md"
                    },
                    {
                        "db": self.sqlite_db,
                        "content_list" : [f'# {codebase_name}'],
                        "codebase_type": self.codebase_type,
                        "group": f"{codebase_name}_code",
                        "source": "README.md"
                    },
                    {
                        "db": self.sqlite_db,
                        "content_list" : ['[]'],
                        "codebase_type": self.codebase_type,
                        "group": f"{codebase_name}_threads",
                        "source": "default_threads"
                    }
                ]
                if self.codebase_type=="user":
                    thread_ids: List[str] = await self._save_default_docs(codebase_config)
                else:
                    thread_ids = await self._save_default_docs(codebase_config[:-1])
            ## If threads do exist, pass the thread IDs
            else:
                thread_ids = []
                codes_list: List[Tuple[str, str]] = await threads.get_list(load_type="code")
                for item in chain(threads_list, codes_list):
                    thread_ids.append(item[1])
            return (
                threads, 
                thread_ids
            )
        except Exception as e:
            logger.error(f'❌ Problem creating default codebase documents: `{str(e)}`.')
            raise

    ## Save the default docs to Milvus and SQLite
    async def _save_default_docs(
        self, 
        codebase_config: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add all documents to the Milvus and SQLite DBs.

        Args
        ------------
            codebase_config: List[Dict[str, Any]]: 
                A list of configurations for the codebase documents to save.

        Returns
        ------------
            List[str]: 
                A list of the resulting SQLite thread IDs for each document.
            
        Raises
        ------------
            Exception: 
                If saving all the documents fails, error is logged and raised.
        """
        try:
            all_docs: List[Docs] = []
            for i in range(len(codebase_config)):
                ## Create the docs handler
                docs: Docs = self._create_docs_handler(codebase_config[i])
                ## Run docs through Python/Markdown/General loads and splitters to create docs
                docs.docs = await docs.acreate_docs()
                if i!=0:
                    metadatas: Dict[str, str] = {
                        k: v for k, v in codebase_config[i].items() if k not in ["docs_type", "content_list", "db"]
                    }
                    for doc in docs.docs:
                        doc.metadata = metadatas
                all_docs.extend([docs])

            ## Codebase config will have 1st element for Milvus docs
            await all_docs[0].aadd_to_vectorstore()
            #all_docs[0].add_to_vectorstore()
            ## 2nd element for SQLite docs
            thread_ids_full: List[List[str]] = []
            for i in range(1, len(codebase_config)):
                results: List[str] = await all_docs[i].aadd_to_sqlite()
                thread_ids_full.extend([results])
            thread_ids: List[str] = [x for thread_id in thread_ids_full for x in thread_id]
            return thread_ids
        except Exception as e:
            logger.error(f'❌ Problem looping through documents: `{str(e)}`.')
            raise

    ## Initialize the selected codebase
    async def initialize_default_codebase(
        self
    ) -> Threads | None:
        """
        Initialize the threads handler for the selected codebase.

        Returns
        ------------
            Threads: 
                The threads handler.
            
        Raises
        ------------
            Exception: 
                If getting the threads handler fails, error is logged and raised.
        """
        try:
            codebases: List[str] = await self.sqlite_db.get_codebase_list(codebase_type=self.codebase_type)
            ## If length of codebases is zero
            if len(codebases)==0:
                ## Need to create default docs for codebase
                if self.codebase_type=="user":
                    codebase_name: str = 'default_codebase'
                    threads, _ = await self._create_codebase_docs(codebase_name)
                    return threads
                else:
                    return None
            ## Codebases exist
            else:
                ## Select a codebase if none selected yet
                if self.selected_codebase_name==None:
                    codebases = await self.sqlite_db.get_codebase_list(codebase_type=self.codebase_type)
                    codebase_name = codebases[0]
                ## or take selected codebase if given
                else:
                    codebase_name = self.selected_codebase_name

                ## Get threads manager for the codebase
                threads = self.get_current_codebase(codebase_name)
                return threads
        except Exception as e:
            logger.error(f'❌ Problem initializing default codebase: `{str(e)}`.')
            raise

    ## Create a new codebase
    async def create_new_codebase(
        self, 
        name: str
    ) -> Tuple[str, List[str], str, List[str], str]:  
        """
        Create a new codebase.

        Args
        ------------
            name: str 
                The name of the codebase to create.

        Returns
        ------------
            Tuple[str, List[str], str, List[str], str]: 
                A Tuple of the newly selected codebases properties.
                (
                    Name of the codebase type (`user` or `external`)
                    List of the available codebases
                    Name of the new codebase
                    List of thread ids for selected codebase 
                    Status message
                )
            
        Raises
        ------------
            Exception: 
                If creating the codebase fails, error is logged and raised.
        """
        try:
            codebases: List[str] = await self.sqlite_db.get_codebase_list(codebase_type=self.codebase_type)
            ## Fix name and check if it already exists
            name = self._fix_name(name) 
            if name in codebases:
                status_message: str = f'Codebase "{name}" already exists. Choose another name.'
                self.selected_codebase, thread_ids = await self._create_codebase_docs(name)
                return (
                    self.codebase_type, 
                    codebases, 
                    name, 
                    thread_ids, 
                    status_message
                )
            ## Create the Milvus collection and default documents
            self.milvus_db.create_collection(name)
            self.selected_codebase, thread_ids = await self._create_codebase_docs(name)  
            codebases = await self.sqlite_db.get_codebase_list(codebase_type=self.codebase_type) 
            ## Select the new agent
            if self.codebase_type=="user":
                self.selected_agent = self.get_current_agent(codebase_name=name)  
            status_message = f'✅ Successfully created codebase `{name}`.'
            logger.info(status_message)
            return (
                self.codebase_type, # Name of the codebase type (`user` or `external`)
                codebases,          # List of the available codebases
                name,               # Name of the new codebase
                thread_ids,         # List of thread ids for selected codebase 
                status_message      # Status message
            )
        except Exception as e:
            logger.error(f'❌ Problem creating new codebase: `{str(e)}`.')
            raise

    async def delete_codebase(
        self, 
        name: str
    ) -> Tuple[str, str | None, List[str], List[str | None] | str | None, str]:
        """
        Delete the selected codebase.

        Args
        ------------
            name: str 
                The name of the codebase to delete.

        Returns
        ------------
            Tuple[str, List[str], str, List[str], str]: 
                A Tuple of the newly selected codebases properties.
                (
                    Name of the codebase type (`user` or `external`)
                    List of the available codebases
                    Name of the new codebase
                    List of thread ids for selected codebase 
                    Status message
                )
            
        Raises
        ------------
            Exception: 
                If deleting the codebase fails, error is logged and raised.
        """
        try:
            ## Drop the Milvus colletion
            self.milvus_db.client.drop_collection(name)
            ## Delete all the SQLite documents
            if self.selected_codebase != None:
                if self.codebase_type=="user":
                    threads: List[Tuple[str, str]] = await self.selected_codebase.get_list(load_type="threads") 
                    codes: List[Tuple[str, str]] = await self.selected_codebase.get_list(load_type="code") 
                    await self.sqlite_db.delete_documents_by_id([thread[1] for thread in threads])
                    await self.sqlite_db.delete_documents_by_id([code[1] for code in codes])
                else:
                    ext_codebase: Threads = self.get_current_codebase(name=name)
                    codes = await ext_codebase.get_list(load_type="code") 
                    await self.sqlite_db.delete_documents_by_id([code[1] for code in codes])
            status_message: str = f'✅ Successfully deleted codebase `{name}`.'
            logger.info(status_message)

            ## Get newly selected codebase properties
            codebases: List[str] = await self.sqlite_db.get_codebase_list(codebase_type=self.codebase_type)
            selected_codebase: str | None = None
            if self.codebase_type=="user":
                thread_ids: List[str | None] | str | None = [None, None]
            else:
                thread_ids = None
            if len(codebases)!=0:
                selected_codebase = codebases[0]
            if selected_codebase:
                self.selected_codebase = self.get_current_codebase(name=selected_codebase)
                results_1: List[Tuple[str, str]] = await self.selected_codebase.get_list(load_type="code")
                if self.codebase_type=="user":
                    results_0: List[Tuple[str, str]] = await self.selected_codebase.get_list(load_type="threads")
                    thread_ids = [
                        results_0[0][1],
                        results_1[0][1]
                    ]
                    self.selected_agent = self.get_current_agent(codebase_name=selected_codebase)
                else:
                    thread_ids = results_1[0][1]
            return (
                self.codebase_type, 
                selected_codebase, 
                codebases, 
                thread_ids, 
                status_message
            )
        except Exception as e:
            logger.error(f'❌ Problem deleting codebase: `{str(e)}`.')
            raise

    def get_current_codebase(
        self, 
        name: str | None
    ) -> Threads:
        """
        Get the threads handler for the selected codebase.

        Args
        ------------
            name: str 
                The name of the selected codebase.

        Returns
        ------------
            Threads: 
                The threads handler.
            
        Raises
        ------------
            Exception: 
                If getting the threads handler fails, error is logged and raised.
        """
        try:
            selected_codebase_instance: Threads | None = None
            if name != None:
                selected_codebase_instance = Threads(
                    codebase_type=self.codebase_type,
                    milvus_db=self.milvus_db, 
                    sqlite_db=self.sqlite_db,
                    models=self.models, 
                    codebase=name
                )
            else:
                raise ValueError(f'❌ Name for current codebase should not be None.')    
            if selected_codebase_instance!=None:
                logger.info(f'📝 Using codebase `{name}`')   
                return selected_codebase_instance
            else:
                raise ValueError(f'❌ Selected codebase should not be None.')
        except Exception as e:
            logger.error(f'❌ Problem getting the currently selected codebase: `{str(e)}`.')
            raise

    def get_current_agent(
        self, 
        codebase_name: str
    ) -> Agent:
        """
        Get the agent for the selected codebase.

        Args
        ------------
            codebase_name: str 
                The name of the selected codebase.

        Returns
        ------------
            Agent: 
                The agent.
            
        Raises
        ------------
            Exception: 
                If getting the agent fails, error is logged and raised.
        """
        try:
            if self.selected_codebase!=None:
                ## Get the threads handler
                current_codebase: Threads = self.get_current_codebase(codebase_name)
                ## Get the general retriever tool for the selected codebase
                codebase_retriever_tool: Tool = general_retriever_tool(
                    vectorstore=current_codebase.vectorstore,
                    name="retrieve_main_docs",
                    description="Search and return information about the user's main documents.",
                    expr=f'group == "{current_codebase.vectorstore.collection_name}_code_part" AND codebase_type == "user"',
                    num_results = self.selected_codebase.max_threads
                )
                ## Enhance the general retriever tool
                enhanced_codebase_retriever_tool: Tool = enhanced_retriever_tool(codebase_retriever_tool, codebase_name, self.models)
                ## Create a list for the docs retriever and searx metasearch tools
                tools: List[Tool | StructuredTool] = [
                    enhanced_codebase_retriever_tool,
                    searx_search_tool
                ]
            else: 
                raise ValueError(f'❌ Selected codebase for user should not be None.')
            ## If user has external codebase selected
            if self.external_codebases_list:
                for external_codebase in self.external_codebases_list:
                    ## Create a threads handler for this ext codebase
                    thread: Threads = Threads(
                        codebase_type="external",
                        milvus_db=self.milvus_db,
                        sqlite_db=self.sqlite_db,
                        models=self.models,
                        codebase=external_codebase,
                        max_threads=self.selected_codebase.max_threads
                    )
                    ## Create the retriever tool
                    retriever_tool: Tool = general_retriever_tool(
                        vectorstore=thread.vectorstore,
                        name=f"retrieve_{external_codebase}_docs",
                        description=f"Search and return information about {external_codebase}.",
                        expr=f'group == "{external_codebase}_code_part" AND codebase_type == "external"',
                        num_results = self.selected_codebase.max_threads
                    )
                    ## Enhance the retriever tool
                    enhanced_external_codebase_retriever_tool: Tool = enhanced_retriever_tool(retriever_tool, external_codebase, self.models)
                    ## Add to tools
                    tools.extend([enhanced_external_codebase_retriever_tool])
            ## Create the agent handler
            agent: Agent = Agent(models=self.models, tools=tools, codebase=current_codebase)
            self.selected_agent = agent
            return agent
        except Exception as e:
            logger.error(f'❌ Problem getting the currently selected agent: `{str(e)}`.')
            raise

    async def get_codebase_state_details(
        self, 
        name: str
    ) -> Tuple[str, Threads, str]:
        """
        Get state details for the selected codebase.

        Args
        ------------
            name: str 
                The name of the selected codebase.

        Returns
        ------------
            Tuple[str, Threads, str]: 
                A tuple of the codebase properties.
                (
                    The name of the codebase type (`user` or `external`)
                    The threads manager for the selected codebase 
                    The name of the selected codebase
                )
            
        Raises
        ------------
            Exception: 
                If getting the agent fails, error is logged and raised.
        """
        try:
            self.selected_codebase = self.get_current_codebase(name=name)
            if self.selected_codebase:
                if self.codebase_type=="user":
                    self.selected_agent = self.get_current_agent(codebase_name=name)
            return (
                self.codebase_type, 
                self.selected_codebase, 
                name
            )
        except Exception as e:
            logger.error(f'❌ Problem getting the selected codebase state details: `{str(e)}`.')
            raise