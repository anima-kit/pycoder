## tests.unit.ui.test_unit_utils
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch, AsyncMock
from gradio import Row, Button
from gradio_modal import Modal
from pyfiles.ui.utils import cancel_deletion_trigger, create_component, handle_current_user, toggle_visibility

class TestUIUtilsUnit(TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = MagicMock()
        with patch('pyfiles.bases.logger.logger', self.mock_logger):
            pass
    
    def test_create_component_success(self):
        """Test successful component creation."""
        with patch('gradio.Row') as mock_row:
            mock_component_instance = MagicMock()
            mock_row.return_value = mock_component_instance
            config = {
                "component_type": mock_row,
                "elem_id": "test_row",
                "visible": True
            }
            result = create_component(config)
            self.assertEqual(result, mock_component_instance)
            mock_row.assert_called_once_with(elem_id="test_row", visible=True)
    
    @patch('pyfiles.ui.utils.logger')
    def test_create_component_exception(self, mock_logger):
        """Test exception handling in component creation."""
        with patch('gradio.Button') as mock_button:
            mock_button.side_effect = Exception("Component creation failed")
            config = {
                "component_type": mock_button,
                "elem_id": "test_button",
                "visible": True
            }
            with self.assertRaises(Exception) as context:
                create_component(config)
    
    def test_toggle_visibility_success(self):
        """Test successful visibility toggle."""
        with patch('pyfiles.ui.utils.Row') as mock_row:
            mock_row_instance = MagicMock()
            mock_row.return_value = mock_row_instance
            result = toggle_visibility()
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 4)
            self.assertEqual(mock_row.call_count, 4) 
    
    @patch('pyfiles.ui.utils.logger')
    def test_toggle_visibility_exception(self, mock_logger):
        """Test exception handling in visibility toggle."""
        with patch('pyfiles.ui.utils.Row') as mock_row:
            mock_row.side_effect = Exception("Visibility toggle failed")
            with self.assertRaises(Exception) as context:
                toggle_visibility()

class TestAUIUtilsUnit(IsolatedAsyncioTestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_logger = MagicMock()
        with patch('pyfiles.bases.logger.logger', self.mock_logger):
            pass
    
    @patch('pyfiles.ui.utils.logger')
    async def test_handle_current_user_exception(self, mock_logger):
        """Test exception handling in current user handler."""
        mock_users = AsyncMock()
        mock_users.get_current_user = AsyncMock(side_effect=Exception("User retrieval failed"))
        user = "test_user"
        docs = "test_docs"
        external_docs = ["ext_doc1"]
        with self.assertRaises(Exception) as context:
            await handle_current_user(mock_users, user, docs, external_docs)
