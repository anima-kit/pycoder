### pyfiles.docs.base_splitter
## This file creates a base class for creating and splitting documents.

## External imports
from abc import ABC, abstractmethod
from langchain_classic.schema import Document
from typing import Dict, List, Any

## Internal imports
from pyfiles.bases.logger import logger

## The base class
class BaseSplitter(ABC):
    """
    Abstract base class for all document splitters.

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
        Initialize the base class.

        Args
        ------------
            source: str
                The document source.
            content: str
                The content of the document.
            chunk_size: int
                The chunk size for splitting the content into multiple documents
            
        Raises
        ------------
            Exception: 
                If initializing the base class fails, error is logged and raised.
        """
        try:
            self.source = source
            self.content = content
            self.chunk_size = chunk_size
        except Exception as e:
            logger.error(f'❌ Problem creating base class: `{str(e)}`')
            raise
    
    ## Create the document
    def _create_document(
        self, 
        content: str,
        **kwargs: Any
    ) -> Document:
        """
        Create the document.

        Args
        ------------
            content: str
                The content of the document.

        Returns
        ------------
            Document:
                The created document.
            
        Raises
        ------------
            Exception: 
                If creating the document fails, error is logged and raised.
        """
        try:
            ## Create the document with metadata
            metadata: Dict[str, str] = {
                "source": self.source
            }
            return Document(page_content=content, metadata=metadata)
        except Exception as e:
            logger.error(f'❌ Problem creating the document: `{str(e)}`')
            raise
    
    @abstractmethod
    def split(
        self
    ) -> List[Document]:
        """
        Abstract method to be implemented by all child classes

        Returns
        ------------
            List[Document]:
                A list of all created documents.
        """
        pass
