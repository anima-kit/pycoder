## tests.unit.bases.test_unit_users
from unittest import TestCase, IsolatedAsyncioTestCase
import tempfile
import os
import aiosqlite
from unittest.mock import patch, AsyncMock
from langchain.docstore.document import Document
from pyfiles.databases.sqlite import SQLiteDB

class TestSQLiteUnit(TestCase):
    def setUp(self):
        self.db_path = ':memory:'
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = SQLiteDB(self.temp_db_path)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)

    def test_init_memory_db(self):
        """Test successful initialization with memory database"""
        db = SQLiteDB(self.db_path)
        self.assertEqual(db.db_path, self.db_path)

    def test_init_file_db(self):
        """Test successful initialization with file database"""
        self.assertEqual(self.db.db_path, self.temp_db_path)

    def test_delete_db_file_success(self):
        """Test successful deletion of database file"""
        with open(self.temp_db_path, 'w') as f:
            f.write('test')
        self.db.delete_db_file()
        self.assertFalse(os.path.exists(self.temp_db_path))

    def test_delete_db_file_not_exists(self):
        """Test deletion of non-existent database file"""
        try:
            self.db.delete_db_file()
        except Exception as e:
            self.fail(f"delete_db_file raised exception: {e}")


class TestASQLiteUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_path = ':memory:'
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = SQLiteDB(self.temp_db_path)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)

    async def test_create_table_success(self):
        """Test successful table creation"""
        async with aiosqlite.connect(self.temp_db_path) as conn:
            await self.db._create_table(conn)
            cursor = await conn.cursor()
            await cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
            result = await cursor.fetchone()
            self.assertIsNotNone(result)

    async def test_insert_documents_success(self):
        """Test successful document insertion"""
        doc1 = Document(page_content="Content 1", metadata={"group": "test_group"})
        doc2 = Document(page_content="Content 2", metadata={"group": "test_group"})
        await self.db.insert_documents([doc1, doc2], ["id1", "id2"])
        async with aiosqlite.connect(self.temp_db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM documents")
            count = await cursor.fetchone()
            self.assertEqual(count[0], 2)

    async def test_get_documents_by_group_success(self):
        """Test successful retrieval of documents by group"""
        doc1 = Document(page_content="Content 1", metadata={"group": "test_group"})
        doc2 = Document(page_content="Content 2", metadata={"group": "test_group"})
        await self.db.insert_documents([doc1, doc2], ["id1", "id2"])
        docs = await self.db.get_documents_by_group("test_group")
        self.assertEqual(len(docs), 2)
        
    async def test_delete_documents_by_id_success(self):
        """Test successful deletion of documents by ID"""
        doc = Document(page_content="Content", metadata={"group": "test_group"})
        await self.db.insert_documents([doc], ["id1"])
        async with aiosqlite.connect(self.temp_db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM documents")
            count = await cursor.fetchone()
            self.assertEqual(count[0], 1)
        await self.db.delete_documents_by_id(["id1"])
        async with aiosqlite.connect(self.temp_db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM documents")
            count = await cursor.fetchone()
            self.assertEqual(count[0], 0)

    async def test_delete_documents_by_source_success(self):
        """Test successful deletion of documents by source"""
        doc = Document(page_content="Content", metadata={"source": "test_source", "group": "test_group"})
        await self.db.insert_documents([doc], ["id1"])
        async with aiosqlite.connect(self.temp_db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM documents")
            count = await cursor.fetchone()
            self.assertEqual(count[0], 1)
        await self.db.delete_documents_by_source(["test_source"], 'test_group')
        async with aiosqlite.connect(self.temp_db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM documents")
            count = await cursor.fetchone()
            self.assertEqual(count[0], 0)

    async def test_get_codebase_list_success(self):
        """Test successful retrieval of codebase list"""
        doc1 = Document(page_content="Content 1", metadata={"group": "codebase_1", "codebase_type": "type1"})
        doc2 = Document(page_content="Content 2", metadata={"group": "codebase_2", "codebase_type": "type1"})
        await self.db.insert_documents([doc1, doc2], ["id1", "id2"])
        codebases = await self.db.get_codebase_list("type1")
        self.assertEqual(len(codebases), 1)

    async def test_create_table_exception_handling(self):
        """Test exception handling in _create_table"""
        with patch('aiosqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            with self.assertRaises(Exception):
                await self.db._create_table()

    async def test_insert_documents_exception_handling(self):
        """Test exception handling in insert_documents"""
        with patch('pyfiles.databases.sqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            doc = Document(page_content="Content", metadata={"group": "test_group"})
            with self.assertRaises(Exception):
                await self.db.insert_documents([doc], ["id1"])

    async def test_get_documents_by_group_exception_handling(self):
        """Test exception handling in get_documents_by_group"""
        with patch('pyfiles.databases.sqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            with self.assertRaises(Exception):
                await self.db.get_documents_by_group("test_group")

    async def test_clear_exception_handling(self):
        """Test exception handling in clear"""
        with patch('pyfiles.databases.sqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            with self.assertRaises(Exception):
                await self.db.clear()

    async def test_delete_documents_by_id_exception_handling(self):
        """Test exception handling in delete_documents_by_id"""
        with patch('pyfiles.databases.sqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            with self.assertRaises(Exception):
                await self.db.delete_documents_by_id(["id1"])

    async def test_delete_documents_by_source_exception_handling(self):
        """Test exception handling in delete_documents_by_source"""
        with patch('pyfiles.databases.sqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            with self.assertRaises(Exception):
                await self.db.delete_documents_by_source(["source1"])

    async def test_get_codebase_list_exception_handling(self):
        """Test exception handling in get_codebase_list"""
        with patch('pyfiles.databases.sqlite.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")
            with self.assertRaises(Exception):
                await self.db.get_codebase_list("type1")