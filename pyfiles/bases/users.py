### pyfiles.bases.users
## This file creates the users handler with which users can be managed.

## External imports
from re import sub
from os import makedirs, remove
from os.path import exists, join
from typing import Tuple, List

## Internal imports
from pyfiles.agents.models import Models
from pyfiles.bases.codebases import Codebases
from pyfiles.bases.logger import logger
from pyfiles.databases.milvus import MilvusClientStart, MilvusDB
from pyfiles.databases.sqlite import SQLiteDB

## Create the user handler
class Users:
    """
    A users class that handles the management of users.

    Attributes
    ------------
        models: Models
                The models manager that houses the LLM and embedding model.
        client: MilvusClientStart
            The Milvus client to use for Milvus management.
        user_dir: str
            The directory to store SQLite DBs.
            Defaults to `user_databases`.
        selected_user (Optional): Codebases
            The codebase handler for the selected user.
            Default to None.
        selected_ext_codebases (Optional): Codebases
            The codebase handler for the selected user's external codebases.
    """
    def __init__(
        self, 
        models: Models, 
        client: MilvusClientStart
    ):
        """
        Initialize the users handler.

        Args
        ------------
            models: Models
                The models manager that houses the LLM and embedding model.
            client: MilvusClientStart
                The Milvus client to use for Milvus management.
            
        Raises
        ------------
            Exception: 
                If initializing the users handler fails, error is logged and raised.
        """
        try:
            self.client = client
            self.models = models
            self.user_dir: str = 'user_databases'
            if not exists(self.user_dir):
                makedirs(self.user_dir)
            self.selected_user: Codebases | None = None
            self.selected_ext_codebases: Codebases | None = None
        except Exception as e:
            logger.error(f'❌ Problem initializing user handler: `{str(e)}`.')
            raise

    ## Format user name properly
    def _fix_name(
        self,
        name: str
    ) -> str:
        """
        Format the user name to save to Milvus and SQLite DBs properly.

        Args
        ------------
            name: str
                The name to fix.

        Returns
        ------------
            str:
                The fixed name. 

        Raises
        ------------
            Exception: 
                If fixing the name fails, error is logged and raised.
        """
        try:
            name = name.replace(" ", "_")
            name = sub(r'[^a-zA-Z0-9_]', '_', name)
            if name=='':
                name = 'unnamed'
            if name[-1]=='_':
                name = name[:len(name)-1]
            return name
        except Exception as e:
            logger.error(f'❌ Problem fixing the name: `{str(e)}`.')
            raise

    ## Get codebases handler for user's main codebases
    async def _get_selected_codebases(
        self,
        milvus_db: MilvusDB,
        sqlite_db: SQLiteDB,
        selected_codebase_name: str | None = None,
        selected_ext_codebases: List[str] | None = None
    ) -> Codebases:
        """
        Get the codebases handler for the user's main codebases.

        Args
        ------------
            milvus_db: MilvusDB
                The Milvus DB manager.
            sqlite_db: SQLiteDB
                The SQLite DB manager.
            selected_codebase_name: str
                The name of the selected main codebase.

        Returns
        ------------
            Codebases:
                The codebases handler. 

        Raises
        ------------
            Exception: 
                If getting the codebases fails, error is logged and raised.
        """
        try:
            selected_user_instance: Codebases = Codebases(
                milvus_db=milvus_db, 
                sqlite_db=sqlite_db,
                models=self.models,
                selected_codebase_name=selected_codebase_name,
                external_codebases_list=selected_ext_codebases,
                codebase_type="user"
            )
            selected_user_instance.selected_codebase = await selected_user_instance.initialize_default_codebase()
            return selected_user_instance
        except Exception as e:
            logger.error(f'❌ Problem getting selected codebases: `{str(e)}`.')
            raise

    ## Get codebases handler for selected external codebases
    async def _get_selected_ext_codebases(
        self,
        milvus_db: MilvusDB,
        sqlite_db: SQLiteDB,
        selected_codebase_name: str | None = None,
        selected_ext_codebases: List[str] | None = None
    ) -> Codebases:
        """
        Get the codebases handler for the user's external codebases.

        Args
        ------------
            milvus_db: MilvusDB
                The Milvus DB manager.
            sqlite_db: SQLiteDB
                The SQLite DB manager.
            selected_codebase_name: str
                The name of the selected main codebase.
            selected_ext_codebases: List[str]
                A list of the selected external codebases.

        Returns
        ------------
            Codebases:
                The codebases handler. 

        Raises
        ------------
            Exception: 
                If getting the codebases fails, error is logged and raised.
        """
        try:
            selected_ext_codebases_instance: Codebases = Codebases(
                milvus_db=milvus_db, 
                sqlite_db=sqlite_db,
                models=self.models,
                selected_codebase_name=selected_codebase_name,
                external_codebases_list=selected_ext_codebases,
                codebase_type="external"
            ) 
            selected_ext_codebases_instance.selected_codebase = await selected_ext_codebases_instance.initialize_default_codebase()
            return selected_ext_codebases_instance
        except Exception as e:
            logger.error(f'❌ Problem getting selected codebases: `{str(e)}`.')
            raise
        
    ## Get selected user main and external codebases handler
    async def get_current_user(
        self, 
        name: str, 
        selected_codebase_name: str | None = None, 
        selected_ext_codebases: List[str] | None = None
    ) -> Tuple[Codebases, Codebases]:
        """
        Select the current user with the given selected codebases.

        Args
        ------------
            name: str
                The user name.
            selected_codebase_name: str
                The name of the selected main codebase.
            selected_ext_codebases: List[str]
                A list of the selected external codebases.

        Returns
        ------------
            Tuple[Codebases, CodeBases]:
                A tuple of codebase handlers for the selected main and external codebases. 

        Raises
        ------------
            Exception: 
                If selecting the current user fails, error is logged and raised.
        """
        try:
            ## Create DBs
            milvus_db: MilvusDB = MilvusDB(
                client=self.client, 
                db_name=name
            )
            sqlite_db: SQLiteDB = SQLiteDB(
                db_path=join(self.user_dir, f'{name}.db')
            )
            ## Create user and external codebases handlers
            selected_user_instance = await self._get_selected_codebases(
                milvus_db=milvus_db,
                sqlite_db=sqlite_db,
                selected_codebase_name=selected_codebase_name,
                selected_ext_codebases=selected_ext_codebases
            )
            selected_ext_codebases_instance = await self._get_selected_ext_codebases(
                milvus_db=milvus_db,
                sqlite_db=sqlite_db,
                selected_codebase_name=selected_codebase_name,
                selected_ext_codebases=selected_ext_codebases
            )
            ## Set attributes of class
            self.selected_user = selected_user_instance 
            self.selected_ext_codebases = selected_ext_codebases_instance 
            if self.selected_user.selected_codebase!=None:
                self.selected_user.selected_agent = selected_user_instance.get_current_agent(
                    self.selected_user.selected_codebase.codebase
                )
            else:
                raise ValueError(f'The `selected_user.selected_codebase` attribute should not be None')
            return (
                selected_user_instance,         # User main codebases handler
                selected_ext_codebases_instance # User ext codebases handler
            )
        except Exception as e:
            logger.error(f'❌ Problem getting codebases for current user: `{str(e)}`.')
            raise

    ## List all users
    def get_users_list(
        self
    ) -> List[str]: 
        """
        Get a list of all available users.

        Returns
        ------------
            List[str]
                A of the available user names. 

        Raises
        ------------
            Exception: 
                If getting the user list fails, error is logged and raised.
        """
        try:
            if self.client.client!=None:
                dbs: List[str] = self.client.client.list_databases()
                dbs.remove('default')
                logger.info(f'📝 Available users `{dbs}`.')
                return dbs
            else:
                raise ValueError(f'❌ Attribute `client.client` should not be None.')
        except Exception as e:
            logger.error(f'❌ Problem getting list of users: `{str(e)}`')
            raise

    ## Create user
    async def create_new_user(
        self, 
        name: str,
        selected_user: str
    ) -> Tuple[str, str]:
        """
        Create a new user.

        Args
        ------------
            name: str
                Name of the user to create.

        Returns
        ------------
            Tuple[str, str]:
                A tuple of the newly selected user and a status message. 

        Raises
        ------------
            Exception: 
                If creating a new user fails, error is logged and raised.
        """
        try:
            ## Fix the name and make sure user doesn't already exist
            name = self._fix_name(name)
            users: List[str] = self.get_users_list()
            if name in users:
                status_message: str = f'User "{name}" already exists. Choose another name.'
                return (
                    name,
                    status_message            
                )
            if name=='default':
                status_message = f"User name can't be default. Choose another name."
                return (
                    selected_user,
                    status_message            
                )
            ## Create new codebases handler for user
            logger.info(f'⚙️ Creating new user `{name}`.')
            self.selected_user, self.selected_ext_codebases = await self.get_current_user(name=name)
            status_message = f'✅ Successfully created user `{name}`.'
            logger.info(status_message)
            return (
                name,           # New selected user
                status_message  # Status
            )
        except Exception as e:
            logger.error(f'❌ Problem creating user: `{str(e)}`')
            raise

    ## Delete selected user
    async def delete_user(
        self, 
        name: str
    ) -> Tuple[str, str]:
        """
        Delete the selected user.

        Args
        ------------
            name: str
                Name of the user to delete.

        Returns
        ------------
            Tuple[str, str]:
                A tuple of the newly selected user and a status message. 

        Raises
        ------------
            Exception: 
                If deleting the user fails, error is logged and raised.
        """
        logger.info(f'⚙️ Deleting user `{name}`.')
        try:
            ## Delete all codebases (all Milvus collections and SQLite docs for user)
            if self.selected_user != None: 
                codebases: List[str] = await self.selected_user.sqlite_db.get_codebase_list(
                    codebase_type='user'
                )
                for codebase in codebases:
                    await self.selected_user.delete_codebase(codebase)
                codebases = await self.selected_user.sqlite_db.get_codebase_list(
                    codebase_type='external'
                )
                for codebase in codebases:
                    await self.selected_user.delete_codebase(codebase)

                ## Now drop the Milvus and SQLite DBs
                if self.client.client!=None:
                    self.client.client.drop_database(name)
                    self.selected_user.sqlite_db.delete_db_file()
                    status_message: str = f'✅ Successfully deleted user `{name}`.'              

                    ## Get new selected user
                    users: List[str] = self.get_users_list()
                    selected_user: str | None = None
                    if len(users)!=0:
                        selected_user = users[0]
                    if selected_user!=None:
                        self.selected_user, self.selected_ext_codebases = await self.get_current_user(
                            name=selected_user
                        )
                        logger.info(status_message)
                        return (
                            selected_user,  # New selected user
                            status_message  # Status
                        )
                    else:
                        raise ValueError(f'❌ Selected user should not be None.')
                else:
                    raise ValueError(f'❌ Attribute client.client should not be None.')
            else:
                raise ValueError(f'❌ Selected user should not be None.')
        except Exception as e:
            logger.error(f'❌ Problem deleting user: `{str(e)}`')
            raise

    ## Get user details
    async def get_user_state_details(
        self, 
        name: str, 
        selected_codebase: str
    ) -> Tuple[str, str, List[str], List[str], str | None]:
        """
        Get details for the selected user.

        Args
        ------------
            name: str
                The user name.
            selected_codebase: str
                The name of the user's main selected codebase.

        Returns
        ------------
            Tuple[str, str]:
                A tuple of the newly selected user and a status message. 

        Raises
        ------------
            Exception: 
                If creating a new user fails, error is logged and raised.
        """
        try:
            ## Get the selected user
            self.selected_user, self.selected_ext_codebases = await self.get_current_user(
                name=name, 
                selected_codebase_name=selected_codebase
            )
            choices: List[str] = await self.selected_user.sqlite_db.get_codebase_list(codebase_type=self.selected_user.codebase_type)
            external_choices: List[str] = await self.selected_ext_codebases.sqlite_db.get_codebase_list(codebase_type=self.selected_ext_codebases.codebase_type)
            external_choice: str | None = external_choices[0] if external_choices!=[] else None
            return (
                name,               # User name
                selected_codebase,  # Selected codebase
                choices,            # Available codebases
                external_choices,   # Available ext codebases
                external_choice     # Selected ext codebase
            )
        except Exception as e:
            logger.error(f'❌ Problem getting user state details: `{str(e)}`')
            raise