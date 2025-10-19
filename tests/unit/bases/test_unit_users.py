
## tests.unit.bases.test_unit_users
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch, AsyncMock
from pyfiles.bases.users import Users

class TestUsersUnit(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_models = MagicMock()
        self.mock_client.client = MagicMock()
        self.mock_client.client.list_databases = MagicMock()
        self.users = Users(self.mock_models, self.mock_client)
        
    def test_init_success(self):
        """Test successful initialization of Users class"""
        self.assertEqual(self.users.client, self.mock_client)
        self.assertEqual(self.users.models, self.mock_models)
        self.assertEqual(self.users.user_dir, 'user_databases')
                
    def test_get_users_list_success(self):
        """Test successful retrieval of users list"""
        self.mock_client.client.list_databases.return_value = ['default', 'user1', 'user2']
        result = self.users.get_users_list()
        self.assertEqual(result, ['user1', 'user2'])
            
    def test_get_users_list_exception(self):
        """Test exception handling in get_users_list"""
        self.mock_client.client.list_databases.side_effect = Exception("Database error")
        with self.assertRaises(Exception):
            self.users.get_users_list()

class TestAUsersUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_models = MagicMock()
        self.mock_milvus_db = MagicMock()
        self.mock_sqlite_db = MagicMock()
        self.mock_codebases_instance = MagicMock()
        self.users = Users(self.mock_models, self.mock_client)
        self.users.get_users_list = MagicMock()
        self.users.get_current_user = AsyncMock()
        self.users.selected_user = MagicMock()
            
    async def test_create_new_user_success(self):
        """Test successful creation of new user"""
        self.users.get_users_list.return_value = ['user1']
        self.users.get_current_user.return_value = ("user_instance", "external_instance")
        result = await self.users.create_new_user("test_user", 'test_user')
        self.assertIsInstance(result, tuple)
            
    async def test_create_new_user_already_exists(self):
        """Test creation of user that already exists"""
        self.users.get_users_list.return_value = ['test_user']
        result = await self.users.create_new_user("test_user", 'test_user')
        self.assertIsInstance(result, tuple)
            
    async def test_create_new_user_exception(self):
        """Test exception handling in create_new_user"""
        self.users.get_users_list.side_effect = Exception("List error")
        with self.assertRaises(Exception):
            await self.users.create_new_user("test_user")
            
    async def test_delete_user_exception(self):
        """Test exception handling in delete_user"""
        self.users.selected_user.sqlite_db.get_codebase_list.side_effect = Exception("DB error")
        with self.assertRaises(Exception):
            await self.users.delete_user("test_user")
                
    async def test_get_current_user_exception(self):
        """Test exception handling in get_current_user"""
        users = Users(self.mock_models, self.mock_client)
        users._get_selected_codebases = AsyncMock(side_effect=Exception("Codebase error"))
        with self.assertRaises(Exception):
            await users.get_current_user("test_user")
                
    async def test_get_selected_codebases_exception(self):
        """Test exception handling in _get_selected_codebases"""
        self.mock_codebases_instance.initialize_default_codebase = AsyncMock(return_value=None)
        with patch('pyfiles.bases.codebases.Codebases', return_value=self.mock_codebases_instance):
            with self.assertRaises(Exception):
                await self.users._get_selected_codebases(self.mock_milvus_db, self.mock_sqlite_db)
                    
    async def test_get_selected_ext_codebases_exception(self):
        """Test exception handling in _get_selected_ext_codebases"""
        with patch('pyfiles.bases.logger') as mock_logger:
            self.mock_codebases_instance.initialize_default_codebase = AsyncMock(side_effect=Exception("Init error"))
            with patch('pyfiles.bases.codebases.Codebases', return_value=self.mock_codebases_instance):
                with self.assertRaises(Exception):
                    await self.users._get_selected_ext_codebases(self.mock_milvus_db, self.mock_sqlite_db)
                    
    async def test_get_user_state_details_exception(self):
        """Test exception handling in get_user_state_details"""
        self.users.get_current_user = AsyncMock(side_effect=Exception("Current user error"))
        with self.assertRaises(Exception):
            await self.users.get_user_state_details("test_user", "test_codebase")
                
    async def test_fix_name_edge_cases(self):
        """Test edge cases in _fix_name method"""
        result = self.users._fix_name("")
        self.assertEqual(result, "unnamed")
        result = self.users._fix_name("test_")
        self.assertEqual(result, "test")