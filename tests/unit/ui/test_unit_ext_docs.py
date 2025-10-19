## tests.unit.ui.test_unit_ext_docs
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from gradio import Markdown, Radio, CheckboxGroup
from gradio_modal import Modal
from pyfiles.ui.interface_ext_docs import ExtDocsInterface

class TestUIExtDocsUnit(TestCase):
    def setUp(self):
        self.mock_users = MagicMock()
        self.ext_docs_interface = ExtDocsInterface(self.mock_users)

    def test_init_success(self):
        """Test successful initialization"""
        interface = ExtDocsInterface(self.mock_users)
        self.assertEqual(interface.users, self.mock_users)

    def test_confirm_deletion_modal_success(self):
        """Test successful deletion modal creation"""
        selected_codebase = "test_codebase"
        result = self.ext_docs_interface._confirm_deletion_modal(selected_codebase)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Modal)
        self.assertTrue(result[0].visible)
        self.assertIsInstance(result[1], Markdown)

    def test_component_triggers_success(self):
        """Test successful component trigger setup"""
        mock_user_state = MagicMock()
        mock_codebase_state = MagicMock()
        mock_docs_name_input = MagicMock()
        mock_docs_list_state = MagicMock()
        mock_codebase_radio = MagicMock()
        mock_checkbox = MagicMock()
        mock_upload = MagicMock()
        mock_delete_button = MagicMock()
        mock_files_radio = MagicMock()
        mock_file_state = MagicMock()
        mock_delete_code_button = MagicMock()
        mock_modal = MagicMock()
        mock_text = MagicMock()
        mock_confirm_btn = MagicMock()
        mock_cancel_btn = MagicMock()
        mock_code_modal = MagicMock()
        mock_code_text = MagicMock()
        mock_code_confirm_btn = MagicMock()
        mock_code_cancel_btn = MagicMock()
        mock_status = MagicMock()
        try:
            self.ext_docs_interface.component_triggers(
                selected_user_state=mock_user_state,
                selected_codebase_state=mock_codebase_state,
                external_docs_name_input=mock_docs_name_input,
                selected_external_docs_list_state=mock_docs_list_state,
                selected_external_codebase_state=mock_codebase_radio,
                external_codebases_checkbox=mock_checkbox,
                external_codebases_radio=mock_codebase_radio,
                external_docs_upload=mock_upload,
                delete_external_docs_button=mock_delete_button,
                external_codebases_files_radio=mock_files_radio,
                selected_external_docs_file_state=mock_file_state,
                delete_external_code_button=mock_delete_code_button,
                confirm_delete_modal=mock_modal,
                confirm_delete_text=mock_text,
                confirm_delete_button=mock_confirm_btn,
                cancel_delete_button=mock_cancel_btn,
                confirm_code_delete_modal=mock_code_modal,
                confirm_code_delete_text=mock_code_text,
                confirm_code_delete_button=mock_code_confirm_btn,
                cancel_code_delete_button=mock_code_cancel_btn,
                status_messages=mock_status
            )
        except Exception as e:
            self.fail(f"component_triggers should not raise exception: {e}")

    def test_create_interface_exception_handling(self):
        """Test exception handling in interface creation"""
        with patch('pyfiles.bases.logger.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logger error")
            with self.assertRaises(Exception):
                self.ext_docs_interface.create_interface(
                    initial_external_docs_list_all=["doc1", "doc2"],
                    initial_external_codebase="doc1",
                    initial_external_code_list=["file1.py", "file2.py"],
                    initial_external_docs_file="file1.py",
                    initial_external_docs_file_content="# Content",
                    initial_external_codebase_del_button=True,
                    initial_external_codebase_files_del_button=True
                )


class TestAUIExtDocsUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_users = MagicMock()
        self.ext_docs_interface = ExtDocsInterface(self.mock_users)

    async def test_confirm_code_deletion_modal_success(self):
        """Test successful code deletion modal creation"""
        with patch('pyfiles.ui.utils.handle_current_user', new_callable=AsyncMock) as mock_handle:
            mock_ext_docs = MagicMock()
            mock_current_codebase = MagicMock()
            mock_docs = MagicMock()
            mock_ext_docs.get_current_codebase.return_value = mock_docs
            mock_handle.return_value = (None, mock_ext_docs)
            mock_docs.get_list = AsyncMock()
            mock_docs.get_list.return_value = [("file1.py", "file1"), ("file2.py", "file2")]
            result = await self.ext_docs_interface._confirm_code_deletion_modal(
                selected_code_state="file1",
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=["doc1", "doc2"],
                selected_ext_docs="test_doc"
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], Modal)
            self.assertTrue(result[0].visible)
            self.assertIsInstance(result[1], Markdown)

    async def test_confirm_code_deletion_modal_exception_handling(self):
        """Test exception handling in code deletion modal creation"""
        with patch('pyfiles.bases.logger.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logger error")
            with self.assertRaises(Exception):
                await self.ext_docs_interface._confirm_code_deletion_modal(
                    selected_code_state="test_file",
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=["doc1", "doc2"],
                    selected_ext_docs="test_doc"
                )

    async def test_handle_create_ext_docs_submit_success(self):
        """Test successful external docs creation"""
        with patch('pyfiles.ui.utils.handle_current_user', new_callable=AsyncMock) as mock_handle:
            mock_ext_docs = MagicMock()
            mock_ext_docs.create_new_codebase = AsyncMock()
            mock_ext_docs.create_new_codebase.return_value = (
                "user", 
                ["doc1", "doc2"], 
                "new_doc",
                ["thread1", "thread2"],
                "Success message"
            )
            mock_handle.return_value = (None, mock_ext_docs)
            result = await self.ext_docs_interface._handle_create_ext_docs_submit(
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=["doc1", "doc2"],
                ext_docs_name="new_doc"
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 7)
            self.assertEqual(result[0], "new_doc")
            self.assertIsInstance(result[2], Radio)

    async def test_handle_create_ext_docs_submit_exception_handling(self):
        """Test exception handling in external docs creation"""
        with patch('pyfiles.bases.logger.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logger error")
            with self.assertRaises(Exception):
                await self.ext_docs_interface._handle_create_ext_docs_submit(
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=["doc1", "doc2"],
                    ext_docs_name="new_doc"
                )

    async def test_handle_delete_ext_docs_click_success(self):
        """Test successful external docs deletion"""
        with patch('pyfiles.ui.utils.handle_current_user', new_callable=AsyncMock) as mock_handle:
            mock_ext_docs = MagicMock()
            mock_ext_docs.delete_codebase = AsyncMock()
            mock_ext_docs.delete_codebase.return_value = (
                "user",
                "deleted_doc",
                ["doc1", "doc2"],
                ["thread1", "thread2"],
                "Success message"
            )
            mock_handle.return_value = (None, mock_ext_docs)
            result = await self.ext_docs_interface._handle_delete_ext_docs_click(
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=["doc1", "doc2"],
                ext_docs_name="deleted_doc"
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 7)
            self.assertEqual(result[0], "deleted_doc")
            self.assertIsInstance(result[1], CheckboxGroup) 
            self.assertIsInstance(result[2], Radio)

    async def test_handle_delete_ext_docs_click_exception_handling(self):
        """Test exception handling in external docs deletion"""
        with patch('pyfiles.bases.logger.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logger error")
            with self.assertRaises(Exception):
                await self.ext_docs_interface._handle_delete_ext_docs_click(
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=["doc1", "doc2"],
                    ext_docs_name="deleted_doc"
                )

    async def test_handle_create_ext_doc_upload_success(self):
        """Test successful external doc upload"""
        with patch('pyfiles.ui.utils.handle_current_user', new_callable=AsyncMock) as mock_handle:
            mock_ext_docs = MagicMock()
            mock_docs = MagicMock()
            mock_docs.create = AsyncMock()
            mock_docs.create.return_value = (
                ["file1.py", "file2.py"],
                "thread1",
                None,
                "Success message"
            )
            mock_ext_docs.get_current_codebase.return_value = mock_docs
            mock_handle.return_value = (None, mock_ext_docs)
            result = await self.ext_docs_interface._handle_create_ext_doc_upload(
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=["doc1", "doc2"],
                ext_docs_name="test_doc",
                files=["file1.py", "file2.py"]
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 4)
            self.assertIsInstance(result[0], Radio)

    async def test_handle_create_ext_doc_upload_exception_handling(self):
        """Test exception handling in external doc upload"""
        with patch('pyfiles.bases.logger.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logger error")
            with self.assertRaises(Exception):
                await self.ext_docs_interface._handle_create_ext_doc_upload(
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=["doc1", "doc2"],
                    ext_docs_name="test_doc",
                    files=["file1.py", "file2.py"]
                )

    async def test_handle_delete_ext_doc_click_success(self):
        """Test successful external doc deletion"""
        with patch('pyfiles.ui.utils.handle_current_user', new_callable=AsyncMock) as mock_handle:
            mock_ext_docs = MagicMock()
            mock_docs = MagicMock()
            mock_docs.delete = AsyncMock()
            mock_docs.delete.return_value = (
                ["file1.py", "file2.py"],
                "file1.py",
                "Success message"
            )
            mock_ext_docs.get_current_codebase.return_value = mock_docs
            mock_handle.return_value = (None, mock_ext_docs)
            result = await self.ext_docs_interface._handle_delete_ext_doc_click(
                user_name="test_user",
                docs_name="test_docs",
                ext_docs_list=["doc1", "doc2"],
                ext_docs_name="test_doc",
                doc_id="file1.py"
            )
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 5)
            self.assertIsInstance(result[0], Radio)

    async def test_handle_delete_ext_doc_click_exception_handling(self):
        """Test exception handling in external doc deletion"""
        with patch('pyfiles.bases.logger.logger') as mock_logger:
            mock_logger.error.side_effect = Exception("Logger error")
            with self.assertRaises(Exception):
                await self.ext_docs_interface._handle_delete_ext_doc_click(
                    user_name="test_user",
                    docs_name="test_docs",
                    ext_docs_list=["doc1", "doc2"],
                    ext_docs_name="test_doc",
                    doc_id="file1.py"
                )