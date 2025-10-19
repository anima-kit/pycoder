### pyfiles.docs.docs_handler
## This file can be used to create LangChain documents from Markdown, Python, or general free content.
## The documents can be saved to an SQLite DB or a Milvus vectorstore.

## External imports
from os import walk
from os.path import (
    abspath, 
    isdir, 
    join, 
    isfile, 
    basename
)
from uuid import uuid4
from gradio import File
from langchain.schema import Document
from langchain_community.document_loaders import (
    PythonLoader, 
    UnstructuredMarkdownLoader
)
from typing import Dict, List, Tuple

## Internal imports
from pyfiles.bases.logger import logger
from pyfiles.databases.milvus import Milvus
from pyfiles.databases.sqlite import SQLiteDB
from pyfiles.docs.ast_code_splitter import ASTCodeSplitter
from pyfiles.docs.general_splitter import GeneralSplitter
from pyfiles.docs.markdown_splitter import MarkdownSplitter

## The class to manage documents
class Docs:
    """
    A documents manager class that can be used to create LangChain documents and store them in SQLite DB's or Milvus vectorstores.

    Attributes
    ------------
        codebase_type: str
            The type of codebase.
            Can be `user` or `external`.
        group: str
            The group associated with the document.
            Can be associated with `threads` or `code`.
        db: SQLiteDB | Milvus
            The DB or vectorstore to store the documents.
            Can be an SQLite DB or a Milvus vectorstore.
        source (Optional): str
            The source associated with the document.
        content_list (Optional): List[str] | None
            The list of content to add to the documents.
        files (Optional): List[str] | None
            The list of files from which to create the documents.
        docs: List[Document]
            The list of created documents.  
    """
    def __init__(
        self, 
        codebase_type: str, 
        group: str, 
        db: SQLiteDB | Milvus, 
        source: str = '',
        content_list: List[str] | None = None, 
        files: List[str] | None = None, 
    ):
        """
        Initialize the document manager.

        Args
        ------------
            codebase_type: str
                The type of codebase.
                Can be `user` or `external`.
            group: str
                The group associated with the document.
                Can be associated with `threads` or `code`.
            db: SQLiteDB | Milvus
                The DB or vectorstore to store the documents.
                Can be an SQLite DB or a Milvus vectorstore.
            source (Optional): str
                The source associated with the document.
            content_list (Optional): List[str] | None
                The list of content to add to the documents.
            files (Optional): List[str] | None
                The list of files from which to create the documents.
            
        Raises
        ------------
            Exception: 
                If initializing the document manager fails, error is logged and raised.
        """
        try:
            self.files = files
            self.content_list = content_list
            self.db = db
            self.group = group
            self.source = source
            self.codebase_type = codebase_type
            # Docs attribute will need to be created after initializing class
            self.docs: List[Document] | None = None
        except Exception as e:
            logger.error(f'❌ Problem initializing Docs: `{str(e)}`')
            raise

    def _create_metadata(
        self,
        group: str,
        file: str
    ) -> Dict[str, str]:
        """
        Create metadata for a Python or Markdown document.

        Returns
        ------------
            group: str
                The group associated with the document.
            file: str
                The file path.
            
        Raises
        ------------
            Exception: 
                If creating the metadata fails, error is logged and raised.
        """
        metadata: Dict[str, str] = {
            "codebase_type": self.codebase_type,
            "group": group, 
            "source": basename(file)
        }
        return metadata

    def _create_py_doc(
        self,
        group: str,
        file: str,
        doc: Document
    ) -> Document:
        """
        Format metadata and content for a Python file.

        Returns
        ------------
            group: str
                The group associated with the document.
            file: str
                The file path.
            doc: Document
                The original document to format.
            
        Raises
        ------------
            Exception: 
                If formating the Python document fails, error is logged and raised.
        """
        metadata: Dict[str, str] = self._create_metadata(
            group=group,
            file=file
        )
        doc.metadata["codebase_type"] = self.codebase_type
        doc.metadata["group"] = group
        doc.metadata["source"] = basename(file)
        doc.page_content = f"```python \n {doc.page_content} \n ```"
        return doc

    async def acreate_docs(
        self
    ) -> List[Document]:
        """
        Create documents to persist to storage.

        Returns
        ------------
            List[Document]:
                A list of created documents.
            
        Raises
        ------------
            Exception: 
                If creating the documents fails, error is logged and raised.
        """
        logger.info(f'⚙️ Creating documents.')
        try:
            ## Create the placeholder variables for docs, loaders, and splitters
            docs: List[Document] = []
            loader: PythonLoader | UnstructuredMarkdownLoader | None = None
            text_splitter: ASTCodeSplitter | MarkdownSplitter | GeneralSplitter | None = None

            ## Deal with file uploads
            if self.files!=None:
                ## Reject any non Python or Markdown files
                for file in self.files: 
                    if not isfile(file):
                        continue
                    if not (file.lower().endswith('.py') or file.lower().endswith('.md')):
                        continue  
                
                    docs_processed: List[Document] = []
                    ## Deal with Python files
                    if file.endswith('.py'):
                        loader = PythonLoader(file)
                        async for doc in loader.alazy_load():
                            if isinstance(self.db, SQLiteDB):
                                doc = self._create_py_doc(
                                    group=self.group,
                                    file=file,
                                    doc=doc
                                )
                                docs_processed.extend([doc])
                            else:
                                group = f'{self.group}_part'
                                text_splitter = ASTCodeSplitter(
                                    source=file, 
                                    content=doc.page_content
                                )
                                split_docs: List[Document] = text_splitter.split()
                                for split_doc in split_docs:
                                    split_doc = self._create_py_doc(
                                        group=group,
                                        file=file,
                                        doc=split_doc
                                    )
                                    docs_processed.extend([split_doc])

                    ## Deal with Markdown files
                    elif file.endswith('.md'):
                        if isinstance(self.db, SQLiteDB):
                            with open(file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            group = self.group
                            metadata = self._create_metadata(
                                group=group,
                                file=file
                            )
                            doc = Document(page_content=content, metadata=metadata)
                            docs_processed.extend([doc])
                        else:
                            loader = UnstructuredMarkdownLoader(file)
                            async for doc in loader.alazy_load():
                                group=f'{self.group}_part'
                                text_splitter = MarkdownSplitter(
                                    source=file, 
                                    content=doc.page_content
                                )
                                split_docs = text_splitter.split()
                                for split_doc in split_docs:
                                    metadata = self._create_metadata(
                                        group=group,
                                        file=file
                                    )
                                    split_doc.metadata = metadata
                                    docs_processed.extend([split_doc])    

                    ## TODO: Can handle more file types        
                    else:
                        pass
                    docs.extend(docs_processed)

            ## Handle free content
            if self.content_list!=None:
                for content in self.content_list:
                    if isinstance(self.db, SQLiteDB):
                        group = self.group
                    else:
                        group = f'{self.group}_part'
                    text_splitter = GeneralSplitter(
                        source=self.source, 
                        content=content
                    )
                    docs_processed=text_splitter.split()
                    for doc in docs_processed:
                        doc.metadata["group"] = group
                        doc.metadata["codebase_type"] = self.codebase_type
                    docs.extend(docs_processed)
            logger.info(f'✅ Successfully created documents.')
            return docs
        except Exception as e:
            logger.error(f'❌ Problem creating documents: `{str(e)}`')
            raise

    async def aadd_to_sqlite(
        self
    ) -> List[str]:
        """
        Add document to SQLite DB.
            
        Raises
        ------------
            Exception: 
                If adding the documents fails, error is logged and raised.
        """
        logger.info(f'⚙️ Adding documents to SQLite DB.')
        try:
            if isinstance(self.db, SQLiteDB):
                if self.docs!=None:
                    thread_ids: List[str] = [str(uuid4()) for _ in range(len(self.docs))]
                    if hasattr(self.db, 'insert_documents'):
                        await self.db.insert_documents(self.docs, thread_ids)
                        logger.info(f'✅ Successfully added documents to SQLite DB.')
                        return thread_ids
                    else:
                        raise ValueError(f'❌ The attribute `db` should be an SQLiteDB class with the method `insert_documents`.')
                else:
                    raise ValueError(f'❌ The attribute `docs` should not be None.')
            else:
                raise ValueError(f'❌ The attribute `db` should be an SQLiteDB class to add to SQLiteDB.')
        except Exception as e:
            logger.error(f'❌ Problem adding documents to SQLite DB: `{str(e)}`')
            raise

    async def aadd_to_vectorstore(
        self
    ) -> None:
        """
        Add document to Milvus vectorstore.
            
        Raises
        ------------
            Exception: 
                If adding the documents fails, error is logged and raised.
        """
        logger.info(f'⚙️ Adding documents to Milvus vectorstore.')
        try:
            if self.docs!=None:
                thread_ids: List[str] = [str(uuid4()) for _ in range(len(self.docs))]
                if hasattr(self.db, 'aadd_documents'):
                    if self.docs!=None:
                        await self.db.aadd_documents(
                            documents=self.docs, 
                            ids=thread_ids
                        )
                        logger.info(f'✅ Successfully added documents to Milvus vectorstore.')
                    else:
                        raise ValueError(f'❌ The attributes `docs` should not be None.')
                else:
                    raise ValueError(f'❌ The attribute `db` should be a Milvus class with the method `aadd_documents`.')
            else:
                raise ValueError(f'❌ The attribute `docs` should not be None.')
        except Exception as e:
            logger.error(f'❌ Problem adding documents to Milvus vectorstore: `{str(e)}`')
            raise

    async def add_to_vectorstore(
        self
    ) -> None:
        """
        Add document to Milvus vectorstore.
            
        Raises
        ------------
            Exception: 
                If adding the documents fails, error is logged and raised.
        """
        logger.info(f'⚙️ Adding documents to Milvus vectorstore.')
        try:
            if self.docs!=None:
                thread_ids: List[str] = [str(uuid4()) for _ in range(len(self.docs))]
                if hasattr(self.db, 'add_documents'):
                    if self.docs!=None:
                        await self.db.add_documents(
                            documents=self.docs, 
                            ids=thread_ids
                        )
                        logger.info(f'✅ Successfully added documents to Milvus vectorstore.')
                    else:
                        raise ValueError(f'❌ The attributes `docs` should not be None.')
                else:
                    raise ValueError(f'❌ The attribute `db` should be a Milvus class with the method `aadd_documents`.')
            else:
                raise ValueError(f'❌ The attribute `docs` should not be None.')
        except Exception as e:
            logger.error(f'❌ Problem adding documents to Milvus vectorstore: `{str(e)}`')
            raise