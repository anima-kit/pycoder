### pyfiles.docs.general_splitter
## This file creates a class for creating LangChain documents from free content (not Markdown or Python).

## External imports
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

## Internal imports
from pyfiles.docs.base_splitter import BaseSplitter
from pyfiles.bases.logger import logger

## The general splitter manager
class GeneralSplitter(BaseSplitter):  
    """
    A class for creating and splitting documents from general content.

    Attributes
    ------------
        source: str
            The document source.
        content: str
            The content of the document.
        chunk_size: int
            The chunk size for splitting the content into multiple documents
    """ 
    def __init__(
        self, 
        source: str, 
        content: str, 
        chunk_size: int = 512
    ):
        """
        Initialize the general splitter.

        Args
        ------------
            source: str
                The document source.
            content: str
                The content of the document.
            chunk_size: int
                The chunk size for splitting the content into multiple documents.
        """
        super().__init__(
            source, 
            content, 
            chunk_size
        )
            
    ## Create and split the documents
    def split(self) -> List[Document]:
        """
        Create document and forgo splitting.

        Returns
        ------------
            List[Document]: 
                List of documents created.
            
        Raises
        ------------
            Exception: 
                If creating the documents fails, error is logged and raised.
        """
        try:
            ## Create the document and forgo splitting for now
            doc: Document = self._create_document(self.content)
            docs: List[Document] = [doc]
            return docs
        except Exception as e:
            logger.error(f'❌ Problem splitting general documents: `{str(e)}`')
            raise
