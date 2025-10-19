### pyfiles.databases.milvus
## This file creates a Milvus client and a Milvus vectorstore to be used for document management and retrieval.

## External imports
from os import getenv
from dotenv import load_dotenv
from langchain_milvus import BM25BuiltInFunction, Milvus
from pymilvus import (  # type: ignore
    AsyncMilvusClient, 
    MilvusClient, 
    DataType, 
    Function, 
    FunctionType, 
    CollectionSchema
)
from pymilvus.milvus_client.index import IndexParams # type: ignore

## Internal imports
from pyfiles.bases.logger import logger
from pyfiles.agents.models import Models

## Get Milvus parameters from environment
load_dotenv()
uri: str = getenv("MILVUS_URI", "http://localhost:19530")
token: str = getenv("MILVUS_TOKEN", "root:Milvus")

## Connect the Milvus client
class MilvusClientStart:
    """
    A Milvus client manager to create synchronous and asynchronous clients.

    Attributes
    ------------
        uri: str
            The Milvus server URI.
            Defaults to MILVUS_URI in environment file or `http://localhost:19530` if MILVUS_URI doesn't exist.
        token: str
            The Milvus token to use.
            Defaults to MILVUS_TOKEN in environment file or `root:Milvus` if MILVUS_TOKEN doesn't exist.
        client: MilvusClient
            The synchronous Milvus client.
        aclient: AsyncMilvusClient
            The asynchronous Milvus client.
    """
    def __init__(
        self, 
        uri: str = uri,
        token: str = token
    ):
        """
        Initialize the Milvus clients.

        Args
        ------------
            uri: str
                The Milvus server URI.
                Defaults to MILVUS_URI in environment file or `http://localhost:19530` if MILVUS_URI doesn't exist.
            token: str
                The Milvus token to use.
                Defaults to MILVUS_TOKEN in environment file or `root:Milvus` if MILVUS_TOKEN doesn't exist.
            
        Raises
        ------------
            Exception: 
                If initializing the Milvus clients fails, error is logged and raised.
        """
        try:
            logger.info(f'⚙️ Creating Milvus client.')
            self.uri = uri
            self.token = token
            self.client: MilvusClient | None = None
            self.aclient: AsyncMilvusClient | None = None
            self._connect()
            logger.info(f'✅ Successfully created Milvus client.')
        except Exception as e:
            logger.error(f'❌ Problem creating Milvus Client: `{str(e)}`')
            raise

    ## Connect the sync and async clients
    def _connect(
        self
    ) -> None:
        """
        Connect the Milvus clients.
            
        Raises
        ------------
            Exception: 
                If creating the Milvus clients fails, error is logged and raised.
        """
        logger.info(f'⚙️ Connecting Milvus client.')
        try:
            self.client = MilvusClient(
                uri=self.uri,
                token=self.token,
                ## For pymilvus 2.5.12
                _async=False
            )
            self.aclient = AsyncMilvusClient(
                uri=self.uri,
                token=self.token
            )
            logger.info(f'✅ Milvus client connected on URI `{self.uri}`')
        except Exception as e:
            logger.error(f'❌ Problem connecting Milvus client: `{str(e)}`')
            raise

## Create the Milvus DB and vectorstore manager
class MilvusDB:
    def __init__(
        self, 
        client: MilvusClientStart, 
        db_name: str = "milvus_demo"
    ):
        """
        Initialize the Milvus DB from the given client.

        Args
        ------------
            client: MilvusClientStart
                The Milvus client to use.
            db_name: str
                The DB to use.
            
        Raises
        ------------
            Exception: 
                If initializing the Milvus DB fails, error is logged and raised.
        """
        try:
            self.db_name = db_name
            self.client: MilvusClient = client.client
            self.aclient: AsyncMilvusClient = client.aclient
            self.uri: str = client.uri
            self.token: str = client.token
            self._connect()
        except Exception as e:
            logger.error(f'❌ Problem initializing Milvus DB: `{str(e)}`')
            raise

    def _connect(
        self
    ) -> None:
        """
        Connect the Milvus client to the DB.
            
        Raises
        ------------
            Exception: 
                If connecting the Milvus DB fails, error is logged and raised.
        """
        logger.info(f'⚙️ Connecting to DB')
        try:
            existing_databases: list = self.client.list_databases()
            if self.db_name not in existing_databases:
                logger.info(f'⚙️ Creating Milvus DB.')
                self.client.create_database(self.db_name)
                logger.info(f'✅ Successfully created Milvus DB.')
            self.client.using_database(self.db_name)
            logger.info(f'📝 Using `{self.db_name}` database')
            logger.info(f'✅ Successfully connected to Milvus DB.')
        except Exception as e:
            logger.error(f'❌ Problem connecting to Milvus DB: `{str(e)}`')
            raise
    
    ## Create the Milvus collection
    def create_collection(
        self, 
        collection_name: str, 
        dim: int = 768
    ) -> None:
        """
        Create the Milvus collection.

        Args
        ------------
            collection_name: str
                The name of the collection.
            dim: int
                The dimension for dense vectors.
            
        Raises
        ------------
            Exception: 
                If creating the Milvus collection fails, error is logged and raised.
        """
        logger.info(f'⚙️ Creating Milvus collection.')
        try:
            ## Create schema for sparse and dense fields with metadata for doc group and source
            schema: CollectionSchema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field(field_name="pk", datatype=DataType.VARCHAR, max_length=255, is_primary=True)
            schema.add_field(field_name="dense", datatype=DataType.FLOAT_VECTOR, dim=dim)
            schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535, enable_analyzer=True)
            schema.add_field(field_name="group", datatype=DataType.VARCHAR, max_length=255, index=True)
            schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=255, index=True)

            ## Create the function for sparse embeddings
            bm25_function: Function = Function(
                name="text_bm25_emb",
                input_field_names=["text"],
                output_field_names=["sparse"],
                function_type=FunctionType.BM25
            )
            schema.add_function(bm25_function)

            ## Create the index params for dense and sparse vectors
            index_params: IndexParams = self.client.prepare_index_params()
            index_params.add_index(
                field_name="dense",
                index_type="IVF_FLAT",
                metric_type="L2"
            )

            index_params.add_index(
                field_name="sparse",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25",
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    "bm25_k1": 2.5,
                    "bm25_b": 0.7
                }
            )

            ## Create the collection
            self.client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
            logger.info(f'✅ Successfully created Milvus collection `{collection_name}`.')
        except Exception as e:
            logger.error(f'❌ Problem creating Milvus collection: `{str(e)}`')
            raise

    ## Create the vectorstore for retrieval
    def get_vectorstore(
        self, 
        models: Models, 
        collection_name: str
    ) -> Milvus:
        """
        Create the Milvus vectorstore for the given collection.

        Args
        ------------
            models: Models
                The models manager that houses the embedding model.
            collection_name: str
                The name of the collection.
            
        Raises
        ------------
            Exception: 
                If creating the Milvus vectorstore fails, error is logged and raised.
        """
        logger.info(f'⚙️ Creating Milvus vectorstore.')
        try:
            vectorstore: Milvus = Milvus(
                collection_name=collection_name,
                embedding_function=models.embed,
                builtin_function=BM25BuiltInFunction(
                    input_field_names="text", output_field_names="sparse"
                ),
                text_field="text",
                vector_field=[
                    "dense", 
                    "sparse"
                ],
                connection_args={
                    "uri": self.uri, 
                    "token": self.token, 
                    "db_name": self.db_name
                },
                consistency_level="Strong",
                drop_old=False,
                enable_dynamic_field=True
            )
            logger.info(f'✅ Successfully created Milvus vectorstore for collection `{collection_name}`.')
            return vectorstore
        except Exception as e:
            logger.error(f'❌ Problem creating Milvus vectorstore: `{str(e)}`')
            raise