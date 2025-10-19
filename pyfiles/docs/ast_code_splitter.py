### pyfiles.docs.ast_code_splitter
## This file creates a class for creating and splitting LangChain documents according to Python formatting.

## External imports
from ast import (
    parse, 
    get_docstring,
    get_source_segment,
    FunctionDef,
    ClassDef,
    AsyncFunctionDef,
    Import, 
    Name,
    Expr,
    ImportFrom,
    Assign,
    Str
)
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language
)
from langchain.schema import Document
from typing import List, Dict, Any

## Internal imports
from pyfiles.docs.base_splitter import BaseSplitter
from pyfiles.bases.logger import logger


## The Python splitter manager
class ASTCodeSplitter(BaseSplitter):
    def __init__(
        self, 
        source: str, 
        content: str, 
        chunk_size: int = 512
    ): 
        """
        Initialize the Python splitter.

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
        self.tree = parse(content)
        self.docstring = get_docstring(self.tree)

    ## Create the document 
    def _create_document(
        self, 
        content: str,
        **kwargs
    ) -> Document:
        """
        Create the document.

        Args
        ------------
            node: AST
                The node to parse.
            content: str
                The content to add to the document.
            section_type: str
                The type of node processed.
            name: str
                The name of the node processed.
            parent_class (Optional): str | None
                The name of the parent class.

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
            ## Get additional args
            node = kwargs.get("node")
            section_type = kwargs.get("section_type")
            name = kwargs.get("name")
            parent_class = kwargs.get("parent_class")

            ## Get docstring if class or function.
            docstring: str | None = ""
            if isinstance(node, (FunctionDef, ClassDef, AsyncFunctionDef)):
                docstring = get_docstring(node)
            ## Create the document with appropriate metadata
            metadata: Dict[str, Any] = {
                "source": self.source,
                "type": type(node).__name__,
                "name": name,
                "section_type": section_type,
                "docstring": docstring or ""
            }
            if parent_class:
                metadata["parent_class"] = parent_class
            return Document(page_content=content, metadata=metadata)
        except Exception as e:
            logger.error(f'❌ Problem creating document with Python splitter: `{str(e)}`')
            raise

    ## Prepend comments to content
    def _prepend_comments(
        self, 
        content: str, 
        comments: List[str]
    ) -> str:
        """
        Prepend the comments to the content.

        Args
        ------------
            content: str
                The content to which comments will be added.
            comments: str
                The comments to add.

        Returns
        ------------
            str:
                The content with the prepended comments.
            
        Raises
        ------------
            Exception: 
                If prepending the comments fails, error is logged and raised.
        """
        try:
            if comments:
                return "\n".join(comments) + "\n" + content
            return content
        except Exception as e:
            logger.error(f'❌ Problem prepending comments to content: `{str(e)}`')
            raise

    ## Process import groups
    def _process_import_group(
        self,
        documents: List[Document], 
        import_nodes: List[Any], 
        pending_comments: List[str], 
        parent_class: str | None = None
    ) -> None:
        """
        Process group of import statements.

        Args
        ------------
            documents: List[Document]
                The list of documents from which to process import groups.
            import_nodes: AST
                The import nodes.
            pending_comments: List[str]
                List of comments to add to content.
            parent_class (Optional): str | None
                The name of the parent class.
            
        Raises
        ------------
            Exception: 
                If processing the import groups fails, error is logged and raised.
        """
        try:
            ## Get all imports
            import_content: str = ''
            for node in import_nodes:
                source_segment = get_source_segment(self.content, node)
                if source_segment:
                    import_content = import_content + f'\n{source_segment}'
            ## If imports found
            if import_content:
                # Add comments, create name
                import_content = self._prepend_comments(import_content, pending_comments)
                name: str = ",".join(
                    alias.name for imp_node in import_nodes
                    for alias in imp_node.names
                    if isinstance(imp_node, Import)
                )[:50]
                # Create document with appropriate metadata
                doc: Document = self._create_document(
                    content=import_content,
                    node=import_nodes[0],
                    section_type="import_group",
                    name=name,
                    parent_class=parent_class
                )
                documents.append(doc)
        except Exception as e:
            logger.error(f'❌ Problem processing import groups: `{str(e)}`')
            raise

    ## Process assignment groups
    def _process_assign_group(
        self, 
        documents: List[Document], 
        assign_nodes: List[Any],
        pending_comments: List[str], 
        parent_class: str | None = None
    ) -> None:
        """
        Process group of assignment statements.

        Args
        ------------
            documents: List[Document]
                The list of documents from which to process import groups.
            assign_nodes: AST
                The assignment nodes.
            pending_comments: List[str]
                List of comments to add to content.
            parent_class (Optional): str | None
                The name of the parent class.
            
        Raises
        ------------
            Exception: 
                If processing the assignment groups fails, error is logged and raised.
        """
        try:
            ## Get all assignments
            assign_content: str = ''
            for node in assign_nodes:
                source_segment = get_source_segment(self.content, node)
                if source_segment:
                    assign_content = assign_content + f'\n{source_segment}'
            ## If any assignments found
            if assign_content:
                # Add comments, create name
                assign_content = self._prepend_comments(assign_content, pending_comments)
                variables = []
                for node in assign_nodes:
                    targets = [t.id for t in node.targets if isinstance(t, Name)]
                    variables.extend(targets)
                name = ", ".join(set(variables))[:100]
                # Create document with appropriate metadata
                doc = self._create_document(
                    content=assign_content,
                    node=assign_nodes[0],
                    section_type="assignment_group",
                    name=name,
                    parent_class=parent_class
                )
                documents.append(doc)
        except Exception as e:
            logger.error(f'❌ Problem processing assignment groups: `{str(e)}`')
            raise

    ## Create the documents by processing nodes
    def _process_nodes(
        self, 
        nodes: List[Any], 
        parent_class: str | None = None
    ) -> List[Document]:
        """
        Process all nodes.

        Args
        ------------
            nodes: AST
                The node.
            parent_class (Optional): str | None
                The name of the parent class.

        Returns
        ------------
            List[Document]:
                The list of documents created.

        Raises
        ------------
            Exception: 
                If processing all documents nodes fails, error is logged and raised.
        """
        try:
            documents: List[Document] = []
            current_import_nodes: List[Any] = []
            current_assign_nodes: List[Any] = []
            pending_comments: List[str] = []
            ## Loop over all document nodes
            for node in nodes:
                # Get comments
                if isinstance(node, Expr) and isinstance(node.value, Str):
                    comment_line = get_source_segment(self.content, node)
                    if comment_line:
                        pending_comments.append(comment_line.strip())
                    continue

                ## Get import nodes
                if isinstance(node, (Import, ImportFrom)):
                    ## Process assignment nodes before appending import nodes
                    if current_assign_nodes:
                        self._process_assign_group(
                            documents, 
                            current_assign_nodes, 
                            pending_comments, 
                            parent_class=parent_class
                        )
                        current_assign_nodes = []
                    current_import_nodes.append(node)
                    continue

                ## Get assignment nodes
                if isinstance(node, Assign):
                    ## Process import nodes before appending assignment nodes
                    if current_import_nodes:
                        self._process_import_group(
                            documents, 
                            current_import_nodes, 
                            pending_comments, 
                            parent_class=parent_class
                        )
                        current_import_nodes = []
                    current_assign_nodes.append(node)
                    continue

                ## Check if any remaining import and assignment groups
                if current_import_nodes:
                    self._process_import_group(
                        documents, 
                        current_import_nodes, 
                        pending_comments, 
                        parent_class=parent_class
                    )
                    current_import_nodes = []
                if current_assign_nodes:
                    self._process_assign_group(
                        documents, 
                        current_assign_nodes, 
                        pending_comments, 
                        parent_class=parent_class
                    )
                    current_assign_nodes = []

                ## Get content of node
                content = get_source_segment(self.content, node)
                if not content or not content.strip():
                    continue
                content = self._prepend_comments(content, pending_comments)

                ## Get all class definitions
                if isinstance(node, ClassDef):
                    ## Make sure to process __init__ method with class definition
                    init_node = None
                    for body_node in node.body:
                        if isinstance(body_node, FunctionDef) and body_node.name == '__init__':
                            init_node = body_node
                            break
                    if init_node:
                        class_source = get_source_segment(self.content, node)
                        init_source = get_source_segment(self.content, init_node)
                        if init_source and class_source:
                            init_start = class_source.find(init_source)
                            if init_start != -1:
                                combined_source = class_source[:init_start + len(init_source)]
                                combined_source = self._prepend_comments(combined_source, pending_comments)
                                ## Create a document for the class definition
                                doc = self._create_document(
                                    content=combined_source,
                                    node=node,
                                    section_type="class_with_init",
                                    name=node.name,
                                    parent_class=parent_class
                                )
                                documents.append(doc)

                        ## Check remaining nodes recursively
                        remaining_nodes = [n for n in node.body if n is not init_node]
                        body_docs = self._process_nodes(remaining_nodes, parent_class=node.name)
                        documents.extend(body_docs)
                    else:
                        body_docs = self._process_nodes(node.body, parent_class=node.name)
                        documents.extend(body_docs)
                    continue

                ## Get all function definitions
                elif isinstance(node, (FunctionDef, AsyncFunctionDef)):
                    name = node.name
                    section_type = "function"
                    ## Create a document for the function
                    doc = self._create_document(
                        content=content, 
                        node=node, 
                        section_type=section_type, 
                        name=name, 
                        parent_class=parent_class
                    )
                    documents.append(doc)
                    continue

                ## Get all other node types
                else:
                    section_type = type(node).__name__
                    name = getattr(node, 'name', '')
                    ## Create a document for this node
                    doc = self._create_document(
                        content=content, 
                        node=node, 
                        section_type=section_type, 
                        name=name, 
                        parent_class=parent_class
                    )
                    documents.append(doc)

            ## Check if any remaining import and assignemtn groups
            if current_import_nodes:
                self._process_import_group(documents, current_import_nodes, pending_comments, parent_class=parent_class)
            if current_assign_nodes:
                self._process_assign_group(documents, current_assign_nodes, pending_comments, parent_class=parent_class)
            return documents
        except Exception as e:
            logger.error(f'❌ Problem processing nodes: `{str(e)}`')
            raise

    ## Create and split the documents
    def split(
        self
    ) -> List[Document]:
        """
        Create all documents by processing nodes and split according to the Python schema if no processed nodes.

        Returns
        ------------
            List[Document]:
                The list of documents created.

        Raises
        ------------
            Exception: 
                If splitting the document fails, error is logged and raised.
        """
        try:
            ## Get all documents from processing nodes
            documents = self._process_nodes(self.tree.body)
            ## If no documents, just split according to Python schema
            if not documents:
                splitter = RecursiveCharacterTextSplitter.from_language(Language.PYTHON, chunk_size=self.chunk_size)
                docs = splitter.create_documents([self.content])
                for doc in docs:
                    doc.metadata.update({
                        "source": self.source,
                        "type": "Module",
                        "name": "",
                        "section_type": "fallback",
                        "docstring": self.docstring or ""
                    })
                documents.extend(docs)
            return documents
        except Exception as e:
            logger.error(f'❌ Problem splitting documents with Python splitter: `{str(e)}`')
            raise