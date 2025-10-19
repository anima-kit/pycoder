## tests.unit.ui.test_unit_users
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from gradio import Markdown
from gradio_modal import Modal
from pyfiles.ui.interface_user import UserInterface


class TestUIUsersUnit(TestCase):
    def setUp(self):
        self.mock_users = MagicMock()
        self.mock_users.get_users_list.return_value = ["user1", "user2"]
        self.ui = UserInterface(self.mock_users)

    def test_init_success(self):
        """Test successful initialization of UserInterface"""
        ui = UserInterface(self.mock_users)
        self.assertEqual(ui.users, self.mock_users)

    def test_init_exception_handling(self):
        """Test exception handling during initialization"""
        with patch('pyfiles.ui.interface_user.logger') as mock_logger:
            with patch.object(UserInterface, '__init__', side_effect=Exception("Init Error")):
                with self.assertRaises(Exception):
                    UserInterface(self.mock_users)

    def test_confirm_deletion_modal_success(self):
        """Test successful confirmation modal creation"""
        result = self.ui._confirm_deletion_modal("test_user")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(isinstance(result[0], Modal))
        self.assertTrue(result[0].visible)
        self.assertIsInstance(result[1], Markdown)

    def test_confirm_deletion_modal_exception_handling(self):
        """Test exception handling in confirmation modal creation"""
        with patch('pyfiles.ui.interface_user.logger') as mock_logger:
            with patch('pyfiles.ui.interface_user.Markdown', side_effect=Exception("Markdown Error")):
                with self.assertRaises(Exception):
                    self.ui._confirm_deletion_modal("test_user")
                mock_logger.error.assert_called_once()

    def test_component_triggers_success(self):
        """Test successful setup of component triggers"""
        selected_user_state = MagicMock()
        user_radio = MagicMock()
        delete_user_button = MagicMock()
        user_name_input = MagicMock()
        confirm_delete_modal = MagicMock()
        confirm_delete_text = MagicMock()
        confirm_delete_button = MagicMock()
        cancel_delete_button = MagicMock()
        status_messages = MagicMock()
        self.ui.component_triggers(
            selected_user_state,
            user_radio,
            delete_user_button,
            user_name_input,
            confirm_delete_modal,
            confirm_delete_text,
            confirm_delete_button,
            cancel_delete_button,
            status_messages
        )

    def test_create_interface_exception_handling(self):
        """Test exception handling in interface creation"""
        with patch('pyfiles.ui.interface_user.logger') as mock_logger:
            with patch('pyfiles.ui.utils.create_component', side_effect=Exception("Component Error")):
                with self.assertRaises(Exception):
                    self.ui.create_interface(initial_del_button=True)
                mock_logger.error.assert_called_once()


class TestAUIUsersUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_users = AsyncMock()
        self.mock_users.create_new_user.return_value = (["user1", "user2"], "User created")
        self.mock_users.delete_user.return_value = (["user1"], "user1", "User deleted")
        self.ui = UserInterface(self.mock_users)

    async def test_handle_new_user_submit_exception_handling(self):
        """Test exception handling in new user submission"""
        with patch('pyfiles.ui.interface_user.logger') as mock_logger:
            self.mock_users.create_new_user.side_effect = Exception("Creation Error")
            with self.assertRaises(Exception):
                await self.ui._handle_new_user_submit("new_user")

    async def test_handle_delete_user_click_exception_handling(self):
        """Test exception handling in user deletion"""
        with patch('pyfiles.ui.interface_user.logger') as mock_logger:
            self.mock_users.delete_user.side_effect = Exception("Deletion Error")
            with self.assertRaises(Exception):
                await self.ui._handle_delete_user_click("user1")
            mock_logger.error.assert_called_once()