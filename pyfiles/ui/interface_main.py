### pyfiles.ui.interface_main
## This file creates the main interface for the Gradio app.
## Gradio components for the different interfaces and component triggers for handling changes are created.

## External imports
from gradio import (
    Button, 
    Radio, 
    Textbox, 
    Button, 
    CheckboxGroup, 
    File, 
    Row, 
    Column, 
    State, 
    Tab,
    Chatbot,
    HTML,
    Markdown
)
from typing import (
    Dict, 
    Any, 
    List, 
    Tuple
)

## Internal imports
from pyfiles.bases.logger import logger
from pyfiles.bases.threads import Threads
from pyfiles.bases.users import Users
from pyfiles.ui import utils

## Create the main interface handler
class MainInterface:
    """
    A class to create a main interface handler.
    This creates the Gradio app components and component triggers for the main interface.

    Attributes
    ------------
        users: Users
                The users handler.
    """
    def __init__(
        self, 
        users: Users | None
    ):
        """
        Initialize the main interface handler.

        Args
        ------------
            users: Users
                The users handler.
            
        Raises
        ------------
            Exception: 
                If initializing the main interface fails, error is logged and raised.
        """
        try:
            self.users = users
        except Exception as e:
            logger.error(f'❌ Problem creating main interface: `{str(e)}`')

    async def _handle_user_change(
        self, 
        user_name: str, 
        docs_name: str
    ) -> Tuple[str, str, str, Radio, Button, Radio, Button, CheckboxGroup]:
        """
        Handle the change of the selected user.

        Args
        ------------
            user_name: str
                The selected user name.
            docs_name: str
                The user's selected codebase name.

        Returns
        ------------
            Tuple[str, str, str, Radio, Button, Radio, Button, CheckboxGroup]:
                A tuple defining the properties for Gradio components given the newly selected user.
            
        Raises
        ------------
            Exception: 
                If handling the user change fails, error is logged and raised.
        """
        try:
            if self.users != None:
                ## Get the appropriate details for the selected user
                (
                    name, 
                    selected_codebase, 
                    choices, 
                    external_choices, 
                    external_choice
                ) = await self.users.get_user_state_details(user_name, docs_name)
                ## Check if delete button needs to be toggled off
                del_docs_button: Button = utils.toggle_del_button(choices)
                if not external_choices:
                    del_ext_docs_button: Button = Button(interactive=False)
                else:
                    del_ext_docs_button = utils.toggle_del_button(external_choices)
                return (
                    name,                           # Selected user name Textbox
                    selected_codebase,              # Selected codebase name Textbox
                    selected_codebase,              # Selected codebase name State
                    Radio(                          # User Radio
                        choices=choices, 
                        value=choices[0]
                    ), 
                    del_docs_button,                # Delete main codebases Button
                    Radio(                          # Main codebases Radio
                        choices=external_choices, 
                        value=external_choice
                    ), 
                    del_ext_docs_button,            # Delete external codebases Button
                    CheckboxGroup(                  # External codebases CheckboxGroup
                        choices=external_choices, 
                        value=external_choices
                    )
                )
            else:
                message = f'❌ Attribute `users` should not be None.'
                raise ValueError(message)
        except Exception as e:
            logger.error(f'❌ Problem handling the user change: `{str(e)}`')
            raise

    async def _handle_docs_change(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str]
    ) -> Tuple[str, str | None, str | None, Radio, Radio, Radio, Button, Button]:
        """
        Handle the change of the selected codebase.

        Args
        ------------
            user_name: str
                The selected user name.
            docs_name: str
                The user's selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.

        Returns
        ------------
            Tuple[str, str, str, Radio, Radio, Radio]:
                A tuple defining the properties for Gradio components given the newly selected codebase.
            
        Raises
        ------------
            Exception: 
                If handling the codebase change fails, error is logged and raised.
        """
        try:
            ## Get the current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get the properties for the newly selected codebase
            (
                codebase_type,      # The codebase type (`user` or `external`)
                selected_codebase,  # The threads handler for the selected codebase
                name                # The selected codebase name
            ) = await user.get_codebase_state_details(docs_name)
            
            ## Get the chat and code properties for the selected codebase
            thread_id: str | None = None 
            code_id: str | None = None
            if selected_codebase:
                thread_choices: List[Tuple[str, str]] = await selected_codebase.get_list(load_type="threads")
                if thread_choices:
                    thread_id = thread_choices[0][1] 
                code_choices: List[Tuple[str, str]] = await selected_codebase.get_list(load_type="code")
                if code_choices:
                    code_id = code_choices[0][1]
            del_chat_button: Button = utils.toggle_del_button(thread_choices)
            del_code_button: Button = utils.toggle_del_button(code_choices)
            thread_radio: Radio = Radio(choices=thread_choices, value=thread_id)
            files_radio: Radio = Radio(choices=code_choices, value=code_id)
            return (
                name,           # The selected codebase name Textbox
                thread_id,      # The selected chat State
                code_id,        # The selected code State
                thread_radio,   # The chat Radio
                files_radio,    # The doc Radio for the Docs interface
                files_radio,    # The doc Radio for the Chats interface
                del_chat_button,# The delete chat Button
                del_code_button,# The delete code Button
            )
        except Exception as e:
            logger.error(f'❌ Problem handling the codebase change: `{str(e)}`')
            raise

    async def _handle_chat_change(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_id: str
    ) -> str:
        """
        Handle the change of the selected chat.

        Args
        ------------
            user_name: str
                The selected user name.
            docs_name: str
                The user's selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_id: str
                The ID of the selected chat.

        Returns
        ------------
            Tuple[str, str]:
                A tuple defining the properties for Gradio components given the newly selected chat.
            
        Raises
        ------------
            Exception: 
                If handling the chat change fails, error is logged and raised.
        """
        try:
            ## Get the current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get the threads handler for the current user and selected codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Get the thread content
            results: str = await docs.get_state_details(load_type="threads", thread_id=chat_id)
            return results  # Transcript for Chatbot
        except Exception as e:
            logger.error(f'❌ Problem handling the chat change: `{str(e)}`')
            raise

    async def _handle_doc_change(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        doc_id: str
    ) -> Tuple[str, str]:
        """
        Handle the change of the selected code from the user's selected main codebase.

        Args
        ------------
            user_name: str
                The selected user name.
            docs_name: str
                The user's selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            doc_id: str
                The ID of the selected code.

        Returns
        ------------
            Tuple[str, str]:
                A tuple defining the properties for Gradio components given the newly selected code.
            
        Raises
        ------------
            Exception: 
                If handling the code change fails, error is logged and raised.
        """
        try:
            ## Get the current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get the threads handler for the user's main codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Get the selected code details
            results: str = await docs.get_state_details(load_type="code", thread_id=doc_id)
            return (
                results,    # Code content Mardown in Docs interface
                results     # Code content Markdown in Chat interface
            )
        except Exception as e:
            logger.error(f'❌ Problem handling the code change: `{str(e)}`')
            raise

    async def _handle_ext_docs_change(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        ext_docs_name: str
    ) -> Tuple[str | None, Radio, Button, File]:
        """
        Handle the change of the selected external codebase for dispaly.

        Args
        ------------
            user_name: str
                The selected user name.
            docs_name: str
                The user's selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            ext_docs_name: str
                The name of the selected external codebase.

        Returns
        ------------
            Tuple[str, Radio, Button, File]:
                A tuple defining the properties for Gradio components given the newly selected codebase.
            
        Raises
        ------------
            Exception: 
                If handling the external codebase change fails, error is logged and raised.
        """
        try:
            ## Get current user
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get selected external codebase properties
            (
                codebase_type,      # The codebase type (`user` or `external`)
                selected_codebase,  # The threads handler for the selected codebase
                name                # The selected codebase name
            ) = await ext_docs.get_codebase_state_details(ext_docs_name)

            ## Define Gradio component properties for newly selected external codebase
            del_button: Button = Button(interactive=False)
            files_upload: File = File(interactive=False) 
            code_choices: List[Tuple[str, str]] | None = None
            code_id: str | None = None
            if selected_codebase:
                code_choices = await selected_codebase.get_list(load_type="code")
                files_upload = File(interactive=True)
                if code_choices:
                    code_id = code_choices[0][1]
                    del_button = Button(interactive=False) if len(code_choices)<=1 else Button(interactive=True)
            files_radio: Radio = Radio(choices=code_choices, value=code_id)
            return (
                code_id,        # The selected external code State
                files_radio,    # The external codes Radio
                del_button,     # The external codes delete Button
                files_upload    # The external codes File handler
            )
        except Exception as e:
            logger.error(f'❌ Problem handling the selected external codebase change: `{str(e)}`')
            raise

    async def _handle_ext_doc_change(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        ext_docs_name: str, 
        doc_id: str
    ) -> str:
        """
        Handle the change of the selected code from the user's selected external codebase.

        Args
        ------------
            user_name: str
                The selected user name.
            docs_name: str
                The user's selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            ext_docs_name: str
                The name of the selected external codebase.
            doc_id: str
                The ID of the selected code.

        Returns
        ------------
            str:
                The string content of the newly selected code.
            
        Raises
        ------------
            Exception: 
                If handling the code change fails, error is logged and raised.
        """
        try:
            ## Get the current user
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get the threads handler for the selected external codebaes
            docs: Threads = ext_docs.get_current_codebase(ext_docs_name)
            if docs!=None:
                results: str = await docs.get_state_details(load_type="code", thread_id=doc_id)
                return results  # The selected external code Markdown
            else:
                return ''
        except Exception as e:
            logger.error(f'❌ Problem handling the selected external code change: `{str(e)}`')
            raise

    def component_triggers(
        self,
        selected_user_state: State,
        selected_codebase_state: State,
        selected_thread_state: State,
        selected_code_state: State,
        selected_external_docs_list_state: State,
        selected_external_codebase_state: State,
        selected_external_docs_file_state: State,
        transcript: Chatbot,
        selected_user: str,
        selected_codebase: str,
        codebase_radio: Radio,
        delete_codebase_button: Button,
        delete_code_button: Button,
        files_radio: Radio,
        codebase_details_files: File,
        thread_radio: Radio,
        delete_chat_button: Button,
        selected_file_text: str,
        codebase_details_file_content: str,
        external_codebases_checkbox: CheckboxGroup,
        delete_external_docs_button: Button,
        external_codebases_radio: Radio,
        external_docs_upload: File,
        external_codebases_files_radio: Radio,
        delete_external_code_button: Button,
        selected_external_doc_text: str,
        chat_row: Row,
        codebase_row: Row,
        external_codebase_row: Row,
        user_row: Row,
        start_user_button: Tab, 
        start_chat_button: Tab, 
        start_codebase_button: Tab, 
        start_external_docs_button: Tab
    ) -> None:
        """
        Create the component triggers for all components of the main interface.

        Args
        ------------
            selected_user_state: State
                The selected user state.
            selected_codebase_state: State
                The selected main codebase state.
            selected_thread_state: State
                The selected chat state.
            selected_code_state: State
                The selected main code state.
            selected_external_docs_list_state: State
                The selected external codebases list.
            selected_external_codebase_state: State
                The selected external codebase.
            selected_external_docs_file_state: State
                The selected external code.
            transcript: Chatbot
                The Chatbot component.
            selected_user: str
                The selected user Textbox.
            selected_codebase: str
                The selected codebase Textbox.
            codebase_radio: Radio
                The main codebase radio.
            delete_codebase_button: Button
                The main delete codebase button.
            delete_code_button: Button
                The main delete code button.
            files_radio: Radio
                The main codebase files radio.
            codebase_details_files: File
                The main codebase upload.
            thread_radio: Radio
                The chat radio.
            delete_chat_button: Button
                The chat delete button.
            selected_file_text: str
                The selected code content for the Docs interface.
            codebase_details_file_content: str
                The selected code content for the Chat interface.
            external_codebases_checkbox: CheckboxGroup
                The external codebases checkbox group.
            delete_external_docs_button: Button
                The external codebases delete button.
            external_codebases_radio: Radio
                The external codebases radio.
            external_docs_upload: File
                The external codebases file upload.
            external_codebases_files_radio: Radio
                The external codebases radio.
            delete_external_code_button: Button
                The external code delete button.
            selected_external_doc_text: str
                The selected external code content.
            chat_row: Row
                The chat interface row.
            codebase_row: Row
                The codebase interface row.
            external_codebase_row: Row
                The external codebases interface row.
            user_row: Row
                The user interface row.
            start_user_button: Tab
                The user interface tab.
            start_chat_button: Tab 
                The chat interface tab.
            start_codebase_button: Tab
                The codebase interface tab.
            start_external_docs_button: Tab
                The external codebase interface tab.
            
        Raises
        ------------
            Exception: 
                If creating the component triggers fails, error is logged and raised.
        """
        try:
            _handle_user_change_mapping: Dict[str, Dict[str, Any]] = {
                "in": {                                                         ## In
                    "user_name": selected_user_state,                           # Selected user State
                    "docs_name": selected_codebase_state                        # Selected codebase State
                },
                "out": {                                                        ## Out
                    "selected_user": selected_user,                             # Selected user Textbox
                    "selected_codebase": selected_codebase,                     # Selected codebase Textbox
                    "selected_codebase_state": selected_codebase_state,         # Selected codebase State
                    "codebase_radio": codebase_radio,                           # Codebase Radio 
                    "delete_codebase_button": delete_codebase_button,           # Delete codebase Button
                    "external_codebases_radio": external_codebases_radio,       # External codebase Radio
                    "delete_external_docs_button": delete_external_docs_button, # Delete external codebase Button
                    "external_codebases_checkbox": external_codebases_checkbox  # External codebase CheckboxGroup
                }
            }
            selected_user_state.change(
                self._handle_user_change,
                inputs=list(_handle_user_change_mapping['in'].values()),
                outputs=list(_handle_user_change_mapping['out'].values())
            )

            _handle_docs_change_mapping: Dict[str, Dict[str, Any]] = {
                "in": {                                                         ## In
                    "user_name": selected_user_state,                           # Selected user State
                    "docs_name": selected_codebase_state,                       # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state          # Selected external codebases list State
                },  
                "out": {                                                        ## Out
                    "selected_codebase": selected_codebase,                     # Selected codebase Textbox
                    "selected_thread_state": selected_thread_state,             # Selected thread State
                    "selected_code_state": selected_code_state,                 # Selected code State
                    "thread_radio": thread_radio,                               # Thread Radio
                    "files_radio": files_radio,                                 # Docs interface code Radio
                    "codebase_details_files": codebase_details_files,           # Chat interface code Radio
                    "delete_chat_button": delete_chat_button,                   # Delete chat Button
                    "delete_code_button": delete_code_button                    # Delete code Button
                }
            }
            selected_codebase_state.change(
                self._handle_docs_change,
                inputs=list(_handle_docs_change_mapping['in'].values()),
                outputs=list(_handle_docs_change_mapping['out'].values())
            )

            _handle_chat_change_mapping: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "user_name": selected_user_state,                   # Selected user State
                    "docs_name": selected_codebase_state,               # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state, # Selected external codebases list State
                    "chat_id": selected_thread_state                    # Selected chat state
                },
                "out": {                                                ## Out
                    "transcript": transcript                            # Chatbot
                }
            }
            selected_thread_state.change(
                self._handle_chat_change,
                inputs=list(_handle_chat_change_mapping['in'].values()),
                outputs=list(_handle_chat_change_mapping['out'].values())
            )

            _handle_doc_change_mapping: Dict[str, Dict[str, Any]] = {
                "in": {                                                             ## In
                    "user_name": selected_user_state,                               # Selected user State       
                    "docs_name": selected_codebase_state,                           # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,             # Selected external codebases list State
                    "doc_id": selected_code_state                                   # Selected code State
                },
                "out": {                                                            ## Out
                    "selected_file_text": selected_file_text,                       # Selected code Markdown for Docs interface
                    "codebase_details_file_content": codebase_details_file_content  # Selected code Markdown for Chat interface
                }
            }
            selected_code_state.change(
                self._handle_doc_change,
                inputs=list(_handle_doc_change_mapping['in'].values()),
                outputs=list(_handle_doc_change_mapping['out'].values())
            )

            _handle_ext_docs_change_mapping: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "user_name": selected_user_state,                                       # Selected user State
                    "docs_name": selected_codebase_state,                                   # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,                     # Selected external codebases list State
                    "ext_docs_name": selected_external_codebase_state                       # Selected external codebase State
                },
                "out": {                                                                    ## Out
                    "selected_external_docs_file_state": selected_external_docs_file_state, # Selected external code State
                    "external_codebases_files_radio": external_codebases_files_radio,       # External codebases Radio
                    "delete_external_code_button": delete_external_code_button,             # Delete external code Button
                    "external_docs_upload": external_docs_upload                            # External code File upload
                }
            }
            selected_external_codebase_state.change(
                self._handle_ext_docs_change,
                inputs=list(_handle_ext_docs_change_mapping['in'].values()),
                outputs=list(_handle_ext_docs_change_mapping['out'].values())
            )

            _handle_ext_doc_change_mapping: Dict[str, Dict[str, Any]] = {
                "in": {                                                         ## In
                    "user_name": selected_user_state,                           # Selected user State
                    "docs_name": selected_codebase_state,                       # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,         # Selected external codebase list State
                    "ext_docs_name": selected_external_codebase_state,          # Selected external codebase State
                    "doc_id": selected_external_docs_file_state                 # Selected external code State
                },
                "out": {                                                        ## Out
                    "selected_external_doc_text": selected_external_doc_text    # Selected external code Markdown
                }
            }
            selected_external_docs_file_state.change(
                self._handle_ext_doc_change,
                inputs=list(_handle_ext_doc_change_mapping['in'].values()),
                outputs=list(_handle_ext_doc_change_mapping['out'].values())
            )

            start_user_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                },                                                  # None
                "out": {                                            ## Out
                    "chat_row": chat_row,                           # Chat interface
                    "codebase_row": codebase_row,                   # Docs interface
                    "external_codebase_row": external_codebase_row, # Ext Docs interface
                    "user_row": user_row                            # User interface
                }
            }
            start_user_button.select(
                utils.toggle_visibility,
                inputs=list(start_user_button_click['in'].values()),
                outputs=list(start_user_button_click['out'].values())
            )

            start_codebase_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                },                                                  # None
                "out": {                                            ## Out
                    "user_row": user_row,                           # User interface
                    "chat_row": chat_row,                           # Chat interface
                    "external_codebase_row": external_codebase_row, # Ext Docs interface
                    "codebase_row": codebase_row                    # Docs interface
                }
            }
            start_codebase_button.select(
                utils.toggle_visibility,
                inputs=list(start_codebase_button_click['in'].values()),
                outputs=list(start_codebase_button_click['out'].values())
            )

            start_chat_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                },                                                  # None
                "out": {                                            ## Out
                    "user_row": user_row,                           # User interface
                    "codebase_row": codebase_row,                   # Docs interface
                    "external_codebase_row": external_codebase_row, # Ext Docs interface
                    "chat_row": chat_row                            # Chat interface
                }
            }
            start_chat_button.select(
                utils.toggle_visibility,
                inputs=list(start_chat_button_click['in'].values()),
                outputs=list(start_chat_button_click['out'].values())
            )

            start_external_docs_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                },                                                  # None
                "out": {                                            ## Out
                    "user_row": user_row,                           # User interface
                    "codebase_row": codebase_row,                   # Docs interface
                    "chat_row": chat_row,                           # Chat interface
                    "external_codebase_row": external_codebase_row  # Ext Docs interface
                }
            }
            start_external_docs_button.select(
                utils.toggle_visibility,
                inputs=list(start_external_docs_button_click['in'].values()),
                outputs=list(start_external_docs_button_click['out'].values())
            )

        except Exception as e:
            logger.error(f'❌ Problem setting component triggers for main interface: `{str(e)}`')
            raise

    def create_interface(
        self, 
        initial_user_name: str, 
        initial_docs_name: str
    ) -> Dict[str, Any]:
        """
        Create the main interface.

        Args
        ------------
            initial_user_name: str
                The initially selected user name.
            initial_docs_name: str
                The initially selected codebase name.
            
        Returns
        ------------
            Dict[str, Dict[str, Any]]:
                A dictionary of main interface components to pass to the main app.
            
        Raises
        ------------
            Exception: 
                If creating the main interface fails, error is logged and raised.
        """
        try:
            main_interface_config: Dict[str, Dict[str, Any]] = {
                "status_bar": { ## Status messages Textbox
                    "component_type": Markdown, 
                    "value": "Welcome!",
                    "container": True
                },
                "selected_user": {  ## Selected user Textbox
                    "component_type": Textbox, 
                    "value": initial_user_name, 
                    "interactive": False, 
                    "label": "Selected User", 
                    "scale": 2
                },
                "selected_docs": {  ## Selected codebase Textbox
                    "component_type": Textbox, 
                    "value": initial_docs_name, 
                    "interactive": False, 
                    "label": "Selected Docs", 
                    "scale": 2
                },
                "users_btn": {  ## Select user interface Tab
                    "component_type": Tab, 
                    "label": 'Users'
                },
                "docs_btn": {   ## Selected docs interface Tab
                    "component_type": Tab,  
                    "label": 'Docs', 
                },
                "chats_btn": {  ## Select chat interface Tab
                    "component_type": Tab, 
                    "label": 'Chats', 
                },
                "ext_docs_btn": {   ## Select external docs interface Tab
                    "component_type": Tab, 
                    "label": 'External Docs', 
                }
            }
            params_dict: Dict[str, Dict[str, Any]] = {}
            with Row(equal_height=True) as main_row:
                params_dict['main_row'] = main_row
                with Column():
                    HTML("""
                    <p style='text-align: center'> 
                        <i class="mdi mdi-creation-outline icon-color"></i> 
                        Create user profiles, upload Python and Markdown files to create codebases, chat with an agent about your files
                        <i class="mdi mdi-creation-outline icon-color"></i> 
                    </p>
                    """)
                    with Row(equal_height=True):
                        params_dict['status_bar'] = utils.create_component(main_interface_config['status_bar'])
                        params_dict['selected_user'] = utils.create_component(main_interface_config['selected_user'])
                        params_dict['selected_docs'] = utils.create_component(main_interface_config['selected_docs'])
                    with Row():
                        params_dict['users_btn'] = utils.create_component(main_interface_config['users_btn'])
                        params_dict['docs_btn'] = utils.create_component(main_interface_config['docs_btn'])
                        params_dict['chats_btn'] = utils.create_component(main_interface_config['chats_btn'])
                        params_dict['ext_docs_btn'] = utils.create_component(main_interface_config['ext_docs_btn'])
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating main interface: `{str(e)}`')
            raise