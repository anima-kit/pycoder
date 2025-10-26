## tests.unit.docs.test_unit_md_splitter
from unittest import TestCase
from unittest.mock import patch, MagicMock
from langchain_classic.schema import Document
from pyfiles.docs.markdown_splitter import MarkdownSplitter, MARKDOWN_SEPARATORS

class TestMarkdownSplitterUnit(TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.source = "test_file.md"
        self.content = "# Header\n\nContent here\n\n## Subheader\n\nMore content"
        self.chunk_size = 512
        
    def test_init_success(self):
        """Test successful initialization of MarkdownSplitter"""
        splitter = MarkdownSplitter(self.source, self.content, self.chunk_size)
        self.assertEqual(splitter.source, "test_file.md")
        self.assertEqual(splitter.content, self.content)
        self.assertEqual(splitter.chunk_size, self.chunk_size)
        self.assertEqual(splitter.markdown_separators, MARKDOWN_SEPARATORS)
        
    def test_create_document_success(self):
        """Test successful document creation"""
        splitter = MarkdownSplitter(self.source, self.content)
        doc = splitter._create_document(self.content)
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.page_content, self.content)
        self.assertEqual(doc.metadata["source"], "test_file.md")
            
    def test_create_document_with_exception(self):
        """Test exception handling in _create_document method"""
        splitter = MarkdownSplitter(self.source, self.content)
        with patch('langchain_classic.schema.Document.__init__') as mock_document_init:
            mock_document_init.side_effect = Exception("Document creation failed")
            with self.assertRaises(Exception):
                splitter._create_document(self.content)
        
    def test_split_success_with_content(self):
        """Test successful splitting with content"""
        splitter = MarkdownSplitter(self.source, self.content, self.chunk_size)
        with patch('langchain_classic.text_splitter.RecursiveCharacterTextSplitter') as mock_splitter_class:
            mock_splitter_instance = MagicMock()
            mock_splitter_instance.split_documents.return_value = [
                Document(page_content="chunk1", metadata={"source": "test_file.md"}),
                Document(page_content="chunk2", metadata={"source": "test_file.md"})
            ]
            mock_splitter_class.return_value = mock_splitter_instance
            result = splitter.split()
            self.assertIsInstance(result, list)
            self.assertGreaterEqual(len(result), 1)
            self.assertIsInstance(result[0], Document)
        
    def test_split_with_exception(self):
        """Test exception handling in split method"""
        splitter = MarkdownSplitter(self.source, self.content, self.chunk_size)
        with patch('langchain_classic.text_splitter.RecursiveCharacterTextSplitter.__init__') as mock_splitter_init:
            mock_splitter_init.side_effect = Exception("Splitting failed")
            with self.assertRaises(Exception):
                splitter.split()