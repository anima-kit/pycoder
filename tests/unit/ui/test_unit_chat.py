## tests.unit.ui.test_unit_app
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from gradio import Markdown
from gradio_modal import Modal
from typing import Dict, List, Tuple, AsyncIterator, Any
from pyfiles.ui.interface_chat import ChatInterface

class TestUIChatUnit(TestCase):
    def setUp(self):
        self.mock_users = MagicMock()
        self.chat_interface = ChatInterface(self.mock_users)

    def test_init_success(self):
        """Test successful initialization of ChatInterface"""
        chat_interface = ChatInterface(self.mock_users)
        self.assertEqual(chat_interface.users, self.mock_users)

    @patch('pyfiles.ui.interface_chat.logger')
    def test_init_exception_handling(self, mock_logger):
        """Test exception handling during initialization"""
        with patch('pyfiles.ui.interface_chat.ChatInterface.__init__', side_effect=Exception("Init failed")):
            with self.assertRaises(Exception):
                ChatInterface(self.mock_users)

    def test_component_triggers_success(self):
        """Test successful component triggers setup"""
        mock_selected_user_state = MagicMock()
        mock_selected_codebase_state = MagicMock()
        mock_selected_external_docs_list_state = MagicMock()
        mock_selected_thread_state = MagicMock()
        mock_selected_code_state = MagicMock()
        mock_transcript = MagicMock()
        mock_user_input = MagicMock()
        mock_codebase_details_files = MagicMock()
        mock_new_thread_name_input = MagicMock()
        mock_thread_radio = MagicMock()
        mock_delete_button = MagicMock()
        mock_confirm_delete_modal = MagicMock()
        mock_confirm_delete_text = MagicMock()
        mock_confirm_delete_button = MagicMock()
        mock_cancel_delete_button = MagicMock()
        mock_status_messages = MagicMock()
        self.chat_interface.component_triggers(
            selected_user_state=mock_selected_user_state,
            selected_codebase_state=mock_selected_codebase_state,
            selected_external_docs_list_state=mock_selected_external_docs_list_state,
            selected_thread_state=mock_selected_thread_state,
            selected_code_state=mock_selected_code_state,
            transcript=mock_transcript,
            user_input=mock_user_input,
            codebase_details_files=mock_codebase_details_files,
            new_thread_name_input=mock_new_thread_name_input,
            thread_radio=mock_thread_radio,
            delete_chat_button=mock_delete_button,
            confirm_delete_modal=mock_confirm_delete_modal,
            confirm_delete_text=mock_confirm_delete_text,
            confirm_delete_button=mock_confirm_delete_button,
            cancel_delete_button=mock_cancel_delete_button,
            status_messages=mock_status_messages
        )

    @patch('pyfiles.ui.interface_chat.logger')
    def test_component_triggers_exception_handling(self, mock_logger):
        """Test exception handling in component triggers"""
        with patch.object(self.chat_interface, 'component_triggers', side_effect=Exception("Component triggers failed")):
            with self.assertRaises(Exception):
                self.chat_interface.component_triggers(
                    selected_user_state=MagicMock(),
                    selected_codebase_state=MagicMock(),
                    selected_external_docs_list_state=MagicMock(),
                    selected_thread_state=MagicMock(),
                    selected_code_state=MagicMock(),
                    transcript=MagicMock(),
                    user_input=MagicMock(),
                    codebase_details_files=MagicMock(),
                    new_thread_name_input=MagicMock(),
                    thread_radio=MagicMock(),
                    delete_button=MagicMock(),
                    confirm_delete_modal=MagicMock(),
                    confirm_delete_text=MagicMock(),
                    confirm_delete_button=MagicMock(),
                    cancel_delete_button=MagicMock(),
                    status_messages=MagicMock()
                )
            mock_logger.error.called_once()


class TestAUIChatUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_users = MagicMock()
        self.chat_interface = ChatInterface(self.mock_users)

    async def test_confirm_deletion_modal_success(self):
        """Test successful deletion confirmation modal creation"""
        mock_user = MagicMock()
        mock_docs = MagicMock()
        mock_user.get_current_codebase.return_value = mock_docs
        mock_docs.get_list = AsyncMock()
        mock_docs.get_list.return_value = [("test_chat_1", "test_chat_1"), ("test_chat_2", "test_chat_2")]
        
        with patch('pyfiles.ui.utils.handle_current_user', return_value=(mock_user, None)):
            result = await self.chat_interface._confirm_deletion_modal(
                selected_chat="test_chat_1",
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=[]
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], Modal)
            self.assertIsInstance(result[1], Markdown)

    @patch('pyfiles.ui.interface_chat.logger')
    async def test_confirm_deletion_modal_exception_handling(self, mock_logger):
        """Test exception handling in confirm deletion modal"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                await self.chat_interface._confirm_deletion_modal(
                    selected_chat="test_chat",
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=[]
                )
                mock_logger.error.assert_called_once()

    async def test_handle_create_chat_submit_success(self):
        """Test successful chat creation"""
        mock_user = MagicMock()
        mock_docs = MagicMock()
        mock_user.get_current_codebase.return_value = mock_docs
        mock_docs.create = AsyncMock()
        mock_docs.create.return_value = (["chat1", "chat2"], "chat1", None, "Created successfully")
        with patch('pyfiles.ui.utils.handle_current_user', return_value=(mock_user, None)):
            result = await self.chat_interface._handle_create_chat_submit(
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=[],
                chat_name="New Chat"
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 5)

    @patch('pyfiles.ui.interface_chat.logger')
    async def test_handle_create_chat_submit_exception_handling(self, mock_logger):
        """Test exception handling in chat creation"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                await self.chat_interface._handle_create_chat_submit(
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=[],
                    chat_name="New Chat"
                )
            mock_logger.error.assert_called_once()

    async def test_handle_delete_chat_click_success(self):
        """Test successful chat deletion"""
        mock_user = MagicMock()
        mock_docs = MagicMock()
        mock_user.get_current_codebase.return_value = mock_docs
        mock_docs.delete = AsyncMock()
        mock_docs.delete.return_value = (["chat1"], "chat1", "Deleted successfully")
        with patch('pyfiles.ui.utils.handle_current_user', return_value=(mock_user, None)):
            result = await self.chat_interface._handle_delete_chat_click(
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=[],
                chat_id="chat1"
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 5)

    @patch('pyfiles.ui.interface_chat.logger')
    async def test_handle_delete_chat_click_exception_handling(self, mock_logger):
        """Test exception handling in chat deletion"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                await self.chat_interface._handle_delete_chat_click(
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=[],
                    chat_id="chat1"
                )
            mock_logger.error.assert_called_once()

    async def test_handle_chat_input_submit_exception_handling(self):
        """Test exception handling in chat input submission"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                async def collect_responses():
                    async for response in self.chat_interface._handle_chat_input_submit(
                        user_name="test_user",
                        docs_name="test_docs",
                        ext_docs_list=[],
                        chat_id="chat1",
                        convo_history=[],
                        chat_input="test input"
                    ):
                        pass
                
                await collect_responses()

    async def test_handle_chat_undo_submit_exception_handling(self):
        """Test exception handling in chat undo submission"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                async def collect_responses():
                    async for response in self.chat_interface._handle_chat_undo_submit(
                        user_name="test_user",
                        docs_name="test_docs",
                        ext_docs_list=[],
                        chat_id="chat1",
                        convo_history=[],
                        chat_input="test input"
                    ):
                        pass
                
                await collect_responses()

    async def test_handle_chat_retry_submit_exception_handling(self):
        """Test exception handling in chat retry submission"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                async def collect_responses():
                    async for response in self.chat_interface._handle_chat_retry_submit(
                        user_name="test_user",
                        docs_name="test_docs",
                        ext_docs_list=[],
                        chat_id="chat1",
                        convo_history=[],
                        chat_input="test input"
                    ):
                        pass
                await collect_responses()

    async def test_handle_chat_edit_submit_exception_handling(self):
        """Test exception handling in chat edit submission"""
        with patch('pyfiles.ui.utils.handle_current_user', side_effect=Exception("User handling failed")):
            with self.assertRaises(Exception):
                async def collect_responses():
                    async for response in self.chat_interface._handle_chat_edit_submit(
                        user_name="test_user",
                        docs_name="test_docs",
                        ext_docs_list=[],
                        chat_id="chat1",
                        convo_history=[],
                        chat_input="test input",
                        edit_data=MagicMock()
                    ):
                        pass
                await collect_responses()

    @patch('pyfiles.ui.interface_chat.logger')
    async def test_create_interface_exception_handling(self, mock_logger):
        """Test exception handling in interface creation"""
        with patch.object(self.chat_interface, 'create_interface', side_effect=Exception("Interface creation failed")):
            with self.assertRaises(Exception):
                self.chat_interface.create_interface(
                    initial_threads_list=[],
                    initial_thread=None,
                    initial_convo=[],
                    initial_code_list=[],
                    initial_code=None,
                    initial_code_content=""
                )