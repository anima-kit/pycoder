### pyfiles.ui.interface_chat
## This file creates the chat interface for the Gradio app.
## Gradio components and component triggers are created for chat management.

## External imports
from gradio import (
    Chatbot, 
    Markdown, 
    Progress, 
    Button, 
    Radio, 
    File, 
    Row, 
    Column, 
    Textbox, 
    State, 
    Accordion, 
    Tab, 
    EditData
)
from gradio_modal import Modal # type: ignore 
from langchain_core.messages import BaseMessage
from typing import (
    Dict, 
    List, 
    Tuple, 
    AsyncIterator,
    Any
)

## Internal imports
from pyfiles.agents.agent import Agent
from pyfiles.bases.logger import logger
from pyfiles.bases.threads import Threads
from pyfiles.bases.users import Users
from pyfiles.ui import utils

## Create the chat interface handler
class ChatInterface:
    """
    A class to create a chat interface handler.
    This creates the Gradio app components and component triggers for the chat interface.

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
        Initialize the chat interface handler.

        Args
        ------------
            users: Users
                The users handler.
            
        Raises
        ------------
            Exception: 
                If initializing the chat interface fails, error is logged and raised.
        """
        try:
            self.users = users
        except Exception as e:
            logger.error(f'❌ Problem creating chat interface: `{str(e)}`')
            raise

    async def _confirm_deletion_modal(
        self, 
        selected_chat: str, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str]
    ) -> Tuple[Modal, Markdown]:
        """
        Create the confirm deletion modal for chat deletion.

        Args
        ------------
            selected_chat: str
                The chat to delete.
            user_name: str
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.

        Returns
        ------------
            Tuple[Modal, Markdown]:
                A tuple of the confirm deletion modal and the message for confirmation.
            
        Raises
        ------------
            Exception: 
                If creating the deletion modal fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected codebase
            docs = user.get_current_codebase(docs_name)
            ## Get list of threads
            chats = await docs.get_list("threads")
            ## Get chat name
            for key, value in chats:
                if value==selected_chat:
                    file_name = key
            message = f"⚠️ Are you sure you want to delete chat `{file_name}`?"
            return (
                Modal(visible=True),
                Markdown(value=message)
            )
        except Exception as e:
            logger.error(f'❌ Problem creating confirm deletion modal: `{str(e)}`')
            raise

    
    async def _handle_create_chat_submit(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_name: str
    ) -> Tuple[Radio, str, Button, str, str]:
        """
        Handle the creation of a new chat thread.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_name: str
                The name of the chat thread to create.
        
        Returns
        ------------
            Tuple[Radio, str, Button, str, str]:
                A tuple of the UI properties for the newly selected chat after creation.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new chat fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Create the new chat thread
            choices, thread_id, _, status_message = await docs.create("threads", name=chat_name)
            ## Update chat delete button and radio
            del_button: Button = utils.toggle_del_button(choices)
            thread_radio: Radio = Radio(choices=choices, value=thread_id)
            return (
                thread_radio,   # Chat Radio
                thread_id,      # Selected chat State
                del_button,     # Chat delete Button
                '',             # Chat name input Textbox
                status_message  # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling chat creation: `{str(e)}`')
            raise

    async def _handle_delete_chat_click(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_id: str, 
        progress: Progress = Progress()
    ) -> Tuple[Radio, str | None, Button, Modal, str]:
        """
        Handle the delete of a selected chat thread.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_id: str
                The name of the chat thread to create.
            progress (Optional): Progress
                The progress bar.
        
        Returns
        ------------
            Tuple[Radio, str | None, Button, Modal, str]:
                A tuple of the UI properties for the newly selected chat after deletion.
            
        Raises
        ------------
            Exception: 
                If handling the deletion of a selected chat fails, error is logged and raised.
        """
        try:
            progress(0, desc=f'⚙️ Deleting "{chat_id}"')
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Delete the selected chat
            choices, next_selected, status_message = await docs.delete("threads", chat_id)
            ## Update delete button and radio
            thread_radio: Radio = Radio(
                choices=choices,
                value=next_selected,
            )
            del_button: Button = utils.toggle_del_button(choices)
            return (
                thread_radio,           # Chat Radio
                next_selected,          # Selected chat State
                del_button,             # Chat delete Button
                Modal(visible=False),   # Confirm deletion Modal
                status_message          # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling chat deletion: `{str(e)}`')
            raise

    async def _handle_chat_input_submit(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_id: str,
        chat_input: str
    ) -> AsyncIterator[Tuple[List[Dict[str, Any]], str]]:
        """
        Handle the triggering of the `main` chat mode.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_id: str
                The name of the chat thread to create.
            chat_input: str
                The input message.
        
        Returns
        ------------
            AsyncIterator[Tuple[List[Dict[str, Any]], str]]:
                A tuple for the agent response and the new chat input submission text.
            
        Raises
        ------------
            Exception: 
                If handling the submission of a `main` mode chat fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get current agent for selected codebase
            agent: Agent = user.get_current_agent(docs_name)
            ## Get agent response
            async for response in agent.aget_agent_response(chat_input, chat_id):
                yield (
                    response,   # Chatbot
                    ''          # User chat input Textbox
                )
        except Exception as e:
            logger.error(f'❌ Problem handling `main` chat mode submission: `{str(e)}`')
            raise

    async def _handle_chat_undo_submit(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_id: str, 
        chat_input: str
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Handle the triggering of the `undo` chat mode.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_id: str
                The name of the chat thread to create.
            chat_input: str
                The input message (will be empty).
        
        Returns
        ------------
            AsyncIterator[List[Dict[str, Any]]]:
                The agent response.
            
        Raises
        ------------
            Exception: 
                If handling the submission of an `undo` mode chat fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get current agent for selected codebase
            agent: Agent = user.get_current_agent(docs_name)
            ## Get agent resposne
            async for response in agent.aget_agent_response(chat_input, chat_id, mode="undo"):
                yield response  # Chatbot
        except Exception as e:
            logger.error(f'❌ Problem handling `undo` chat mode submission: `{str(e)}`')
            raise

    async def _handle_chat_retry_submit(
        self,
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_id: str, 
        chat_input: str
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Handle the triggering of the `retry` chat mode.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_id: str
                The name of the chat thread to create.
            chat_input: str
                The input message (will be empty).
        
        Returns
        ------------
            AsyncIterator[List[Dict[str, Any]]]:
                The agent response.
            
        Raises
        ------------
            Exception: 
                If handling the submission of a `retry` mode chat fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get current agent for selected codebase
            agent: Agent = user.get_current_agent(docs_name)
            ## Get agent response
            async for response in agent.aget_agent_response(chat_input, chat_id, mode="retry"):
                yield response  # Chatbot
        except Exception as e:
            logger.error(f'❌ Problem handling `retry` chat mode submission: `{str(e)}`')
            raise

    async def _handle_chat_edit_submit(
        self,
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        chat_id: str, 
        chat_input: str,
        edit_data: EditData
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Handle the triggering of the `edit` chat mode.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            chat_id: str
                The name of the chat thread to create.
            chat_input: str
                The input message (will be empty).
            edit_data: EditData
                The value and index of the edited message.
        
        Returns
        ------------
            AsyncIterator[List[Dict[str, Any]]]:
                The agent response.
            
        Raises
        ------------
            Exception: 
                If handling the submission of an `edit` mode chat fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get current agent for selected codebase
            agent: Agent = user.get_current_agent(docs_name)
            ## Get agent response
            async for response in agent.aget_agent_response(chat_input, chat_id, mode="edit", edit_data=edit_data):
                yield response  # Chatbot
        except Exception as e:
            logger.error(f'❌ Problem handling `edit` chat mode submission: `{str(e)}`')
            raise

    def component_triggers(
        self,
        selected_user_state: State,
        selected_codebase_state: State,
        selected_external_docs_list_state: State,
        selected_thread_state: State,
        selected_code_state: State,
        transcript: Chatbot,
        user_input: Textbox,
        codebase_details_files: File,
        new_thread_name_input: Textbox, 
        thread_radio: Radio,
        delete_chat_button: Button,
        confirm_delete_modal: Modal,
        confirm_delete_text: str,
        confirm_delete_button: Button,
        cancel_delete_button: Button,
        status_messages: str
    ) -> None:
        """
        Create the component triggers for all components of the chat interface.

        Args
        ------------
            selected_user_state: State
                The selected user state.
            selected_codebase_state: State
                The selected main codebase state.
            selected_external_docs_list_state: State
                The selected external codebases list.
            selected_thread_state: State
                The selected chat state.
            selected_code_state: State
                The selected main code state.
            transcript: Chatbot
                The Chatbot component.
            user_input: Textbox.
                The user message input.
            codebase_details_files: File
                The main codebase upload.
            new_thread_name_input: Textbox.
                The new thread name input.
            thread_radio: Radio
                The chat radio.
            confirm_delete_modal: Modal
                The confirm deletion modal.
            confirm_delete_text: str
                The confirm deletion text.
            confirm_delete_button: Button
                The confirm deletion button.
            cancel_delete_button: Button
                The cancel deletion button.
            status_messages: str
                The status messages.
            
        Raises
        ------------
            Exception: 
                If creating the component triggers fails, error is logged and raised.
        """
        try:
            thread_radio_change: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                    "thread_radio": thread_radio                    # Chat Radio
                },
                "out": {                                            ## Out
                    "selected_thread_state": selected_thread_state  # Selected thread State
                }
            }
            thread_radio.change(
                lambda x: x,
                inputs=list(thread_radio_change['in'].values()),
                outputs=list(thread_radio_change['out'].values())
            )

            codebase_details_files_change: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "codebase_details_files": codebase_details_files    # Code Radio for selected codebase
                },
                "out": {                                                ## Out
                    "selected_code_state": selected_code_state          # Selected code State
                }
            }
            codebase_details_files.change(
                lambda x: x,
                inputs=list(codebase_details_files_change['in'].values()),
                outputs=list(codebase_details_files_change['out'].values())
            )

            new_thread_name_input_submit: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "user_name": selected_user_state,                   # Selected user State
                    "docs_name": selected_codebase_state,               # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state, # Selected external codebases list State
                    "chat_name": new_thread_name_input                  # Thread name input Textbox
                },
                "out": {                                                ## Out
                    "thread_radio": thread_radio,                       # Chat Radio
                    "selected_thread_state": selected_thread_state,     # Selected chat State
                    "delete_chat_button": delete_chat_button,                     # Chat delete Button
                    "new_thread_name_input": new_thread_name_input,     # Thread name input Textbox
                    "status_messages": status_messages                  # Status messages Textbox
                }
            }
            new_thread_name_input.submit(
                self._handle_create_chat_submit,
                inputs=list(new_thread_name_input_submit['in'].values()),
                outputs=list(new_thread_name_input_submit['out'].values())
            )
            
            delete_chat_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "selected_chat": selected_thread_state,             # Selected chat State
                    "user_name": selected_user_state,                   # Selected user State
                    "docs_name": selected_codebase_state,               # Selected codebase state
                    "ext_docs_list": selected_external_docs_list_state  # Selected external codebases list State
                },
                "out": {                                                ## Out
                    "confirm_delete_modal": confirm_delete_modal,       # Confirm deletion Modal
                    "confirm_delete_text": confirm_delete_text          # Confirm deletion Markdown
                }
            }
            delete_chat_button.click(
                self._confirm_deletion_modal,
                inputs=list(delete_chat_button_click['in'].values()),
                outputs=list(delete_chat_button_click['out'].values())
            )

            cancel_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                },                                                  # None
                "out": {                                            ## Out
                    "confirm_delete_modal": confirm_delete_modal    # Confirm deletion Modal
                }
            }
            cancel_delete_button.click(
                utils.cancel_deletion_trigger,
                inputs=list(cancel_delete_button_click['in'].values()),
                outputs=list(cancel_delete_button_click['out'].values())
            )

            confirm_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "user_name": selected_user_state,                   # Selected user State
                    "docs_name": selected_codebase_state,               # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state, # Selected external codebases list State
                    "chat_id": selected_thread_state                    # Selected chat State
                },
                "out": {                                                ## Out
                    "thread_radio": thread_radio,                       # Chat Radio
                    "selected_thread_state": selected_thread_state,     # Selected chat State
                    "delete_chat_button": delete_chat_button,           # Chat deletion Button
                    "confirm_delete_modal": confirm_delete_modal,       # Confirm deletion Modal
                    "status_messages": status_messages                  # Status messages Textbox
                }
            }
            confirm_delete_button.click(
                self._handle_delete_chat_click,
                inputs=list(confirm_delete_button_click['in'].values()),
                outputs=list(confirm_delete_button_click['out'].values())
            )

            chat_mode_input = {                                     ## In
                "user_name": selected_user_state,                   # Selected user State
                "docs_name": selected_codebase_state,               # Selected codebase State
                "ext_docs_list": selected_external_docs_list_state, # Selected external codebases list State
                "chat_id": selected_thread_state,                   # Selected chat State
                "chat_input": user_input                            # User message input Textbox
            }
            chat_mode_output = {                                    ## Out
                "transcript": transcript,                           # Chatbot
            }
            user_input_submit: Dict[str, Dict[str, Any]] = {
                "in": chat_mode_input,
                "out": {                                                ## Out
                    "transcript": transcript,                           # Chatbot
                    "user_input": user_input                            # User message input Textbox
                }
            }
            user_input.submit(
                self._handle_chat_input_submit,
                inputs=list(user_input_submit['in'].values()),
                outputs=list(user_input_submit['out'].values())
            )

            transcript_undo: Dict[str, Dict[str, Any]] = {
                "in": chat_mode_input,
                "out": chat_mode_output
            }
            transcript.undo(
                self._handle_chat_undo_submit,
                inputs=list(transcript_undo['in'].values()),
                outputs=list(transcript_undo['out'].values())
            )

            transcript_retry: Dict[str, Dict[str, Any]] = {
                "in": chat_mode_input,
                "out": chat_mode_output
            }
            transcript.retry(
                self._handle_chat_retry_submit,
                inputs=list(transcript_retry['in'].values()),
                outputs=list(transcript_retry['out'].values())
            )

            transcript_edit: Dict[str, Dict[str, Any]] = {
                "in": chat_mode_input,
                "out": chat_mode_output
            }
            transcript.edit(
                self._handle_chat_edit_submit,
                inputs=list(transcript_edit['in'].values()),
                outputs=list(transcript_edit['out'].values())
            )
        except Exception as e:
            logger.error(f'❌ Problem setting component triggers for chat interface: `{str(e)}`')
            raise

    def create_interface(
        self, 
        initial_threads_list: List[str], 
        initial_thread: str, 
        initial_convo: str,
        initial_code_list: List[str], 
        initial_code: str, 
        initial_code_content: str,
        initial_chat_del_button: bool
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create the chat interface.

        Args
        ------------
            initial_threads_list: List[str]
                The initial list of available chats.
            initial_thread: str
                The initially selected chat.
            initial_convo: str
                The content of the initially selected chat.
            initial_code_list: List[str]
                The initial list of available codes.
            initial_code: str
                The initially selected code.
            initial_code_content: str
                The content of the initially selected code.
            initial_chat_del_button: Button
                The initial interactivity for the chat delete button.


        Returns
        ------------
            Dict[str, Dict[str, Any]]:
                A dictionary of chat interface components to pass to the main app.
            
        Raises
        ------------
            Exception: 
                If creating the chat interface fails, error is logged and raised.
        """
        try:
            chat_interface_config: Dict[str, Dict[str, Any]] = {
                "new_thread_name_input": {  # Input for new chat name                  
                    "component_type": Textbox,
                    "placeholder": "Enter chat name...",
                    "show_label": False,
                    "submit_btn": True
                },
                "thread_radio": {   # Chat Radio
                    "component_type": Radio,
                    "show_label": False,
                    "choices": initial_threads_list,
                    "value": initial_thread,
                    "type": "value"
                },
                "delete_chat_button": {  # Chat delete Button
                    "component_type": Button,
                    "value": "DELETE",
                    "interactive": initial_chat_del_button,
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm"
                },
                "transcript": { # Chatbot
                    "component_type": Chatbot,
                    "value": initial_convo,
                    "label": "Conversation",
                    "type": "messages",
                    "show_copy_all_button": True,
                    "show_copy_button": True
                },
                "user_input": { # User message input Textbox
                    "component_type": Textbox,
                    "placeholder": "Enter text here...",
                    "show_label": False
                },
                "codebase_details_files": { # Code Radio
                    "component_type": Radio,
                    "show_label": False,
                    "choices": initial_code_list,
                    "value": initial_code,
                    "type": "value"
                },
                "codebase_details_file_content": {  # Code content Markdown
                    "component_type": Markdown,
                    "value": initial_code_content,
                    "container": True,
                    "render": True
                },
                "confirm_chat_delete_text": {   # Confirm chat deletion message Markdown
                    "component_type": Markdown,
                    "value": ""
                },
                "confirm_chat_delete_button": { # Confirm chat deletion Button
                    "component_type": Button,
                    "value": "YES",
                    "variant": "primary",
                    "size": "sm"
                },
                "cancel_chat_delete_button": {  # Cancel chat deletion button
                    "component_type": Button,
                    "value": "NO",
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm"
                }
            }
            params_dict: Dict[str, Any] = {}
            with Row(visible=False, elem_id='chat_row', equal_height=True) as chat_row:
                params_dict['chat_row'] = chat_row
                with Column():
                    with Tab('Chat'):
                        with Row(equal_height=True):
                            with Column(scale=1):
                                with Accordion('⚙️ Chat Creation'):
                                    Markdown('Input a chat name.')
                                    params_dict['new_thread_name_input'] = utils.create_component(chat_interface_config['new_thread_name_input'])
                                with Accordion('📝 Available Chats'):
                                    Markdown('Select or delete a chat.')
                                    params_dict['thread_radio'] = utils.create_component(chat_interface_config['thread_radio'])
                                    params_dict['delete_chat_button'] = utils.create_component(chat_interface_config['delete_chat_button'])
                            with Column(scale=2):
                                params_dict['transcript'] = utils.create_component(chat_interface_config['transcript'])
                                params_dict['user_input'] = utils.create_component(chat_interface_config['user_input'])
                    with Tab('Codebase Details'):
                        with Row():
                            with Column(scale=1):
                                with Accordion('📂 Availables Files'):
                                    params_dict['codebase_details_files'] = utils.create_component(chat_interface_config['codebase_details_files'])
                            with Column(scale=2):
                                with Accordion('📝 Selected File'):
                                    params_dict['codebase_details_file_content'] = utils.create_component(chat_interface_config['codebase_details_file_content'])
            with Modal(visible=False) as modal_chats:
                params_dict['confirm_chat_delete_modal'] = modal_chats
                params_dict['confirm_chat_delete_text'] = utils.create_component(chat_interface_config['confirm_chat_delete_text'])
                with Row():
                    params_dict['confirm_chat_delete_button'] = utils.create_component(chat_interface_config['confirm_chat_delete_button'])
                    params_dict['cancel_chat_delete_button'] = utils.create_component(chat_interface_config['cancel_chat_delete_button'])
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating user interface: `{str(e)}`')
            raise