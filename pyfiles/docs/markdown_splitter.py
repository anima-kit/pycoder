### pyfiles.docs.markdown_splitter
## This file creates a class for creating and splitting LangChain documents according to Markdown formatting.

## External imports
from os.path import basename
from langchain_classic.schema import Document
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter 
from typing import List

## Internal imports
from pyfiles.docs.base_splitter import BaseSplitter
from pyfiles.bases.logger import logger

# We use a list of separators tailored for splitting Markdown documents
# This list is taken from LangChain's MarkdownTextSplitter class
MARKDOWN_SEPARATORS: List[str] = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

## The Markdown splitter manager
class MarkdownSplitter(BaseSplitter):   
    """
    A class for creating and splitting documents from Markdown content.

    Attributes
    ------------
        source: str
            The document source.
        content: str
            The content of the document.
        chunk_size: int
            The chunk size for splitting the content into multiple documents
        markdown_separators: List[str]
            The specific separators to use for splitting Markdown documents.
    """
    def __init__(
        self, 
        source: str, 
        content: str, 
        chunk_size: int = 512, 
        markdown_separators: List[str] = MARKDOWN_SEPARATORS
    ):
        """
        Initialize the Markdown splitter.

        Args
        ------------
            source: str
                The document source.
            content: str
                The content of the document.
            chunk_size: int
                The chunk size for splitting the content into multiple documents.
            markdown_separators: List[str]
                The specific separators to use for splitting Markdown documents.
        """
        super().__init__(
            source, 
            content, 
            chunk_size
        )
        self.markdown_separators = markdown_separators

    ## Split the documents 
    def split(
        self
    ) -> List[Document]:
        """
        Split created documents.

        Returns
        ------------
            List[Document]: 
                List of documents created by splitting.
            
        Raises
        ------------
            Exception: 
                If splitting the documents fails, error is logged and raised.
        """
        try:
            ## Create the document from the Markdown content
            docs: List[Document] = []
            doc: Document = self._create_document(self.content)
            ## Split the document
            # If content is empty, just pass original document
            if self.content=='':
                docs=[doc]
            # Else, split the document according to the chunk size and markdown splitters
            else: 
                text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=int(self.chunk_size / 10),
                    separators=self.markdown_separators,
                )
                docs.extend(text_splitter.split_documents([doc]))
            return docs
        except Exception as e:
            logger.error(f'❌ Problem splitting Markdown documents: `{str(e)}`')
            raise
