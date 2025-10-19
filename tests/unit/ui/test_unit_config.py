## tests.unit.ui.test_unit_config
from unittest import TestCase
from unittest.mock import patch, MagicMock
from pyfiles.ui.gradio_config import Config, custom_css


class TestUIConfigUnit(TestCase):
    @patch('pyfiles.ui.gradio_config.logger')
    def test_config_initialization_success(self, mock_logger):
        """Test successful initialization of Config class"""
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        config = Config()
        self.assertIsInstance(config, Config)
        self.assertEqual(config.custom_css, custom_css)
        self.assertIsNotNone(config.theme)
    
    @patch('pyfiles.ui.gradio_config.logger')
    def test_config_initialization_with_custom_css(self, mock_logger):
        """Test successful initialization with custom CSS"""
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        custom_css_test = "test css"
        config = Config(custom_css=custom_css_test)
        self.assertIsInstance(config, Config)
        self.assertEqual(config.custom_css, custom_css_test)
        self.assertIsNotNone(config.theme)
    
    @patch('pyfiles.ui.gradio_config.logger')
    @patch('pyfiles.ui.gradio_config.Ocean')
    def test_config_initialization_exception_handling(self, mock_ocean, mock_logger):
        """Test exception handling during Config initialization"""
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        mock_ocean.side_effect = Exception("Gradio theme creation failed")
        with self.assertRaises(Exception) as context:
            Config()
        self.assertTrue("Gradio theme creation failed" in str(context.exception))
        self.assertTrue(mock_logger.error.called)
    
    @patch('pyfiles.ui.gradio_config.logger')
    @patch('pyfiles.ui.gradio_config.Ocean')
    def test_config_initialization_theme_exception(self, mock_ocean, mock_logger):
        """Test exception handling when gr.themes.Ocean fails"""
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        mock_ocean.return_value.set.side_effect = Exception("Theme set failed")
        with self.assertRaises(Exception) as context:
            Config()
        self.assertTrue("Theme set failed" in str(context.exception))
        self.assertTrue(mock_logger.error.called)
