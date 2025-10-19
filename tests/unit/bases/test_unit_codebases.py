## tests.unit.bases.test_unit_codebases
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch, AsyncMock
from langchain.schema import Document
from pyfiles.bases.codebases import Codebases

class TestCodebasesUnit(TestCase):
    def setUp(self):
        self.mock_milvus_db = MagicMock()
        self.mock_sqlite_db = MagicMock()
        self.mock_models = MagicMock()
        self.codebase = Codebases(
            milvus_db=self.mock_milvus_db,
            sqlite_db=self.mock_sqlite_db,
            models=self.mock_models,
            selected_codebase_name="test_codebase"
        )
        
    def test_init_success(self):
        """Test successful initialization of Codebases"""
        self.assertEqual(self.codebase.milvus_db, self.mock_milvus_db)
        self.assertEqual(self.codebase.sqlite_db, self.mock_sqlite_db)
        self.assertEqual(self.codebase.models, self.mock_models)
        self.assertEqual(self.codebase.codebase_type, "user")
        self.assertEqual(self.codebase.selected_codebase_name, "test_codebase")
        
    def test_init_with_none_selected_codebase(self):
        """Test initialization with None selected codebase name"""
        codebase = Codebases(
            milvus_db=self.mock_milvus_db,
            sqlite_db=self.mock_sqlite_db,
            models=self.mock_models,
            codebase_type="external",
            selected_codebase_name=None
        )
        self.assertEqual(codebase.milvus_db, self.mock_milvus_db)
        self.assertEqual(codebase.codebase_type, "external")
        self.assertIsNone(codebase.selected_codebase_name)
        
    @patch('pyfiles.bases.codebases.Docs')
    def test_create_docs_handler_success(self, mock_docs_class):
        """Test successful creation of DB component"""
        config = {
            "codebase_type": "user",
            "db": self.mock_milvus_db,
            "group": 'group',
            "content_list": ["test content"]
        }
        mock_docs_instance = MagicMock()
        mock_docs_class.return_value = mock_docs_instance
        result = self.codebase._create_docs_handler(config)
        self.assertEqual(result, mock_docs_instance)
        mock_docs_class.assert_called_once_with(
            codebase_type="user",
            db=self.mock_milvus_db,
            group='group',
            content_list=["test content"]
        )
            
    def test_fix_name_success(self):
        """Test successful name fixing"""
        result = self.codebase._fix_name("test name")
        self.assertEqual(result, "test_name")
        result = self.codebase._fix_name("test-name_with.special!chars")
        self.assertEqual(result, "test_name_with_special_chars")
        result = self.codebase._fix_name("123test")
        self.assertEqual(result, "_123test")
        result = self.codebase._fix_name("test_")
        self.assertEqual(result, "test")
        result = self.codebase._fix_name("")
        self.assertEqual(result, "unnamed")
                
    @patch('pyfiles.bases.codebases.Codebases._fix_name')
    def test_init_exception_handling(self, mock_fix_name):
        """Test exception handling in __init__"""
        mock_fix_name.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            codebase = Codebases(
                milvus_db=None,
                sqlite_db=None,
                models=None,
                codebase_type="user",
                selected_codebase_name="test"
            )
                
    @patch('pyfiles.docs.docs_handler.Docs')
    def test_create_docs_handler_exception_handling(self, mock_docs_class):
        """Test exception handling in _create_docs_handler"""
        mock_docs_class.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            self.codebase._create_docs_handler({"docs_type": "milvus"})
                
    def test_fix_name_exception_handling(self):
        """Test exception handling in _fix_name"""
        with self.assertRaises(Exception):
            result = self.codebase._fix_name(None)
                
    def test_get_current_agent_exception_handling(self):
        """Test exception handling in get_current_agent"""
        self.codebase.get_current_codebase = MagicMock()
        self.codebase.get_current_codebase.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            self.codebase.get_current_agent("test_codebase")

class TestACodebasesUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_milvus_db = MagicMock()
        self.mock_sqlite_db = MagicMock()
        self.mock_models = MagicMock()
        self.codebase = Codebases(
            milvus_db=self.mock_milvus_db,
            sqlite_db=self.mock_sqlite_db,
            models=self.mock_models,
            selected_codebase_name="test_codebase"
        )
        self.codebase.get_current_codebase = MagicMock()
        self.codebase._create_docs_handler = MagicMock()
        self.codebase.sqlite_db = MagicMock()

    async def test_save_default_docs_success(self):
        """Test success of _save_default_docs"""
        mock_docs = MagicMock()
        mock_docs.acreate_docs = AsyncMock(
            return_value=[
                Document(page_content='doc1', metadata={}), 
                Document(page_content='doc2', metadata={})
            ]
        )
        mock_docs.aadd_to_vectorstore = AsyncMock()
        mock_docs.aadd_to_sqlite = AsyncMock(return_value=["thread1", "thread2"])
        with patch.object(self.codebase, '_create_docs_handler', return_value=mock_docs):
            codebase_config = [
                {"docs_type": "milvus", "content_list": ["content1"], "db": "milvus"},
                {"docs_type": "sqlite", "content_list": ["content2"], "db": "sqlite"}
            ]
            result = await self.codebase._save_default_docs(codebase_config)
            assert result == ["thread1", "thread2"]
            mock_docs.aadd_to_vectorstore.assert_awaited_once()
            mock_docs.aadd_to_sqlite.assert_awaited_once()
                
    async def test_save_default_docs_exception_handling(self):
        """Test exception handling in _save_default_docs"""
        config = {
            "codebase_type": "user",
            "db": self.mock_milvus_db,
            "group": 'group',
            "content_list": ["test content"]
        }
        self.codebase._create_docs_handler.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.codebase._save_default_docs([config])

    async def test_create_codebase_docs_success_no_existing_threads(self):
        """Test successful creation of codebase docs when no threads exist"""
        mock_threads = AsyncMock()
        mock_threads.get_list = AsyncMock(return_value=[])
        with patch.object(self.codebase, 'get_current_codebase', return_value=mock_threads):
            mock_save_docs = AsyncMock(return_value=["thread1", "thread2", "thread3"])
            self.codebase._save_default_docs = mock_save_docs
            result = await self.codebase._create_codebase_docs("test_codebase")
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == mock_threads
            assert result[1] == ["thread1", "thread2", "thread3"]
            mock_save_docs.assert_called_once()
            call_args = mock_save_docs.call_args[0][0]
            assert len(call_args) == 3
            assert call_args[0]["content_list"] == ["# test_codebase"]
            assert call_args[1]["content_list"] == ["# test_codebase"]
            assert call_args[2]["content_list"] == ['[]']

    async def test_create_codebase_docs_success_with_existing_threads(self):
        """Test successful creation of codebase docs when threads already exist"""
        mock_threads = AsyncMock()
        mock_threads.get_list = AsyncMock(return_value=[("thread1", "id1"), ("thread2", "id2")])
        with patch.object(self.codebase, 'get_current_codebase', return_value=mock_threads):
            result = await self.codebase._create_codebase_docs("test_codebase")
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == mock_threads
            assert result[1] == ["id1", "id2", "id1", "id2"]

    async def test_create_codebase_docs_external_codebase_type(self):
        """Test successful creation of codebase docs for external codebase type"""
        mock_threads = AsyncMock()
        mock_threads.get_list = AsyncMock(return_value=[])
        codebases = Codebases(
            milvus_db=self.mock_milvus_db,
            sqlite_db=self.mock_sqlite_db,
            models=self.mock_models,
            codebase_type="external"
        )
        with patch.object(codebases, 'get_current_codebase', return_value=mock_threads):
            mock_save_docs = AsyncMock(return_value=["thread1", "thread2"])
            codebases._save_default_docs = mock_save_docs
            result = await codebases._create_codebase_docs("test_codebase")
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == mock_threads
            assert result[1] == ["thread1", "thread2"]
            mock_save_docs.assert_called_once()
            call_args = mock_save_docs.call_args[0][0]
            assert len(call_args) == 2
                    
    async def test_create_codebase_docs_exception_handling(self):
        """Test exception handling in _create_codebase_docs"""
        self.codebase.get_current_codebase.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.codebase._create_codebase_docs("test_codebase")

    async def test_initialize_default_codebase_empty_user_codebases(self):
        """Test initialize_default_codebase when no user codebases exist"""
        mock_threads = MagicMock()
        self.codebase.sqlite_db.get_codebase_list = AsyncMock()
        with patch.object(self.codebase, '_create_codebase_docs', return_value=(mock_threads, None)):
            self.codebase.sqlite_db.get_codebase_list.return_value = []
            result = await self.codebase.initialize_default_codebase()
            assert result == mock_threads
            self.codebase.sqlite_db.get_codebase_list.assert_called_once_with(codebase_type="user")
            self.codebase._create_codebase_docs.assert_called_once_with("default_codebase")

    async def test_initialize_default_codebase_empty_external_codebases(self):
        """Test initialize_default_codebase when no external codebases exist"""
        mock_milvus_db = MagicMock()
        mock_sqlite_db = AsyncMock()
        mock_models = MagicMock()
        mock_sqlite_db.get_codebase_list.return_value = []
        codebases = Codebases(
            milvus_db=mock_milvus_db,
            sqlite_db=mock_sqlite_db,
            models=mock_models,
            codebase_type="external"
        )
        result = await codebases.initialize_default_codebase()
        assert result is None
        mock_sqlite_db.get_codebase_list.assert_called_once_with(codebase_type="external")

    async def test_initialize_default_codebase_existing_codebases_no_selection(self):
        """Test initialize_default_codebase when codebases exist but none selected"""
        mock_milvus_db = MagicMock()
        mock_sqlite_db = AsyncMock()
        mock_models = MagicMock()
        mock_sqlite_db.get_codebase_list.return_value = ["codebase1", "codebase2"]
        codebases = Codebases(
            milvus_db=mock_milvus_db,
            sqlite_db=mock_sqlite_db,
            models=mock_models,
            codebase_type="user"
        )
        mock_threads = MagicMock()
        codebases.get_current_codebase = MagicMock(return_value=mock_threads)
        result = await codebases.initialize_default_codebase()
        assert result == mock_threads
        codebases.get_current_codebase.assert_called_once_with("codebase1")

    async def test_initialize_default_codebase_existing_codebases_with_selection(self):
        """Test initialize_default_codebase when codebases exist and one is selected"""
        mock_threads = AsyncMock()
        mock_threads.get_list = AsyncMock(return_value=[("thread1", "id1"), ("thread2", "id2")])
        self.codebase.sqlite_db.get_codebase_list = AsyncMock()
        with patch.object(self.codebase, 'get_current_codebase', return_value=mock_threads):
            self.codebase.sqlite_db.get_codebase_list.return_value = ["codebase1", "codebase2"]
            result = await self.codebase.initialize_default_codebase()
            assert result == mock_threads
            self.codebase.sqlite_db.get_codebase_list.assert_called_once_with(codebase_type="user")
            self.codebase.get_current_codebase.assert_called_once()
                
    async def test_initialize_default_codebase_exception_handling(self):
        """Test exception handling in initialize_default_codebase"""
        self.codebase.sqlite_db.get_codebase_list.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.codebase.initialize_default_codebase()

    async def test_create_new_codebase_success(self):
        mock_threads = MagicMock()
        with patch.object(self.codebase, '_fix_name', return_value="test_codebase"):
            with patch.object(self.codebase, '_create_codebase_docs', return_value=(mock_threads, ["thread1", "thread2"])):
                self.codebase.sqlite_db.get_codebase_list = AsyncMock(return_value=[])
                with patch.object(self.codebase, 'get_current_agent', return_value="agent1"):
                    result = await self.codebase.create_new_codebase("test_codebase")
                    assert result[0] == "user"
                    assert result[2] == "test_codebase"
                    assert result[3] == ["thread1", "thread2"]
                    assert "Successfully created codebase" in result[4]
                    self.codebase.milvus_db.create_collection.assert_called_once_with("test_codebase")
                    self.codebase.get_current_agent.assert_called_once_with(codebase_name="test_codebase")

    async def test_create_new_codebase_already_exists(self):
        mock_threads = MagicMock()
        with patch.object(self.codebase, '_fix_name', return_value="test_codebase"):
            self.codebase.sqlite_db.get_codebase_list = AsyncMock(return_value=["test_codebase"])
            with patch.object(self.codebase, '_create_codebase_docs', return_value=(mock_threads, ["thread1", "thread2"])):
                result = await self.codebase.create_new_codebase("test_codebase")
                assert result[0] == "user" 
                assert result[2] == "test_codebase"
                assert result[3] == ["thread1", "thread2"]
                assert "already exists" in result[4]
                self.codebase.milvus_db.create_collection.assert_not_called()
                    
    async def test_create_new_codebase_exception_handling(self):
        """Test exception handling in create_new_codebase"""
        self.codebase.sqlite_db.get_codebase_list.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.codebase.create_new_codebase("test")
                        
    async def test_delete_codebase_exception_handling(self):
        """Test exception handling in delete_codebase"""
        self.codebase.get_current_codebase.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.codebase.delete_codebase("test_codebase")
                
    async def test_get_codebase_state_details_success(self):
        """Test successful get_codebase_state_details execution"""
        mock_threads = MagicMock()
        self.codebase.get_current_codebase.return_value = mock_threads
        result = await self.codebase.get_codebase_state_details("test_codebase")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
            
    async def test_get_codebase_state_details_exception_handling(self):
        """Test exception handling in get_codebase_state_details"""
        self.codebase.get_current_codebase.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await self.codebase.get_codebase_state_details("test_codebase")

    async def test_get_current_codebase_none_name(self):
        """Test get_current_codebase with None name"""
        codebase = Codebases(
            milvus_db=self.mock_milvus_db,
            sqlite_db=self.mock_sqlite_db,
            models=self.mock_models
        )
        with self.assertRaises(ValueError):
            codebase.get_current_codebase(None)

    async def test_get_current_agent_no_selected_codebase(self):
        """Test get_current_agent when selected_codebase is None"""
        codebase = Codebases(
            milvus_db=self.mock_milvus_db,
            sqlite_db=self.mock_sqlite_db,
            models=self.mock_models
        )
        with self.assertRaises(ValueError):
            codebase.get_current_agent("test_codebase")