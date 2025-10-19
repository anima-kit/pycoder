## tests.unit.ui.test_unit_app
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from pyfiles.ui.gradio_config import Config
from pyfiles.agents.models import Models
from pyfiles.databases.milvus import MilvusClientStart
from pyfiles.ui.gradio_app import GradioApp

class TestUIAppUnit(TestCase):
    def setUp(self):
        self.config = MagicMock(spec=Config)
        self.models = MagicMock(spec=Models)
        self.milvus_client = MagicMock(spec=MilvusClientStart)

    def test_init_success(self):
        """Test successful initialization of GradioApp"""
        app = GradioApp(
            config=self.config,
            models=self.models,
            milvus_client=self.milvus_client
        )
        self.assertEqual(app.config, self.config)
        self.assertEqual(app.models, self.models)
        self.assertEqual(app.milvus_client, self.milvus_client)

    def test_create_dynamic_states_success(self):
        """Test successful creation of dynamic states"""
        app = GradioApp(
            config=self.config,
            models=self.models,
            milvus_client=self.milvus_client
        )
        result = app._create_dynamic_states(
            initial_user_name="test_user",
            initial_codebase_name="test_codebase",
            initial_thread="thread_1",
            initial_code="code_1",
            initial_external_codebase="ext_codebase_1",
            initial_external_docs_file="file_1",
            initial_external_docs_list_all=["ext_codebase_1, ext_codebase_2"]
        )
        self.assertIn("selected_user_state", result)
        self.assertIn("selected_codebase_state", result)
        self.assertIn("selected_thread_state", result)
        self.assertIn("selected_code_state", result)
        self.assertIn("selected_external_codebase_state", result)
        self.assertIn("selected_external_docs_list_state", result)
        self.assertIn("selected_external_docs_file_state", result)

    def test_create_dynamic_states_exception(self):
        """Test exception handling in create_dynamic_states"""
        app = GradioApp(
            config=self.config,
            models=self.models,
            milvus_client=self.milvus_client
        )
        with patch('pyfiles.ui.gradio_app.logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Dynamic states error")
            with self.assertRaises(Exception) as context:
                app._create_dynamic_states(
                    initial_user_name="test_user",
                    initial_codebase_name="test_codebase",
                    initial_thread="thread_1",
                    initial_code="code_1",
                    initial_external_codebase="ext_codebase_1",
                    initial_external_docs_file="file_1",
                    initial_external_docs_list_all=["ext_codebase_1", "ext_codebase_2"]
                )
            self.assertIn("Dynamic states error", str(context.exception))

class TestAUIAppUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = MagicMock(spec=Config)
        self.models = MagicMock(spec=Models)
        self.milvus_client = MagicMock(spec=MilvusClientStart)

    async def test_create_initial_states_exception(self):
        """Test exception handling in create_initial_states"""
        with patch('pyfiles.ui.gradio_app.Users') as mock_users_class:
            mock_users_instance = MagicMock()
            mock_users_class.return_value = mock_users_instance
            mock_users_instance.initialize_default_user = AsyncMock(side_effect=Exception("Init error"))
            app = GradioApp(
                config=self.config,
                models=self.models,
                milvus_client=self.milvus_client
            )
            with patch('pyfiles.ui.gradio_app.logger') as mock_logger:
                mock_logger.info.side_effect = Exception("Logging error")
                with self.assertRaises(Exception) as context:
                    await app._create_initial_states()

    async def test_app_exception(self):
        """Test exception handling in app method"""
        with patch('pyfiles.ui.gradio_app.Users') as mock_users_class:
            mock_users_instance = MagicMock()
            mock_users_class.return_value = mock_users_instance
            mock_users_instance.initialize_default_user = AsyncMock(side_effect=Exception("App error"))
            app = GradioApp(
                config=self.config,
                models=self.models,
                milvus_client=self.milvus_client
            )
            with patch('pyfiles.ui.gradio_app.logger') as mock_logger:
                mock_logger.info.side_effect = Exception("Logging error")
                with self.assertRaises(Exception) as context:
                    await app.app()
