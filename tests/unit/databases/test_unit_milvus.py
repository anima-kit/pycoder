## tests.unit.databases.test_unit_milvus
from unittest import TestCase
from unittest.mock import patch, MagicMock
from pyfiles.databases.milvus import MilvusClientStart, MilvusDB


class TestMilvusUnit(TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.uri = "http://localhost:19530"
        self.token = "root:Milvus"

    @patch('pyfiles.databases.milvus.MilvusClient')
    @patch('pyfiles.databases.milvus.AsyncMilvusClient')
    def test_milvus_client_start_success(
        self, 
        mock_async_client, 
        mock_sync_client
    ):
        """Test successful initialization of MilvusClientStart."""
        mock_sync_instance = MagicMock()
        mock_async_instance = MagicMock()
        mock_sync_client.return_value = mock_sync_instance
        mock_async_client.return_value = mock_async_instance
        client_start = MilvusClientStart(uri=self.uri, token=self.token)
        self.assertEqual(client_start.uri, self.uri)
        self.assertEqual(client_start.token, self.token)
        self.assertIsNotNone(client_start.client)
        self.assertIsNotNone(client_start.aclient)

    @patch('pyfiles.databases.milvus.MilvusClient')
    @patch('pyfiles.databases.milvus.AsyncMilvusClient')
    def test_milvus_client_start_exception(
        self, 
        mock_async_client, 
        mock_sync_client
    ):
        """Test exception handling in MilvusClientStart._connect()."""
        mock_sync_client.side_effect = Exception("Connection failed")
        mock_async_client.side_effect = Exception("Async connection failed")
        with self.assertRaises(Exception):
            MilvusClientStart(uri=self.uri, token=self.token)

    @patch('pyfiles.databases.milvus.MilvusClient')
    def test_milvus_db_init_success(
        self, 
        mock_sync_client
    ):
        """Test successful initialization of MilvusDB."""
        mock_instance = MagicMock()
        mock_sync_client.return_value = mock_instance
        mock_instance.list_databases.return_value = ["milvus_demo"]
        mock_client = MagicMock()
        mock_client.client = mock_instance
        mock_client.aclient = mock_instance
        mock_client.uri = self.uri
        mock_client.token = self.token
        milvus_db = MilvusDB(client=mock_client, db_name="milvus_demo")
        self.assertEqual(milvus_db.db_name, "milvus_demo")
        self.assertEqual(milvus_db.client, mock_instance)
        self.assertEqual(milvus_db.uri, self.uri)
        self.assertEqual(milvus_db.token, self.token)

    @patch('pyfiles.databases.milvus.MilvusClient')
    def test_milvus_db_init_create_db_success(
        self, 
        mock_sync_client
    ):
        """Test successful DB creation when it doesn't exist."""
        mock_instance = MagicMock()
        mock_sync_client.return_value = mock_instance
        mock_instance.list_databases.return_value = []
        mock_client = MagicMock()
        mock_client.client = mock_instance
        mock_client.aclient = mock_instance
        mock_client.uri = self.uri
        mock_client.token = self.token
        milvus_db = MilvusDB(client=mock_client, db_name="new_db")
        mock_instance.create_database.assert_called_once_with("new_db")
        mock_instance.using_database.assert_called_once_with("new_db")

    @patch('pyfiles.databases.milvus.MilvusClient')
    def test_milvus_db_init_exception(
        self, 
        mock_sync_client
    ):
        """Test exception handling in MilvusDB._connect()."""
        mock_instance = MagicMock()
        mock_sync_client.return_value = mock_instance
        mock_instance.list_databases.side_effect = Exception("Database listing failed")
        mock_client = MagicMock()
        mock_client.client = mock_instance
        mock_client.aclient = mock_instance
        mock_client.uri = self.uri
        mock_client.token = self.token
        with self.assertRaises(Exception):
            MilvusDB(client=mock_client, db_name="milvus_demo")

    @patch('pyfiles.databases.milvus.MilvusClient')
    def test_create_collection_success(
        self, 
        mock_sync_client
    ):
        """Test successful creation of collection."""
        mock_instance = MagicMock()
        mock_sync_client.return_value = mock_instance
        mock_client = MagicMock()
        mock_client.client = mock_instance
        mock_client.aclient = mock_instance
        milvus_db = MilvusDB(client=mock_client)
        milvus_db.create_collection(collection_name="test_collection", dim=768)
        mock_instance.create_schema.assert_called_once()
        mock_instance.create_collection.assert_called_once()

    @patch('pyfiles.databases.milvus.MilvusClient')
    def test_create_collection_exception(
        self,
        mock_sync_client
    ):
        """Test exception handling in create_collection()."""
        mock_instance = MagicMock()
        mock_sync_client.return_value = mock_instance
        mock_instance.create_schema.side_effect = Exception("Schema creation failed")
        mock_client = MagicMock()
        mock_client.client = mock_instance
        mock_client.aclient = mock_instance
        milvus_db = MilvusDB(client=mock_client)
        with self.assertRaises(Exception):
            milvus_db.create_collection(collection_name="test_collection", dim=768)

    @patch('pyfiles.databases.milvus.Milvus')
    def test_get_vectorstore_success(
        self, 
        mock_milvus_class
    ):
        """Test successful retrieval of vectorstore."""
        mock_instance = MagicMock()
        mock_milvus_class.return_value = mock_instance
        mock_embedding = MagicMock()
        mock_embedding.embed.return_value = [0.1] * 768
        mock_models = MagicMock()
        mock_models.embed = mock_embedding
        mock_client = MagicMock()
        mock_client.uri = self.uri
        mock_client.token = self.token
        milvus_db = MilvusDB(client=mock_client)
        vectorstore = milvus_db.get_vectorstore(models=mock_models, collection_name="test_collection")
        self.assertEqual(vectorstore, mock_instance)
        mock_milvus_class.assert_called_once()

    @patch('pyfiles.databases.milvus.Milvus')
    def test_get_vectorstore_exception(
        self, 
        mock_milvus_class
    ):
        """Test exception handling in get_vectorstore()."""
        mock_milvus_class.side_effect = Exception("Vectorstore creation failed")
        mock_embedding = MagicMock()
        mock_embedding.embed.return_value = [0.1] * 768
        mock_models = MagicMock()
        mock_models.embed = mock_embedding
        mock_client = MagicMock()
        mock_client.uri = self.uri
        mock_client.token = self.token
        milvus_db = MilvusDB(client=mock_client)
        with self.assertRaises(Exception):
            milvus_db.get_vectorstore(models=mock_models, collection_name="test_collection")
