## tests.unit.bases.test_unit_threads
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, AsyncMock, MagicMock
from pyfiles.bases.threads import Threads

class TestThreadsUnit(TestCase):
    def setUp(self):
        self.codebase_type = "test_type"
        self.milvus_db = MagicMock()
        self.sqlite_db = MagicMock()
        self.models = MagicMock()
        self.codebase = "test_codebase"
        self.max_threads = 1000

class TestAThreadsUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.codebase_type = "test_type"
        self.milvus_db = MagicMock()
        self.sqlite_db = MagicMock()
        self.models = MagicMock()
        self.codebase = "test_codebase"
        self.sqlite_db.get_documents_by_group = AsyncMock()
        self.sqlite_db.delete_documents_by_id = AsyncMock()
        self.sqlite_db.insert_documents = AsyncMock()

    async def test_load_all_from_sqlite_success(self):
        """
        Test success of load_all_from_sqlite
        """
        load_type = "code"
        group = f"{self.codebase}_{load_type}"
        mock_results = [("doc1", MagicMock(page_content="test", metadata={"source": "src1", "group": group}))] 
        self.sqlite_db.get_documents_by_group.return_value = mock_results
        threads = Threads(
            codebase_type=self.codebase_type,
            milvus_db=self.milvus_db,
            sqlite_db=self.sqlite_db,
            models=self.models,
            codebase=self.codebase
        )
        result = await threads.load_all_from_sqlite(load_type)
        expected = {
            "doc1": {
                'content': "test",
                'source': "src1", 
                'group': group
            }
        }
        self.assertEqual(result, expected)

    async def test_load_all_from_sqlite_exception(self):
        """
        Test exception handling of load_all_from_sqlite
        """
        load_type = "code"
        self.sqlite_db.get_documents_by_group.side_effect = Exception("Load failed")
        threads = Threads(
            codebase_type=self.codebase_type,
            milvus_db=self.milvus_db,
            sqlite_db=self.sqlite_db,
            models=self.models,
            codebase=self.codebase
        )
        with self.assertRaises(Exception):
            await threads.load_all_from_sqlite(load_type)

    async def test_get_list_success(self):
        """
        Test success of get_list
        """
        load_type = "code"
        mock_state = {
            "thread1": {"source": "file1.py", "content": "test content"},
            "thread2": {"source": "file2.py", "content": "test content"}
        }
        with patch.object(Threads, 'load_all_from_sqlite', return_value=mock_state):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            result = await threads.get_list(load_type)
            self.assertEqual(len(result), 2)
            self.assertIn(("file1.py", "thread1"), result)
            self.assertIn(("file2.py", "thread2"), result)

    async def test_get_list_exception(self):
        """
        Test exception handling of get_list
        """
        load_type = "code"
        with patch.object(Threads, 'load_all_from_sqlite', side_effect=Exception("List failed")):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            with self.assertRaises(Exception):
                await threads.get_list(load_type)

    async def test_delete_success(self):
        """
        Test success of delete
        """
        load_type = "code"
        thread_id = "thread123"
        mock_state = {
            thread_id: {"source": "file.py", "content": "test content"}
        }
        with patch.object(Threads, 'load_all_from_sqlite', return_value=mock_state):
            self.sqlite_db.delete_documents_by_id.return_value = None
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            result = await threads.delete(load_type, thread_id)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 3)
            self.assertIn("Deleted thread", result[2])

    async def test_delete_exception(self):
        """
        Test exception handling of delete
        """
        load_type = "code"
        thread_id = "thread123"
        with patch.object(Threads, 'load_all_from_sqlite', side_effect=Exception("Delete failed")):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            with self.assertRaises(Exception):
                await threads.delete(load_type, thread_id)

    async def test_create_threads_success(self):
        """
        Test success of create
        """
        load_type = "threads"
        name = "test_thread"
        self.sqlite_db.insert_documents.return_value = None
        self.sqlite_db.get_documents_by_group.return_value = []
        mock_list_result = [("file.py", "thread123")]
        with patch.object(Threads, 'get_list', return_value=mock_list_result):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            result = await threads.create(load_type, name=name)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 4)

    async def test_create_exception(self):
        """
        Test exception handling of create
        """
        load_type = "threads"
        with patch.object(Threads, 'get_list', side_effect=Exception("Create failed")):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            with self.assertRaises(Exception):
                await threads.create(load_type)

    async def test_get_state_details_success(self):
        """
        Test success of get_state_details
        """
        load_type = "code"
        thread_id = "thread123"
        mock_state = {
            thread_id: {"content": "test content", "history": ["msg1"]}
        }
        with patch.object(Threads, 'load_all_from_sqlite', return_value=mock_state):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            result = await threads.get_state_details(load_type, thread_id)
            self.assertEqual(result, "test content")

    async def test_get_state_details_exception(self):
        """
        Test exception handling of get_state_details
        """
        load_type = "code"
        thread_id = "thread123"
        with patch.object(Threads, 'load_all_from_sqlite', side_effect=Exception("State failed")):
            threads = Threads(
                codebase_type=self.codebase_type,
                milvus_db=self.milvus_db,
                sqlite_db=self.sqlite_db,
                models=self.models,
                codebase=self.codebase
            )
            with self.assertRaises(Exception):
                await threads.get_state_details(load_type, thread_id)
