### pyfiles.ui.gradio_app
## This file creates the main Gradio app.
## All states and components for each interface is created.

## External imports
from os.path import join
from json import loads
from gradio import Blocks, State, HTML
from typing import List, Tuple, Dict, Any

## Internal imports
from pyfiles.agents.models import Models
from pyfiles.bases.codebases import Codebases
from pyfiles.bases.logger import logger
from pyfiles.bases.threads import Threads
from pyfiles.bases.users import Users
from pyfiles.databases.milvus import MilvusClientStart
from pyfiles.databases.sqlite import SQLiteDB
from pyfiles.ui.gradio_config import Config
from pyfiles.ui.interface_chat import ChatInterface
from pyfiles.ui.interface_docs import DocsInterface
from pyfiles.ui.interface_ext_docs import ExtDocsInterface
from pyfiles.ui.interface_main import MainInterface
from pyfiles.ui.interface_user import UserInterface

## Create the main Gradio app
class GradioApp:
    """
    A class to create a main Gradio app.
    This creates all Gradio app states, components, and component triggers for all interfaces.

    Attributes
    ------------
        config: Config
            The Gradio configurations.
        models: Models
            The models handler.
        milvus_client: MilvusClientStart
            The Milvus client.
        users: Users
            The users handler.
    """
    def __init__(
        self, 
        config: Config, 
        models: Models, 
        milvus_client: MilvusClientStart
    ):
        """
        Initialize the main Gradio app.

        Args
        ------------
            config: Config
                The Gradio configurations.
            models: Models
                The models handler.
            milvus_client: MilvusClientStart
                The Milvus client.
            
        Raises
        ------------
            Exception: 
                If initializing the main Gradio app fails, error is logged and raised.
        """
        try:
            self.config = config
            self.milvus_client = milvus_client
            self.models = models
            self.users: Users | None = None
        except Exception as e:
            logger.error(f'❌ Problem initializing GradioApp: `{str(e)}`')
            raise

    async def _create_initial_states(
        self
    ) -> Dict[str, Any]:
        """
        Create the initial states.

        Returns
        ------------
            Dict[str, Any]:
                A dictionary of initial states.
            
        Raises
        ------------
            Exception: 
                If creating the initial states fails, error is logged and raised.
        """
        logger.info('⚙️ Creating initial states')
        try:
            ## Get the users handler
            self.users = Users(
                models=self.models, 
                client=self.milvus_client
            )

            ## Get user properties
            initial_user_list: List[str] = self.users.get_users_list()
            logger.info(f'Initial users {initial_user_list}')
            if len(initial_user_list)==0:
                initial_user_name: str = 'default_user'
                _, _ = await self.users.get_current_user(
                    name=initial_user_name
                )
            else:
                initial_user_name = initial_user_list[0]
            initial_del_button: bool = False
            if len(initial_user_list)>1:
                initial_del_button = True

            ## Get all codebases for user
            sqlite_db = SQLiteDB(db_path=join(self.users.user_dir, f'{initial_user_name}.db'))
            initial_codebase_list: List[str] = await sqlite_db.get_codebase_list('user')
            initial_codebase_name: str = initial_codebase_list[0]
            initial_external_docs_list_all: List[str] = await sqlite_db.get_codebase_list('external')
            self.users.selected_user, self.users.selected_ext_codebases = await self.users.get_current_user(
                name=initial_user_name,
                selected_codebase_name=initial_codebase_name,
                selected_ext_codebases=initial_external_docs_list_all
            )

            ## Get main codebases handler and initial selected codebase properties
            initial_user_instance: Codebases = self.users.selected_user
            initial_codebase_del_button: bool = False
            if len(initial_codebase_list)>1:
                initial_codebase_del_button = True
            initial_codebase_instance: Threads = initial_user_instance.get_current_codebase(initial_codebase_name)
            initial_threads_list: List[Tuple[str, str]] = await initial_codebase_instance.get_list(load_type="threads")
            thread_state: Dict[str, dict] = await initial_codebase_instance.load_all_from_sqlite(load_type="threads")
            initial_thread: str = next(iter(thread_state.keys()))
            initial_chat_del_button = False
            if len(initial_threads_list)>1:
                initial_chat_del_button = True
            initial_convo: Dict[str, Any] = loads(thread_state[initial_thread]['content'])
            initial_code_list: List[Tuple[str, str]] = await initial_codebase_instance.get_list(load_type="code")
            initial_code_del_button = False
            if len(initial_code_list)>1:
                initial_code_del_button = True
            code_state: Dict[str, dict] = await initial_codebase_instance.load_all_from_sqlite(load_type="code")
            initial_code: str = next(iter(code_state.keys()))
            initial_code_name: str = code_state[initial_code]['source']
            initial_code_content: str = code_state[initial_code]['content']

            ## Get external codebases handler and initial selected codebase properties
            initial_external_codebases_instance: Codebases = self.users.selected_ext_codebases
            initial_external_codebase_del_button: bool = False
            if len(initial_external_docs_list_all)>1:
                initial_external_codebase_del_button = True
            initial_external_codebase: str | None = None
            initial_external_code_list: List[Tuple[str, str]] = []
            initial_external_docs_file: str | None = None
            initial_external_docs_file_content: str | None = None
            initial_external_codebase_files_del_button: bool = False
            if len(initial_external_docs_list_all)!=0:
                initial_external_codebase = initial_external_docs_list_all[0]
                initial_external_threads: Threads = initial_external_codebases_instance.get_current_codebase(initial_external_codebase)
                initial_external_code_list = await initial_external_threads.get_list(load_type="code")
                external_code_state: Dict[str, dict] = await initial_external_threads.load_all_from_sqlite(load_type="code")
                if external_code_state:
                    initial_external_codebase_files_del_button = True
                    initial_external_docs_file = next(iter(external_code_state.keys()))
                    initial_external_docs_file_content = external_code_state[initial_external_docs_file]['content']

            ## Define the initial states dict
            params_dict: Dict[str, Any] = {
                "initial_user_name": initial_user_name,
                "initial_del_button": initial_del_button,
                "initial_codebase_name": initial_codebase_name,
                "initial_codebase_list": initial_codebase_list,
                "initial_codebase_del_button": initial_codebase_del_button,
                "initial_thread": initial_thread, 
                "initial_threads_list": initial_threads_list, 
                "initial_chat_del_button": initial_chat_del_button,
                "initial_convo": initial_convo,
                "initial_code": initial_code, 
                "initial_code_list": initial_code_list, 
                "initial_code_del_button": initial_code_del_button,
                "initial_code_content": initial_code_content,
                "initial_external_codebase": initial_external_codebase, 
                "initial_external_docs_list_all": initial_external_docs_list_all, 
                "initial_external_code_list": initial_external_code_list,
                "initial_external_docs_file": initial_external_docs_file, 
                "initial_external_docs_file_content": initial_external_docs_file_content, 
                "initial_external_codebase_del_button": initial_external_codebase_del_button, 
                "initial_external_codebase_files_del_button": initial_external_codebase_files_del_button
            }
            logger.info(f'✅ Successfully created initial states.')

            ## Warm up the agent
            logger.info('⚙️ Warming up agent.')
            initial_user_instance.selected_agent.agent.invoke(
                {"messages": [{"role": "user", "content": "Hi."}]},
                config={"configurable": {"thread_id": initial_thread}}
            )
            logger.info(f'✅ Successfully warmed up agent.')
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating initial states: `{str(e)}`')
            raise

    def _create_dynamic_states(
        self, 
        initial_user_name: str, 
        initial_codebase_name: str, 
        initial_thread: str, 
        initial_code: str,
        initial_external_codebase: str, 
        initial_external_docs_file: str,
        initial_external_docs_list_all: List[str]
    ) -> Dict[str, State]:
        """
        Create the dynamic Gradio states.

        Returns
        ------------
            Dict[str, State]:
                A dictionary of dynamic states.
            
        Raises
        ------------
            Exception: 
                If creating the dynamic states fails, error is logged and raised.
        """
        logger.info('⚙️ Creating dynamic states')
        try:
            selected_user_state: State = State(initial_user_name)                           # Selected user
            selected_codebase_state: State = State(initial_codebase_name)                   # Selected codebase
            selected_thread_state: State = State(initial_thread)                            # Selected chat
            selected_code_state: State = State(initial_code)                                # Selected main codebase document
            selected_external_codebase_state: State = State(initial_external_codebase)      # Selected external codebase
            selected_external_docs_file_state: State = State(initial_external_docs_file)    # Selected external codebase document
            selected_external_docs_list_state: State = State(initial_external_docs_list_all)# Selected external codebases list
            params_dict: Dict[str, State] = {
                "selected_user_state": selected_user_state,
                "selected_codebase_state": selected_codebase_state,
                "selected_thread_state": selected_thread_state,
                "selected_code_state": selected_code_state,
                "selected_external_codebase_state": selected_external_codebase_state,
                "selected_external_docs_list_state": selected_external_docs_list_state,
                "selected_external_docs_file_state": selected_external_docs_file_state
            }
            logger.info(f'✅ Successfully created dynamic states')
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating dynamic states: `{str(e)}`')
            raise

    async def app(
        self
    ) -> Blocks:
        """
        Create the Gradio app.

        Returns
        ------------
            Blocks:
                The Gradio app.
            
        Raises
        ------------
            Exception: 
                If creating the Gradio app fails, error is logged and raised.
        """
        logger.info('⚙️ Creating Gradio app')
        try:
            with Blocks(analytics_enabled=False, theme=self.config.theme, css=self.config.custom_css) as demo:
                HTML("""
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/MaterialDesign-Webfont/7.2.96/css/materialdesignicons.min.css">
                """)
                HTML("""
                <h1 style='text-align: center'>
                    PyCoder 
                    <i class="mdi mdi-file-code-outline icon-color"></i>
                </h1>
                """)
                ## Create initial and dynamic states
                initial_states: Dict[str, Any] = await self._create_initial_states()
                dynamic_states: Dict[str, State] = self._create_dynamic_states(
                    initial_user_name=initial_states['initial_user_name'], 
                    initial_codebase_name=initial_states['initial_codebase_name'], 
                    initial_thread=initial_states['initial_thread'], 
                    initial_code=initial_states['initial_code'],
                    initial_external_codebase=initial_states['initial_external_codebase'], 
                    initial_external_docs_file=initial_states['initial_external_docs_file'],
                    initial_external_docs_list_all=initial_states['initial_external_docs_list_all']
                )

                ## Create all interfaces
                main_interface: MainInterface = MainInterface(users=self.users)
                user_interface: UserInterface = UserInterface(users=self.users)
                docs_interface: DocsInterface = DocsInterface(users=self.users)
                chat_interface: ChatInterface = ChatInterface(users=self.users)
                ext_docs_interface: ExtDocsInterface = ExtDocsInterface(users=self.users)
                main_int_comps: Dict[str, Any] = main_interface.create_interface(
                    initial_user_name=initial_states['initial_user_name'], 
                    initial_docs_name=initial_states['initial_codebase_name']
                )
                user_int_comps: Dict[str, Any] = user_interface.create_interface(
                    initial_del_button=initial_states['initial_del_button']
                )
                docs_int_comps: Dict[str, Any] = docs_interface.create_interface(
                    initial_docs_list=initial_states['initial_codebase_list'], 
                    initial_docs_del_button=initial_states['initial_codebase_del_button'],
                    initial_docs_name=initial_states['initial_codebase_name'], 
                    initial_doc_list=initial_states['initial_code_list'], 
                    initial_doc_del_button=initial_states['initial_code_del_button'],
                    initial_doc=initial_states['initial_code'], 
                    initial_doc_content=initial_states['initial_code_content']
                )
                chats_int_comps: Dict[str, Any] = chat_interface.create_interface(
                    initial_threads_list=initial_states['initial_threads_list'], 
                    initial_thread=initial_states['initial_thread'], 
                    initial_convo=initial_states['initial_convo'],
                    initial_code_list=initial_states['initial_code_list'], 
                    initial_code=initial_states['initial_code'], 
                    initial_code_content=initial_states['initial_code_content'],
                    initial_chat_del_button=initial_states['initial_chat_del_button']
                )
                ext_docs_int_comps: Dict[str, Any] = ext_docs_interface.create_interface(
                    initial_external_docs_list_all=initial_states['initial_external_docs_list_all'],
                    initial_external_codebase=initial_states['initial_external_codebase'],
                    initial_external_code_list=initial_states['initial_external_code_list'],
                    initial_external_docs_file=initial_states['initial_external_docs_file'],
                    initial_external_docs_file_content=initial_states['initial_external_docs_file_content'],
                    initial_external_codebase_del_button=initial_states['initial_external_codebase_del_button'],
                    initial_external_codebase_files_del_button=initial_states['initial_external_codebase_files_del_button']
                )

                ## Set all component triggers
                main_interface.component_triggers(        
                    selected_user_state=dynamic_states['selected_user_state'],
                    selected_codebase_state=dynamic_states['selected_codebase_state'],
                    selected_thread_state=dynamic_states['selected_thread_state'],
                    selected_code_state=dynamic_states['selected_code_state'],
                    selected_external_docs_list_state=dynamic_states['selected_external_docs_list_state'],
                    selected_external_codebase_state=dynamic_states['selected_external_codebase_state'],
                    selected_external_docs_file_state=dynamic_states['selected_external_docs_file_state'],
                    transcript=chats_int_comps['transcript'],
                    selected_user=main_int_comps['selected_user'],
                    selected_codebase=main_int_comps['selected_docs'],
                    codebase_radio=docs_int_comps['codebase_radio'],
                    delete_codebase_button=docs_int_comps['delete_codebase_button'],
                    delete_code_button=docs_int_comps['delete_code_button'],
                    files_radio=docs_int_comps['files_radio'],
                    codebase_details_files=chats_int_comps['codebase_details_files'],
                    thread_radio=chats_int_comps['thread_radio'],
                    delete_chat_button=chats_int_comps['delete_chat_button'],
                    selected_file_text=docs_int_comps['selected_file_text'],
                    codebase_details_file_content=chats_int_comps['codebase_details_file_content'],
                    external_codebases_checkbox=ext_docs_int_comps['ext_docs_checkbox'],
                    delete_external_docs_button=ext_docs_int_comps['delete_ext_docs_button'],
                    external_codebases_radio=ext_docs_int_comps['ext_docs_radio'],
                    external_docs_upload=ext_docs_int_comps['ext_docs_upload'],
                    external_codebases_files_radio=ext_docs_int_comps['ext_docs_files_radio'],
                    delete_external_code_button=ext_docs_int_comps['delete_ext_code_button'],
                    selected_external_doc_text=ext_docs_int_comps['selected_ext_doc_text'],
                    chat_row=chats_int_comps['chat_row'],
                    codebase_row=docs_int_comps['docs_row'],
                    external_codebase_row=ext_docs_int_comps['ext_docs_row'],
                    user_row=user_int_comps['user_row'],
                    start_user_button=main_int_comps['users_btn'], 
                    start_chat_button=main_int_comps['chats_btn'], 
                    start_codebase_button=main_int_comps['docs_btn'], 
                    start_external_docs_button=main_int_comps['ext_docs_btn']
                )
                user_interface.component_triggers(
                    selected_user_state=dynamic_states['selected_user_state'],
                    user_radio=user_int_comps['user_radio'],
                    delete_user_button=user_int_comps['delete_user_button'],
                    user_name_input=user_int_comps['user_name_input'],
                    confirm_delete_modal=user_int_comps['confirm_user_delete_modal'],
                    confirm_delete_text=user_int_comps['confirm_user_delete_text'],
                    confirm_delete_button=user_int_comps['confirm_user_delete_button'],
                    cancel_delete_button=user_int_comps['cancel_user_delete_button'],
                    status_messages=main_int_comps['status_bar']
                )        
                docs_interface.component_triggers(
                    selected_user_state=dynamic_states['selected_user_state'],
                    selected_codebase_state=dynamic_states['selected_codebase_state'],
                    selected_external_docs_list_state=dynamic_states['selected_external_docs_list_state'],
                    selected_thread_state=dynamic_states['selected_thread_state'],
                    selected_code_state=dynamic_states['selected_code_state'],
                    codebase_radio=docs_int_comps['codebase_radio'],
                    codebase_name_input=docs_int_comps['codebase_name_input'],
                    delete_codebase_button=docs_int_comps['delete_codebase_button'],
                    files_upload=docs_int_comps['files_upload'],
                    files_radio=docs_int_comps['files_radio'],
                    delete_code_button=docs_int_comps['delete_code_button'],
                    confirm_delete_modal=docs_int_comps['confirm_codebase_delete_modal'],
                    confirm_delete_text=docs_int_comps['confirm_codebase_delete_text'],
                    confirm_delete_button=docs_int_comps['confirm_codebase_delete_button'],
                    cancel_delete_button=docs_int_comps['cancel_codebase_delete_button'],
                    confirm_code_delete_modal=docs_int_comps['confirm_code_delete_modal'],
                    confirm_code_delete_text=docs_int_comps['confirm_code_delete_text'],
                    confirm_code_delete_button=docs_int_comps['confirm_code_delete_button'],
                    cancel_code_delete_button=docs_int_comps['cancel_code_delete_button'],
                    status_messages=main_int_comps['status_bar']
                )
                chat_interface.component_triggers(
                    selected_user_state=dynamic_states['selected_user_state'],
                    selected_codebase_state=dynamic_states['selected_codebase_state'],
                    selected_external_docs_list_state=dynamic_states['selected_external_docs_list_state'],
                    selected_thread_state=dynamic_states['selected_thread_state'],
                    selected_code_state=dynamic_states['selected_code_state'],
                    transcript=chats_int_comps['transcript'],
                    user_input=chats_int_comps['user_input'],
                    codebase_details_files=chats_int_comps['codebase_details_files'],
                    new_thread_name_input=chats_int_comps['new_thread_name_input'],
                    thread_radio=chats_int_comps['thread_radio'],
                    delete_chat_button=chats_int_comps['delete_chat_button'],
                    confirm_delete_modal=chats_int_comps['confirm_chat_delete_modal'],
                    confirm_delete_text=chats_int_comps['confirm_chat_delete_text'],
                    confirm_delete_button=chats_int_comps['confirm_chat_delete_button'],
                    cancel_delete_button=chats_int_comps['cancel_chat_delete_button'],
                    status_messages=main_int_comps['status_bar']
                )
                ext_docs_interface.component_triggers(
                    selected_user_state=dynamic_states['selected_user_state'],
                    selected_codebase_state=dynamic_states['selected_codebase_state'],
                    external_docs_name_input=ext_docs_int_comps['ext_docs_name_input'],
                    selected_external_docs_list_state=dynamic_states['selected_external_docs_list_state'],
                    selected_external_codebase_state=dynamic_states['selected_external_codebase_state'],
                    external_codebases_checkbox=ext_docs_int_comps['ext_docs_checkbox'],
                    external_codebases_radio=ext_docs_int_comps['ext_docs_radio'],
                    external_docs_upload=ext_docs_int_comps['ext_docs_upload'],
                    delete_external_docs_button=ext_docs_int_comps['delete_ext_docs_button'],
                    external_codebases_files_radio=ext_docs_int_comps['ext_docs_files_radio'],
                    selected_external_docs_file_state=dynamic_states['selected_external_docs_file_state'],
                    delete_external_code_button=ext_docs_int_comps['delete_ext_code_button'],
                    confirm_delete_modal=ext_docs_int_comps['confirm_ext_docs_delete_modal'],
                    confirm_delete_text=ext_docs_int_comps['confirm_ext_docs_delete_text'],
                    confirm_delete_button=ext_docs_int_comps['confirm_ext_docs_delete_button'],
                    cancel_delete_button=ext_docs_int_comps['cancel_ext_docs_delete_button'],
                    confirm_code_delete_modal=ext_docs_int_comps['confirm_ext_code_delete_modal'],
                    confirm_code_delete_text=ext_docs_int_comps['confirm_ext_code_delete_text'],
                    confirm_code_delete_button=ext_docs_int_comps['confirm_ext_code_delete_button'],
                    cancel_code_delete_button=ext_docs_int_comps['cancel_ext_code_delete_button'],
                    status_messages=main_int_comps['status_bar']
                )
            logger.info(f'✅ Successfully created Gradio app')
            return demo
        except Exception as e:
            logger.error(f'❌ Problem creating Gradio app: `{str(e)}`')
            raise