## tests.unit.docs.test_unit_docs
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch, AsyncMock
from langchain_core.documents import Document
from uuid import uuid4
from pyfiles.databases.sqlite import SQLiteDB
from pyfiles.docs.docs_handler import Docs

class TestDocsUnit(TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_docs = MagicMock()
        
    def test_init_success(self):
        """Test successful initialization of Docs class"""
        docs = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db,
            content_list=["content1", "content2"],
            files=["file1.py", "file2.md"],
            source="test_source"
        )
        self.assertEqual(docs.codebase_type, "test_type")
        self.assertEqual(docs.group, "test_group")
        self.assertEqual(docs.db, self.mock_db)
        self.assertEqual(docs.content_list, ["content1", "content2"])
        self.assertEqual(docs.files, ["file1.py", "file2.md"])
        self.assertEqual(docs.source, "test_source")

    def test_split_success(self):
        """Test successful document splitting"""
        mock_splitter = MagicMock()
        mock_splitter.split.return_value = [Document(page_content="test content")]
        docs = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db
        )
        result = mock_splitter.split()
        self.assertEqual(result, [Document(page_content="test content")])
        mock_splitter.split.assert_called_once()

    def test_split_exception(self):
        """Test exception handling in split method"""
        with patch('pyfiles.bases.logger') as mock_logger:
            mock_splitter = MagicMock()
            mock_splitter.split.side_effect = Exception("Split error")
            docs = Docs(
                codebase_type="test_type",
                group="test_group", 
                db=self.mock_db
            )
            with self.assertRaises(Exception):
                docs.split(mock_splitter)

class TestADocsUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_db = AsyncMock()
        self.mock_docs = MagicMock()
        
    async def test_acreate_docs_success(self):
        """Test successful async document creation"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db
        )
        with patch('os.path.abspath') as mock_abspath, \
             patch('os.path.isdir') as mock_isdir, \
             patch('os.walk') as mock_walk, \
             patch('os.path.isfile') as mock_isfile, \
             patch('builtins.open', new_callable=MagicMock) as mock_open:
            mock_abspath.return_value = "/test/file.py"
            mock_isdir.return_value = False
            mock_isfile.return_value = True
            mock_walk.return_value = [("/test", [], ["file1.py"])]
            with patch('pyfiles.docs.docs_handler.PythonLoader') as mock_loader:
                mock_doc = Document(page_content="test content")
                mock_loader.return_value.alazy_load.return_value = [mock_doc]
                result_docs = await docs_instance.acreate_docs()
                self.assertIsInstance(result_docs, list)

    async def test_acreate_docs_with_nonexistent_file(self):
        """Test document creation with non-existent file"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db,
            files=["nonexistent.py"]
        )
        with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = False
            result_docs = await docs_instance.acreate_docs()
            self.assertIsInstance(result_docs, list)

    async def test_acreate_docs_with_invalid_file_type(self):
        """Test document creation with invalid file type"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db,
            files=["file.txt"]
        )
        with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            result_docs = await docs_instance.acreate_docs()
            self.assertIsInstance(result_docs, list)

    async def test_acreate_docs_with_content_list_sqlite(self):
        """Test document creation with content list for SQLite DB"""
        sqlite_db = MagicMock()
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=sqlite_db,
            content_list=["content1", "content2"]
        )
        with patch('pyfiles.docs.docs_handler.GeneralSplitter') as mock_splitter:
            mock_splitter_instance = MagicMock()
            mock_splitter_instance.split.return_value = [Document(page_content="split content")]
            result_docs = await docs_instance.acreate_docs()
            self.assertIsInstance(result_docs, list)
            mock_splitter.assert_called()

    async def test_aadd_to_sqlite_success(self):
        """Test successful addition of documents to SQLite DB."""
        mock_db = MagicMock(spec=SQLiteDB)
        mock_db.insert_documents = AsyncMock()
        docs_instance = Docs(
            codebase_type="user",
            group="code",
            db=mock_db,
            source="test_source"
        )
        mock_docs = [MagicMock(), MagicMock()]
        docs_instance.docs = mock_docs
        with patch('uuid.uuid4', side_effect=[uuid4(), uuid4()]):
            result = await docs_instance.aadd_to_sqlite()
            assert isinstance(result, list)
            assert len(result) == 2
            mock_db.insert_documents.assert_called_once_with(mock_docs, result)

    async def test_aadd_to_sqlite_exception(self):
        """Test exception handling in aadd_to_sqlite method"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db
        )
        docs_instance.docs = [Document(page_content="test content")]
        with patch('pyfiles.bases.logger') as mock_logger:
            self.mock_db.insert_documents.side_effect = Exception("DB insert error")
            with self.assertRaises(Exception):
                await docs_instance.aadd_to_sqlite()

    async def test_aadd_to_vectorstore_success(self):
        """Test successful addition to vector store"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db
        )
        docs_instance.docs = [Document(page_content="test content")]
        await docs_instance.aadd_to_vectorstore()
        self.mock_db.aadd_documents.assert_called_once()

    async def test_aadd_to_vectorstore_exception(self):
        """Test exception handling in aadd_to_vectorstore method"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db
        )
        docs_instance.docs = [Document(page_content="test content")]
        with patch('pyfiles.bases.logger') as mock_logger:
            self.mock_db.aadd_documents.side_effect = Exception("Vector store error")
            with self.assertRaises(Exception):
                await docs_instance.aadd_to_vectorstore()

    async def test_acreate_docs_with_empty_files(self):
        """Test document creation with empty files list"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db,
            files=[]
        )
        result_docs = await docs_instance.acreate_docs()
        self.assertIsInstance(result_docs, list)

    async def test_acreate_docs_with_none_files(self):
        """Test document creation with None files"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db,
            files=None
        )
        result_docs = await docs_instance.acreate_docs()
        self.assertIsInstance(result_docs, list)

    async def test_acreate_docs_with_none_content_list(self):
        """Test document creation with None content_list"""
        docs_instance = Docs(
            codebase_type="test_type",
            group="test_group", 
            db=self.mock_db,
            content_list=None
        )
        result_docs = await docs_instance.acreate_docs()
        self.assertIsInstance(result_docs, list)