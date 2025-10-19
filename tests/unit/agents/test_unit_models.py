### tests.unit.agents.test_unit_models
import unittest
from unittest.mock import patch, MagicMock
from pyfiles.agents.models import Models

model_name = 'model-name'
embed_name = 'embed_name'

class MockModel:
    """
    A mock model object representing a pulled model from Ollama.
    """
    def __init__(self, model):
        self.model = model

class MockListResponse:
    """
    A mock response object representing the result of an ollama.list() call.
    """
    def __init__(self, models):
        self.models = [MockModel(model=m) for m in models]

class MockPullResponse:
    """
    A mock response object representing the result of an ollama.pull() call.
    """
    def __init__(self, status):
        self.status = status

class TestOllamaClientUnit(unittest.TestCase):
    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.ChatOllama')
    def test_init_client_success(
        self, 
        mock_client, 
        mock_list
    ):
        """
        Test successful initialization of OllamaClient with a custom URL.
        """
        url = 'custom-url'
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_list.return_value = MockListResponse(models=[model_name, embed_name])
        mock_client_instance.list = mock_list
        client = Models(url=url, llm_name=model_name, embed_name=embed_name)
        self.assertEqual(client.url, url)
        mock_client.assert_called_once_with(model=model_name, temperature=0.5, base_url=url)

    @patch('pyfiles.agents.models.pull')
    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.ChatOllama')
    def test_init_lm_existing_model(
        self, 
        mock_client, 
        mock_list, 
        mock_pull
    ):
        """
        Test initialization of language model when the model already exists.
        """
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_list.return_value = MockListResponse(models=[model_name, embed_name])
        mock_client_instance.list = mock_list
        client = Models(llm_name=model_name, embed_name=embed_name)
        mock_pull.assert_not_called()

    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.pull')
    @patch('pyfiles.agents.models.ChatOllama')
    def test_init_lm_pull_exception(
        self, 
        mock_client, 
        mock_pull, 
        mock_list
    ):
        """
        Test initialization of language model when pulling fails.
        """
        mock_list.return_value = MockListResponse(models=[])
        mock_pull.side_effect = Exception("Pull failed")
        with self.assertRaises(Exception):
            Models(llm_name=model_name, embed_name=embed_name)

    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.pull')
    @patch('pyfiles.agents.models.ChatOllama')
    def test_init_lm_chat_ollama_exception(
        self, 
        mock_client, 
        mock_pull, 
        mock_list
    ):
        """
        Test initialization of language model when ChatOllama creation fails.
        """
        mock_list.return_value = MockListResponse(models=[])
        mock_pull.return_value = MockPullResponse(status="success")
        mock_client.side_effect = Exception("ChatOllama failed")
        with self.assertRaises(Exception):
            Models(llm_name=model_name, embed_name=embed_name)

    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.pull')
    @patch('pyfiles.agents.models.OllamaEmbeddings')
    def test_init_embed_pull_exception(
        self, 
        mock_embed, 
        mock_pull, 
        mock_list
    ):
        """
        Test initialization of embedding model when pulling fails.
        """
        mock_list.return_value = MockListResponse(models=[])
        mock_pull.side_effect = Exception("Pull failed")
        with self.assertRaises(Exception):
            Models(llm_name=model_name, embed_name=embed_name)

    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.pull')
    @patch('pyfiles.agents.models.OllamaEmbeddings')
    def test_init_embed_ollama_embeddings_exception(
        self, 
        mock_embed, 
        mock_pull, 
        mock_list
    ):
        """
        Test initialization of embedding model when OllamaEmbeddings creation fails.
        """
        mock_list.return_value = MockListResponse(models=[])
        mock_pull.return_value = MockPullResponse(status="success")
        mock_embed.side_effect = Exception("OllamaEmbeddings failed")
        with self.assertRaises(Exception):
            Models(llm_name=model_name, embed_name=embed_name)

    @patch('pyfiles.agents.models.ollama_list')
    def test_list_pulled_models_exception(
        self, 
        mock_list
    ):
        """
        Test listing pulled models when listing fails.
        """
        mock_list.side_effect = Exception("List failed")
        with self.assertRaises(Exception):
            models = Models(llm_name=model_name, embed_name=embed_name)
            models._list_pulled_models()

    @patch('pyfiles.agents.models.ollama_list')
    @patch('pyfiles.agents.models.ChatOllama')
    def test_init_exception(
        self, 
        mock_client, 
        mock_list
    ):
        """
        Test initialization when model creation fails.
        """
        mock_list.return_value = MockListResponse(models=[])
        mock_client.side_effect = Exception("Initialization failed")
        with self.assertRaises(Exception):
            Models(llm_name=model_name, embed_name=embed_name)