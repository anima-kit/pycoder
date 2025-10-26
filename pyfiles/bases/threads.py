### pyfiles.bases.threads
## This file creates a threads handler to manage chat and code threads for a given codebase.

## External imports
from uuid import uuid4
from json import loads
from os.path import basename
from langchain_classic.docstore.document import Document
from typing import Dict, Tuple, List

## Internal imports
from pyfiles.agents.models import Models
from pyfiles.bases.logger import logger
from pyfiles.databases.milvus import MilvusDB, Milvus
from pyfiles.databases.sqlite import SQLiteDB
from pyfiles.docs.docs_handler import Docs

## Create the threads manager
class Threads:
    """
    A users class that handles the management of threads for a given codebase.

    Attributes
    ------------
        models: Models
                The models manager that houses the LLM and embedding model.
        client: MilvusClientStart
            The Milvus client to use for Milvus management.
        user_dir: str
            The directory to store SQLite DBs.
            Defaults to `user_databases`.
        selected_user (Optional): Codebases
            The codebase handler for the selected user.
            Default to None.
        selected_ext_codebases (Optional): Codebases
            The codebase handler for the selected user's external codebases.
    """
    def __init__(
        self, 
        codebase_type: str, 
        milvus_db: MilvusDB, 
        sqlite_db: SQLiteDB, 
        models: Models, 
        codebase: str, 
        max_threads: int = 1000
    ):
        """
        Initialize the threads handler.

        Args
        ------------
            codebase_type: str
                The type of codebase.
                Can be `user` or `external`.
            milvus_db: MilvusDB
                The Milvus DB handler.
            sqlite_db: SQLiteDB
                The SQLite DB handler.
            models: Models
                The models manager that houses the LLM and embedding model.
            codebase: str
                The name of the codebase. 
            max_threads: str
                The maximum number of threads allowed.
            
        Raises
        ------------
            Exception: 
                If initializing the threads handler fails, error is logged and raised.
        """
        try:
            self.codebase_type = codebase_type
            self.milvus_db = milvus_db
            self.sqlite_db = sqlite_db
            self.models = models
            self.codebase = codebase
            self.max_threads = max_threads
            ## Get Milvus vectorstore for given codebase
            self.vectorstore: Milvus = self._get_vectorstore()
            logger.info(f'✅ Successfully initialized threads handler for codebase `{self.codebase}` and codebase type `{self.codebase_type}`')
        except Exception as e:
            logger.error(f'❌ Problem initializing threads handler: `{str(e)}`.')
            raise
    
    ## Get the Milvus vectorstore for the codebase
    def _get_vectorstore(
        self
    ) -> Milvus:
        """
        Get the Milvus vectorstore.

        Returns
        ------------
            Milvus:
                The Milvus vectorstore.
            
        Raises
        ------------
            Exception: 
                If getting the Milvus vectorstore fails, error is logged and raised.
        """
        try:
            threads_vectorstore: Milvus = self.milvus_db.get_vectorstore(
                models = self.models,
                collection_name = self.codebase
            )
            return threads_vectorstore
        except Exception as e:
            logger.error(f'❌ Problem getting Milvus vectorstore: `{str(e)}`.')
            raise

    ## Load at threads from SQLite
    async def load_all_from_sqlite(
        self, 
        load_type: str
    ) -> Dict[str, Dict[str, str]]:
        """
        Load all threads from the SQLite DB.

        Args
        ------------
            load_type: str
                The type of threads to load.
                Can be `threads` or `code`.

        Returns
        ------------
            Dict[str, Dict[str, str]]:
                A dictionary containing all the threads data.
            
        Raises
        ------------
            Exception: 
                If getting the threads fails, error is logged and raised.
        """
        try:
            group: str = f"{self.codebase}_{load_type}"
            results: List[Tuple[str, Document]] = await self.sqlite_db.get_documents_by_group(group)
            threads_data: Dict[str, Dict[str, str]] = {}
            for doc_id, doc in results:
                metadata: Dict[str, str] = doc.metadata
                threads_data[doc_id] = {
                    'content': doc.page_content,
                    'source': metadata.get('source', ''),
                    'group': metadata.get('group', '')
                }
            return threads_data
        except Exception as e:
            logger.error(f'❌ Problem getting threads data: `{str(e)}`.')
            raise

    async def get_list(
        self, 
        load_type: str
    ) -> List[Tuple[str, str]]:
        """
        Get a list of all available threads.

        Args
        ------------
            load_type: str
                The type of threads to load.
                Can be `threads` or `code`.

        Returns
        ------------
            List[Tuple[str, str]]:
                A list of tuples containing all the thread IDs and name.
            
        Raises
        ------------
            Exception: 
                If getting the threads list, error is logged and raised.
        """
        try:
            thread_state: Dict[str, Dict[str, str]] = await self.load_all_from_sqlite(load_type)
            return [(data['source'], thread_id) for thread_id, data in thread_state.items()]
        except Exception as e:
            logger.error(f'❌ Problem getting threads list: `{str(e)}`.')
            raise 

    async def delete(
        self, 
        load_type,
        thread_id
    ) -> Tuple[List[Tuple[str, str]], str | None, str]:
        """
        Delete the thread with the given thread ID then select a new thread.

        Args
        ------------
            load_type: str
                The type of threads to delete.
                Can be `threads` or `code`.
            thread_id: str
                The ID of the thread.

        Returns
        ------------
            Tuple[List[Tuple[str, str]], str | None, str]:
                A tuple containing the properties for the newly selected thread.
            
        Raises
        ------------
            Exception: 
                If deleting the thread fails, error is logged and raised.
        """
        try:
            ## Get all available threads of the given type
            thread_state: Dict[str, Dict[str, str]] = await self.load_all_from_sqlite(load_type)
            ## Delete the selected thread
            if thread_id in thread_state:
                thread_name: str = thread_state[thread_id]['source']
                del thread_state[thread_id]
            if load_type=='threads':
                await self.sqlite_db.delete_documents_by_id([thread_id])
            elif load_type=="code":
                self.vectorstore.delete(expr=f"source == '{thread_name}'")
                await self.sqlite_db.delete_documents_by_id([thread_id])
            ## Get the new available threads list
            choices: List[Tuple[str, str]] = await self.get_list(load_type)
            ## and select a new thread
            next_selected: str | None = choices[0][1] if choices else None
            status_message: str = f'Deleted thread `{thread_name}`'
            logger.info(status_message)
            return (
                choices,        # Available threads
                next_selected,  # Newly selected thread
                status_message  # Status message
            )
        except Exception as e:
            logger.error(f'❌ Problem deleting thread: `{str(e)}`.')
            raise

    async def create(
        self, 
        load_type: str, 
        files: List[str] | None = None, 
        name: str | None = None
    ) -> Tuple[List[Tuple[str, str]], str, List[str] | None, str]:
        """
        Create a new thread.

        Args
        ------------
            load_type: str
                The type of threads to delete.
                Can be `threads` or `code`.
            files (Optional): List[str] 
                Can upload files to create `code` threads.
            name (Optional): str
                The name of the thread to create.

        Returns
        ------------
            Tuple[List[Tuple[str, str]], str, List[str] | None, str]:
                A tuple containing the properties for the newly selected thread.
            
        Raises
        ------------
            Exception: 
                If creating the thread fails, error is logged and raised.
        """
        try:
            ## For chats
            if load_type=="threads":
                ## Create the documents
                if name==None:
                    name='unnamed'
                thread_id: str = str(uuid4())
                group: str = f"{self.codebase}_threads"
                metadata: Dict[str, str] = {"group": group, "source": name}
                docs: Docs = Docs(
                    codebase_type=self.codebase_type,
                    group=group, 
                    source=name, 
                    db=self.sqlite_db, 
                    content_list=['[]']
                )
                docs.docs = await docs.acreate_docs()
                ## Add them to SQLite
                await self.sqlite_db.insert_documents(docs.docs, [thread_id])
                ## Return properties for newly selected thread
                choices: List[Tuple[str, str]] = await self.get_list(load_type="threads")
                status_message: str = f'Created thread `{name}`'
                logger.info(status_message)
                return (
                    choices, 
                    thread_id, 
                    None,
                    status_message
                )
            ## For codes
            else:
                ## Check if file already in threads
                existing_files: List[Tuple[str, str]] = await self.get_list(load_type="code")
                existing_files_list: List[str] = [x[0] for x in existing_files]
                if files!=None:
                    for file in files:
                        file_name: str = basename(file)
                        # Delete if found
                        if file_name in existing_files_list:
                            #self.vectorstore.delete(expr=f"source == '{file_name}' AND group == '{self.codebase}_code'")
                            self.vectorstore.delete(expr=f"source == '{file_name}'")
                            await self.sqlite_db.delete_documents_by_source([file_name], group=f'{self.codebase}_code')
                ## Create SQLite documents
                docs_sqlite: Docs = Docs(
                    codebase_type=self.codebase_type,
                    group=f"{self.codebase}_code",
                    db=self.sqlite_db,
                    files=files
                )
                docs_sqlite.docs = await docs_sqlite.acreate_docs()
                ## Create Milvus documents
                docs_milvus: Docs = Docs(
                    codebase_type=self.codebase_type,
                    group=f"{self.codebase}_code", 
                    db=self.vectorstore,
                    files=files
                )
                docs_milvus.docs = await docs_milvus.acreate_docs()
                ## Add to Milvus and SQLite
                await docs_milvus.aadd_to_vectorstore()
                #docs_milvus.add_to_vectorstore()
                await docs_sqlite.aadd_to_sqlite()
                ## Get properties for newly selected thread
                choices = await self.get_list(load_type="code")
                thread_id = choices[0][1]
                status_message = f'Created code `{name}`'
                logger.info(status_message)
                return (
                    choices, 
                    thread_id, 
                    files, 
                    status_message
                )
        except Exception as e:
            logger.error(f'❌ Problem creating thread: `{str(e)}`.')
            raise

    async def get_state_details(
        self, 
        load_type: str,
        thread_id: str
    ) -> str:
        """
        Get the thread state details.

        Args
        ------------
            load_type: str
                The type of threads to delete.
                Can be `threads` or `code`.
            thread_id: str
                The ID of the thread.

        Returns
        ------------
            str:
                The content of the thread document
            
        Raises
        ------------
            Exception: 
                If get the thread state details fails, error is logged and raised.
        """
        try:
            thread_state: Dict[str, Dict[str, str]] = await self.load_all_from_sqlite(load_type=load_type)
            thread: Dict[str, str] = thread_state.get(thread_id, {})
            if thread:
                if load_type=="code":
                    return thread['content']
                else:
                    return loads(thread['content'])
            else:
                return ''
        except Exception as e:
            logger.error(f'❌ Problem getting thread state details: `{str(e)}`.')
            raise