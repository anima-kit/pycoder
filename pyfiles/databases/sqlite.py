### pyfiles.databases.sqlite
## This file creates an SQLite DB manager for managing documents in an SQLite DB.

## External imports
from os import remove
from os.path import exists
from json import loads, dumps
from aiosqlite import (
    connect, 
    Connection, 
    Cursor, 
    Row
)
from langchain_classic.docstore.document import Document
from typing import (
    List, 
    Dict, 
    Tuple, 
    Iterable
)

## Internal imports
from pyfiles.bases.logger import logger

## The SQLite DB manager
class SQLiteDB:
    """
    An SQLite DB manager to manage documents.

    Attributes
    ------------
        db_path: str
                The path of the SQLite DB.
    """
    def __init__(
        self, 
        db_path: str = ':memory:'
    ):
        """
        Initialize the SQLite DB manager.

        Args
        ------------
            db_path: str
                The path of the SQLite DB.
            
        Raises
        ------------
            Exception: 
                If initializing the SQLite DB manager fails, error is logged and raised.
        """
        logger.info(f'⚙️ Initializing the SQLite DB')
        try:
            self.db_path = db_path
            logger.info(f'✅ SQLite DB initialized for path `{self.db_path}`')
        except Exception as e:
            logger.error(f'❌ Problem initializing the SQLite DB: `{str(e)}`')
            raise

    ## Create the table for each execution
    async def _create_table(
        self, 
        conn: Connection
    ) -> None:
        """
        Create the SQLite DB table for each execution.

        Args
        ------------
            conn: Connection
                The aiosqlite connection.
            
        Raises
        ------------
            Exception: 
                If creating the SQLite DB table fails, error is logged and raised.
        """
        ## Create documents with id, content, and metadata
        try:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    metadata TEXT
                )
            ''')
        except Exception as e:
            logger.error(f'❌ Problem creating SQLite DB table: `{str(e)}`')
            raise

    ## Update documents in DB
    async def insert_documents(
        self, 
        documents: List[Document], 
        ids: List[str]
    ):
        """
        Insert or replace documents in DB.

        Args
        ------------
            documents: List[Document]
                The documents to insert or replace.
            ids: List[str]
                The unique IDs for each document.
            
        Raises
        ------------
            Exception: 
                If inserting or replacing the documents fails, error is logged and raised.
        """
        try:
            async with connect(self.db_path) as conn:
                await self._create_table(conn)
                cursor: Cursor = await conn.cursor()
                for doc, doc_id in zip(documents, ids):
                    metadata_json: str = dumps(doc.metadata)
                    await cursor.execute('''
                        INSERT OR REPLACE INTO documents (id, content, metadata)
                        VALUES (?, ?, ?)
                    ''', (doc_id, doc.page_content, metadata_json))
                await conn.commit()
        except Exception as e:
            logger.error(f'❌ Problem inserting documents into SQLite DB: `{str(e)}`')
            raise

    ## Get relevant documents from group
    async def get_documents_by_group(
        self, 
        group: str
    ) -> List[Tuple[str, Document]]:
        """
        Get documents by the `group` metadata.

        Args
        ------------
            group: str
                The metadata with which to obtain relevant documents.

        Return
        ------------
            List[Tuple[str, Document]]:
                A list of documents with associated IDs.
            
        Raises
        ------------
            Exception: 
                If getting the documents fails, error is logged and raised.
        """
        try:
            async with connect(self.db_path) as conn:
                ## Get relevant document information from DB
                await self._create_table(conn)
                cursor: Cursor = await conn.cursor()
                await cursor.execute('''
                    SELECT id, content, metadata FROM documents
                    WHERE json_extract(metadata, '$.group') = ?
                ''', (group,))
                rows: Iterable[Row] = await cursor.fetchall()
                ## Create Document for each relevant doc
                docs: List[Tuple[str, Document]] = []
                for row in rows:
                    doc_id, content, metadata_str = row
                    metadata: Dict[str, str] = loads(metadata_str)
                    doc: Document = Document(page_content=content, metadata=metadata)
                    docs.append((doc_id, doc))
                return docs
        except Exception as e:
            logger.error(f'❌ Problem getting documents by group from SQLite DB: `{str(e)}`')
            raise

    ## Get relevant documents from ID
    async def delete_documents_by_id(
        self, 
        doc_ids: List[str]
    ) -> None:
        """
        Delete documents with the given IDs from the DB.

        Args
        ------------
            docs_ids: List[str]
                The IDs of the documents to delete.
            
        Raises
        ------------
            Exception: 
                If deleting the documents fails, error is logged and raised.
        """
        try:
            async with connect(self.db_path) as conn:
                await self._create_table(conn)
                cursor: Cursor = await conn.cursor()
                await cursor.executemany('''
                    DELETE FROM documents WHERE id = ?
                ''', [(doc_id,) for doc_id in doc_ids])
                await conn.commit()
        except Exception as e:
            logger.error(f'❌ Problem deleting documents by ID from SQLite DB: `{str(e)}`')
            raise

    ## Delete relevant documents from source tag
    async def delete_documents_by_source(
        self, 
        sources: List[str],
        group: str
    ) -> None:
        """
        Delete documents given the `source` metadata tag.

        Args
        ------------
            sources: List[str]
                The `source` tag for the documents to delete.
            group: str
                The documents group.
            
        Raises
        ------------
            Exception: 
                If deleting the documents fails, error is logged and raised.
        """
        try:
            async with connect(self.db_path) as conn:
                await self._create_table(conn)
                cursor: Cursor = await conn.cursor()
                await cursor.executemany('''
                    DELETE FROM documents
                    WHERE json_extract(metadata, '$.source') = ? 
                    AND json_extract(metadata, '$.group') = ?
                ''', [(source, group) for source in sources])
                await conn.commit()
        except Exception as e:
            logger.error(f'❌ Problem deleting documents by source from SQLite DB: `{str(e)}`')
            raise

    ## Delete the physical SQLite DB file
    def delete_db_file(
        self
    ) -> None:
        """
        Delete the physical DB file.
            
        Raises
        ------------
            Exception: 
                If deleting the DB file fails, error is logged and raised.
        """
        try:
            if exists(self.db_path):
                remove(self.db_path)
        except Exception as e:
            logger.error(f'❌ Problem deleting SQLite DB file: `{str(e)}`')
            raise

    ## Get list of codebases in the given DB
    async def get_codebase_list(
        self, 
        codebase_type: str
    ) -> List[str]:
        """
        Get all codebases in the given DB.

        Args
        ------------
            codebase_type: str
                The codebase type.
                Can be `user` or `external`.

        Return
        ------------
            List[str]:
                A list of codebases in the DB.
            
        Raises
        ------------
            Exception: 
                If getting the codebases fails, error is logged and raised.
        """
        try:
            async with connect(self.db_path) as conn:
                await self._create_table(conn)
                cursor: Cursor = await conn.cursor()
                await cursor.execute(f'''
                    SELECT DISTINCT json_extract(metadata, '$.group') 
                    FROM documents
                    WHERE json_extract(metadata, '$.codebase_type') = "{codebase_type}"
                ''')
                groups: Iterable[Row] = await cursor.fetchall()
                return list(set(g[0].rsplit('_', 1)[0] for g in groups if g[0]))
        except Exception as e:
            logger.error(f'❌ Problem getting codebases from SQLite DB: `{str(e)}`')
            raise
