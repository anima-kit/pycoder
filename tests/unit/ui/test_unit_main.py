## tests.unit.ui.test_unit_main
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from gradio import Radio, CheckboxGroup, Markdown, Textbox, Tab
from pyfiles.ui.interface_main import MainInterface

class TestUIMainUnit(TestCase):
    def setUp(self):
        self.mock_users = MagicMock()
        self.main_interface = MainInterface(self.mock_users)
    
    def test_init_success(self):
        """Test successful initialization"""
        mock_users = MagicMock()
        interface = MainInterface(mock_users)
        self.assertEqual(interface.users, mock_users)
    
    def test_init_exception_handling(self):
        """Test exception handling in initialization"""
        mock_users = MagicMock()
        mock_users.side_effect = Exception("Initialization failed")
        with patch('pyfiles.ui.interface_main.logger') as mock_logger:
            interface = MainInterface(mock_users)

class TestAUIMainUnit(IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_users = MagicMock()
        self.main_interface = MainInterface(self.mock_users)

    async def test_handle_user_change_success(self):
        mock_users = AsyncMock()
        mock_users.get_user_state_details.return_value = (
            "test_user",
            "test_codebase",
            ["choice1", "choice2"],
            ["ext_choice1", "ext_choice2"],
            "ext_choice1"
        )
        mock_utils = MagicMock()
        mock_utils.toggle_del_button.return_value = MagicMock()
        main_interface = MainInterface(users=mock_users)
        with patch('pyfiles.ui.interface_main.utils', mock_utils):
            result = await main_interface._handle_user_change(
                user_name="test_user",
                docs_name="test_codebase"
            )
            assert len(result) == 8
            assert result[0] == "test_user"
            assert result[1] == "test_codebase"
            assert result[2] == "test_codebase"
            assert isinstance(result[3], Radio)
            assert isinstance(result[5], Radio)
            assert isinstance(result[7], CheckboxGroup)
            mock_users.get_user_state_details.assert_called_once_with("test_user", "test_codebase")
    
    async def test_handle_user_change_exception_handling(self):
        """Test exception handling in user change handler"""
        user_name = "test_user"
        docs_name = "test_docs"
        with patch('pyfiles.ui.interface_main.logger') as mock_logger:
            self.mock_users.get_user_state_details.side_effect = Exception("User change failed")
            with self.assertRaises(Exception):  
                result = await self.main_interface._handle_user_change(user_name, docs_name)
            mock_logger.error.assert_called_once()
    
    async def test_handle_docs_change_exception_handling(self):
        """Test exception handling in docs change handler"""
        user_name = "test_user"
        docs_name = "test_docs"
        ext_docs_list = ["ext1", "ext2"]    
        with patch('pyfiles.ui.interface_main.logger') as mock_logger:
            self.mock_users.handle_current_user = AsyncMock(side_effect=Exception("Docs change failed"))
            with self.assertRaises(Exception):  
                result = await self.main_interface._handle_docs_change(user_name, docs_name, ext_docs_list)
            mock_logger.error.assert_called_once()
    
    async def test_handle_chats_change_exception_handling(self):
        """Test exception handling in chats change handler"""
        user_name = "test_user"
        docs_name = "test_docs"
        ext_docs_list = ["ext1", "ext2"]
        chat_id = "chat_id"
        with patch('pyfiles.ui.interface_main.utils.handle_current_user', side_effect=Exception("Switch failed")):
            with patch('pyfiles.ui.interface_main.logger') as mock_logger:
                with self.assertRaises(Exception):
                    await self.main_interface._handle_chats_change(user_name, docs_name, ext_docs_list, chat_id)
    
    async def test_handle_doc_change_exception_handling(self):
        """Test exception handling in doc change handler"""
        user_name = "test_user"
        docs_name = "test_docs"
        ext_docs_list = ["ext1", "ext2"]
        doc_id = "doc_id"
        with patch('pyfiles.ui.interface_main.utils.handle_current_user', side_effect=Exception("Switch failed")):
            with patch('pyfiles.ui.interface_main.logger') as mock_logger:
                with self.assertRaises(Exception):
                    await self.main_interface._handle_doc_change(user_name, docs_name, ext_docs_list, doc_id)
                mock_logger.error.assert_called_once()
    
    async def test_handle_ext_docs_change_exception_handling(self):
        """Test exception handling in external docs change handler"""
        user_name = "test_user"
        docs_name = "test_docs"
        ext_docs_list = ["ext1", "ext2"]
        ext_docs_name = "ext_docs_name"
        with patch('pyfiles.ui.interface_main.utils.handle_current_user', side_effect=Exception("Switch failed")):
            with patch('pyfiles.ui.interface_main.logger') as mock_logger:
                with self.assertRaises(Exception):
                    await self.main_interface._handle_ext_docs_change(user_name, docs_name, ext_docs_list, ext_docs_name)
                mock_logger.error.assert_called_once()
    
    async def test_handle_ext_doc_change_exception_handling(self):
        """Test exception handling in external doc change handler"""
        user_name = "test_user"
        docs_name = "test_docs"
        ext_docs_list = ["ext1", "ext2"]
        ext_docs_name = "ext_docs_name"
        doc_id = "doc_id"       
        with patch('pyfiles.ui.interface_main.utils.handle_current_user', side_effect=Exception("Switch failed")):
            with patch('pyfiles.ui.interface_main.logger') as mock_logger:
                with self.assertRaises(Exception):
                    await self.main_interface._handle_ext_doc_change(user_name, docs_name, ext_docs_list, ext_docs_name, doc_id)
                mock_logger.error.assert_called_once()

    @patch('pyfiles.ui.utils.create_component')
    @patch('pyfiles.ui.interface_main.Row')
    @patch('pyfiles.ui.interface_main.Column')
    @patch('pyfiles.ui.interface_main.HTML')
    def test_create_interface_success(self, mock_html, mock_column, mock_row, mock_create_component):
        mock_row_instance = MagicMock()
        mock_column_instance = MagicMock()
        mock_html_instance = MagicMock()
        mock_row.return_value.__enter__.return_value = mock_row_instance
        mock_column.return_value.__enter__.return_value = mock_column_instance
        mock_html.return_value = mock_html_instance
        mock_create_component.side_effect = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        users = MagicMock()
        main_interface = MainInterface(users)
        result = main_interface.create_interface("test_user", "test_docs")
        self.assertIsInstance(result, dict)
        self.assertIn('main_row', result)
        self.assertIn('status_bar', result)
        self.assertIn('selected_user', result)
        self.assertIn('selected_docs', result)
        self.assertIn('users_btn', result)
        self.assertIn('docs_btn', result)
        self.assertIn('chats_btn', result)
        self.assertIn('ext_docs_btn', result)
        expected_configs = [
            {"component_type": Markdown, "value": "Welcome!", "container": True},
            {"component_type": Textbox, "value": "test_user", "interactive": False, "label": "Selected User", "scale": 2},
            {"component_type": Textbox, "value": "test_docs", "interactive": False, "label": "Selected Docs", "scale": 2},
            {"component_type": Tab, "label": 'Users'},
            {"component_type": Tab, "label": 'Docs'},
            {"component_type": Tab, "label": 'Chats'},
            {"component_type": Tab, "label": 'External Docs'}
        ]
        self.assertEqual(mock_create_component.call_count, 7)
        for i, call in enumerate(mock_create_component.call_args_list):
            self.assertEqual(call[0][0], expected_configs[i])
    
    async def test_create_interface_exception_handling(self):
        """Test exception handling in interface creation"""
        initial_user_name = "test_user"
        initial_docs_name = "test_docs"
        with patch('pyfiles.ui.interface_main.logger') as mock_logger:
            with patch('pyfiles.ui.interface_main.Row', side_effect=Exception("Create failed")):
                with self.assertRaises(Exception):    
                    result = self.main_interface.create_interface(initial_user_name, initial_docs_name)
            mock_logger.error.assert_called_once()
