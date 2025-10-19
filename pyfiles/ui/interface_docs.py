### pyfiles.ui.interface_docs
## This file creates the docs interface for the Gradio app.
## Gradio components and component triggers are created for main codebase management.

## External imports
from gradio import (
    Markdown, 
    Progress, 
    Button, 
    CheckboxGroup, 
    Radio, 
    File, 
    Row, 
    Column, 
    Textbox, 
    State, 
    Accordion, 
    Tab
)
from gradio_modal import Modal # type: ignore 
from typing import (
    List, 
    Tuple, 
    Dict, 
    Any, 
    cast
)

## Internal imports
from pyfiles.bases.logger import logger
from pyfiles.bases.threads import Threads
from pyfiles.bases.users import Users
from pyfiles.ui import utils

## Create the docs interface handler
class DocsInterface:
    """
    A class to create a docs interface handler.
    This creates the Gradio app components and component triggers for the docs interface.

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
        Initialize the docs interface handler.

        Args
        ------------
            users: Users
                The users handler.
            
        Raises
        ------------
            Exception: 
                If initializing the docs interface fails, error is logged and raised.
        """
        try:
            self.users = users
        except Exception as e:
            logger.error(f'❌ Problem creating docs interface: `{str(e)}`')
            raise

    def _confirm_deletion_modal(
        self, 
        selected_codebase: str
    ) -> Tuple[Modal, Markdown]:
        """
        Create the confirm deletion modal for docs deletion.

        Args
        ------------
            selected_codebase: str
                The codebase to delete.

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
            message: str = f"Are you sure you want to delete codebase `{selected_codebase}`?"
            return (
                Modal(visible=True),
                Markdown(value=message)
            )
        except Exception as e:
            logger.error(f'❌ Problem creating confirm deletion modal: `{str(e)}`')
            raise
        
    async def _confirm_code_deletion_modal(
        self, 
        selected_code_state: str, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str]
    ) -> Tuple[Modal, Markdown]:
        """
        Create the confirm deletion modal for code deletion.

        Args
        ------------
            selected_code_state: str
                The code to delete.
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
            ## Get threads manager for selected codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Get all available code docs
            codes: List[Tuple[str, str]] = await docs.get_list("code")
            ## Get code name
            file_name: str | None = None
            for key, value in codes:
                if value==selected_code_state:
                    file_name = key
            message = f"⚠️ Are you sure you want to delete file `{file_name}`?"
            return (
                Modal(visible=True), 
                Markdown(value=message)
            )
        except Exception as e:
            logger.error(f'❌ Problem creating confirm deletion modal: `{str(e)}`')
            raise

    async def _handle_create_docs_submit(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str],
        progress=Progress()
    ) -> Tuple[str, Radio, Button, str, str, str, str]:
        """
        Handle the creation of a new main codebase.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            progress: Progress
                The progress bar.
        
        Returns
        ------------
            Tuple[str, Radio, Button, str, str, str, str]:
                A tuple of the UI properties for the newly selected codebase after creation.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new codebase fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Create new codebase
            codebase_type, codebases, name, thread_ids, status_message = await user.create_new_codebase(docs_name)
            progress(0, desc=f'⚙️ Creating codebase `{name}`')
            ## Get properties for newly selected codebase
            del_button: Button = utils.toggle_del_button(codebases)    
            return (
                name,                                   # Selected codebase State
                Radio(choices=codebases, value=name),   # Codebase Radio
                del_button,                             # Delete codebase Button
                thread_ids[0],                          # Selected chat State
                thread_ids[1],                          # Selected code State
                '',                                     # Codebase name input Textbox
                status_message                          # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling codebase creation: `{str(e)}`')
            raise

    async def _handle_delete_docs_click(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        progress=Progress()
    ) -> Tuple[str, Radio, Button, str, str, Modal, str]:
        """
        Handle the deletion of a selected codebase.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            progress: Progress
                The progress bar.
        
        Returns
        ------------
            Tuple[str, Radio, Button, str, str, Modal, str]:
                A tuple of the UI properties for the newly selected codebase after deletion.
            
        Raises
        ------------
            Exception: 
                If handling the deletion of a selected codebase fails, error is logged and raised.
        """
        progress(0, desc=f'⚙️ Deleting codebase `{docs_name}`')
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Delete selected codebase
            codebase_type, selected_codebase, codebases, thread_ids, status_message = await user.delete_codebase(docs_name)
            ## Get properties for newly selected codebase
            del_button: Button = utils.toggle_del_button(codebases)
            if selected_codebase!=None:
                if thread_ids!=None:
                    if all(type(x)==str for x in thread_ids):
                        thread_id_0: str = cast(str, thread_ids[0])
                        thread_id_1: str = cast(str, thread_ids[1])
                        return (
                            selected_codebase,                                  # Selected codebase State
                            Radio(choices=codebases, value=selected_codebase),  # Codebase Radio
                            del_button,                                         # Delete codebase Button
                            thread_id_0,                                        # Selected chat State
                            thread_id_1,                                        # Selected code State
                            Modal(visible=False),                               # Confirm deletion Modal
                            status_message                                      # Status message Textbox
                        )
                    else:
                        raise ValueError(f'❌ Each thread ID of selected codebase for user should be a string.')
                else:
                    raise ValueError(f'❌ Threads IDs for user should not be None.')
            else:
                raise ValueError(f'❌ Selected codebase and threads IDs should not be None for user.')
        except Exception as e:
            logger.error(f'❌ Problem handling codebase deletion: `{str(e)}`')
            raise

    async def _handle_create_doc_upload(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        files: List[str] | None
    ) -> Tuple[Radio, Button, str]:
        """
        Handle the creation of new codebase documents.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            files: List[str]
                The files to be uploaded and converted to documents.
        
        Returns
        ------------
            Tuple[Radio, Button]:
                A tuple of the UI properties for the newly selected code after creation.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new code fails, error is logged and raised.
        """
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Create the file docs
            choices, thread_id, all_files, _ = await docs.create("code", files=files)
            ## Set properties for newly selected code
            del_button: Button = utils.toggle_del_button(choices)
            thread_radio: Radio = Radio(choices=choices, value=thread_id)
            return (
                thread_radio,   # Code Radio    
                del_button,     # Delete code Button
                thread_id       # Selected code State
            )
        except Exception as e:
            logger.error(f'❌ Problem handling code creation: `{str(e)}`')
            raise

    async def _handle_delete_doc_click(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        doc_id: str,
        progress=Progress()
    ) -> Tuple[Radio, str | None, Button, Modal, str]:
        """
        Handle the deletion of the selected codebase document.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            doc_id: str
                The ID of the document to delete.
            progress: Progress
                The progress bar.
        
        Returns
        ------------
            Tuple[Radio, str | None, Button, Modal, str]:
                A tuple of the UI properties for the newly selected code after deletion.
            
        Raises
        ------------
            Exception: 
                If handling the deletion of a selected code fails, error is logged and raised.
        """
        progress(0, desc=f'⚙️ Deleting "{doc_id}"')
        try:
            ## Get current user
            user, _ = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected codebase
            docs: Threads = user.get_current_codebase(docs_name)
            ## Delete the selected document
            choices, next_selected, status_message = await docs.delete("code", doc_id)
            ## Get properties for newly selected code doc
            thread_radio: Radio = Radio(
                choices=choices,
                value=next_selected,
            )
            del_button: Button = utils.toggle_del_button(choices)
            return (
                thread_radio,           # Code Radio
                next_selected,          # Selected code State
                del_button,             # Delete code Button
                Modal(visible=False),   # Confirm deletion Modal
                status_message          # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling code deletion: `{str(e)}`')
            raise

    def component_triggers(
        self,        
        selected_user_state: State,
        selected_codebase_state: State,
        selected_external_docs_list_state: State,
        selected_thread_state: State,
        selected_code_state: State,
        codebase_radio: Radio,
        codebase_name_input: Textbox,
        delete_codebase_button: Button,
        files_upload: File,
        files_radio: Radio,
        delete_code_button: Button,
        confirm_delete_modal: Modal,
        confirm_delete_text: str,
        confirm_delete_button: Button,
        cancel_delete_button: Button,
        confirm_code_delete_modal: Modal,
        confirm_code_delete_text: str,
        confirm_code_delete_button: Button,
        cancel_code_delete_button: Button,
        status_messages: str
    ) -> None:
        """
        Create the component triggers for all components of the docs interface.

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
            codebase_radio: Radio
                The codebase radio.
            codebase_name_input: Textbox.
                The new thread name input.
            delete_codebase_button: Button
                The button to delete a codebase.
            files_upload: File
                The file component to upload files.
            files_radio: Radio
                The codebase document radio.
            delete_code_button: Button
                The button to delete a codebase document.
            confirm_delete_modal: Modal
                The confirm deletion modal for codebases.
            confirm_delete_text: str
                The confirm deletion text for codebases.
            confirm_delete_button: Button
                The confirm deletion button for codebases.
            cancel_delete_button: Button
                The cancel deletion button for codebases.
            confirm_code_delete_modal: Modal
                The confirm deletion modal for codebase documents.
            confirm_code_delete_text: str
                The confirm deletion text for codebase documents.
            confirm_code_delete_button: Button
                The confirm deletion button for codebase documents.
            cancel_code_delete_button: Button
                The cancel deletion button for codebase documents.
            status_messages: str
                The status messages.
            
        Raises
        ------------
            Exception: 
                If creating the component triggers fails, error is logged and raised.
        """
        try:
            codebase_radio_change: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "codebase_radio": codebase_radio                    # Codebase Radio
                },
                "out": {                                                ## Out
                    "selected_codebase_state": selected_codebase_state  # Selected codebase State
                }
            }
            codebase_radio.change(
                lambda x: x,
                inputs=list(codebase_radio_change['in'].values()),
                outputs=list(codebase_radio_change['out'].values())
            )

            files_radio_change: Dict[str, Dict[str, Any]] = {
                "in": {                                         ## In
                    "files_radio": files_radio                  # Code Radio
                },
                "out": {                                        ## Out
                    "selected_code_state": selected_code_state  # Selected code State
                }
            }
            files_radio.change(
                lambda x: x,
                inputs=list(files_radio_change['in'].values()),
                outputs=list(files_radio_change['out'].values())
            )

            codebase_name_input_submit: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "user_name": selected_user_state,                   # Selected user State
                    "docs_name": codebase_name_input,                   # Codebase name input Textbox
                    "ext_docs_list": selected_external_docs_list_state  # Selected external codebases list State
                },
                "out": {                                                ## Out
                    "selected_codebase_state": selected_codebase_state, # Selected codebase State
                    "codebase_radio": codebase_radio,                   # Codebase Radio
                    "delete_codebase_button": delete_codebase_button,   # Delete codebase Button
                    "selected_thread_state": selected_thread_state,     # Selected chat State
                    "selected_code_state": selected_code_state,         # Selected code State
                    "codebase_name_input": codebase_name_input,         # Codebase name input Textbox
                    "status_messages": status_messages                  # Status messages Textbox
                }
            }
            codebase_name_input.submit(
                self._handle_create_docs_submit,
                inputs=list(codebase_name_input_submit['in'].values()),
                outputs=list(codebase_name_input_submit['out'].values())
            )

            delete_codebase_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                    "selected_codebase": selected_codebase_state    # Selcted codebase State
                },
                "out": {                                            ## Out
                    "confirm_delete_modal": confirm_delete_modal,   # Confirm codebase deletion Modal
                    "confirm_delete_text": confirm_delete_text      # Confirm codebase deletion Markdown
                }
            }
            delete_codebase_button.click(
                self._confirm_deletion_modal,
                inputs=list(delete_codebase_button_click['in'].values()),
                outputs=list(delete_codebase_button_click['out'].values())
            )

            cancel_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                             ## In
                },                                                  # None
                "out": {                                            ## Out
                    "confirm_delete_modal": confirm_delete_modal    # Confirm codebase deletion Modal
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
                    "ext_docs_list": selected_external_docs_list_state  # Selected external codebases list State
                },
                "out": {                                                ## Out
                    "selected_codebase_state": selected_codebase_state, # Selected codebase State
                    "codebase_radio": codebase_radio,                   # Codebase Radio
                    "delete_codebase_button": delete_codebase_button,   # Delete codebase Button
                    "selected_thread_state": selected_thread_state,     # Selected chat State
                    "selected_code_state": selected_code_state,         # Selected code State
                    "confirm_delete_modal": confirm_delete_modal,       # Confirm codebase deletion Modal
                    "status_messages": status_messages                  # Status messages Textbox
                }
            }
            confirm_delete_button.click(
                self._handle_delete_docs_click,
                inputs=list(confirm_delete_button_click['in'].values()),
                outputs=list(confirm_delete_button_click['out'].values())
            )

            files_upload_upload: Dict[str, Dict[str, Any]] = {
                "in": {                                                 ## In
                    "user_name": selected_user_state,                   # Selected user State
                    "docs_name": selected_codebase_state,               # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state, # Selected external codebases list State
                    "files": files_upload                               # Code documents File upload
                },
                "out": {                                                ## Out
                    "files_radio": files_radio,                         # Code documents Radio
                    "delete_code_button": delete_code_button,           # Delete code Button
                    "selected_code_state": selected_code_state,         # Selected code State
                }
            }
            files_upload.upload(
                self._handle_create_doc_upload,
                inputs=list(files_upload_upload['in'].values()),
                outputs=list(files_upload_upload['out'].values())
            )

            delete_code_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                         ## In
                    "selected_code_state": selected_code_state,                 # Selected code State
                    "user_name": selected_user_state,                           # Selected user State
                    "docs_name": selected_codebase_state,                       # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state          # Selected external codebases list State
                },
                "out": {                                                        ## Out
                    "confirm_code_delete_modal": confirm_code_delete_modal,     # Confirm code deletion Modal
                    "confirm_code_delete_text": confirm_code_delete_text        # Confirm code deletion Markdown
                }
            }
            delete_code_button.click(
                self._confirm_code_deletion_modal,
                inputs=list(delete_code_button_click['in'].values()),
                outputs=list(delete_code_button_click['out'].values())
            )

            cancel_code_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                     ## In
                },                                                          # None
                "out": {                                                    ## Out
                    "confirm_code_delete_modal": confirm_code_delete_modal  # Confirm code deletion Modal
                }
            }
            cancel_code_delete_button.click(
                utils.cancel_deletion_trigger,
                inputs=list(cancel_code_delete_button_click['in'].values()),
                outputs=list(cancel_code_delete_button_click['out'].values())
            )

            confirm_code_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                     ## In
                    "user_name": selected_user_state,                       # Selected user State
                    "docs_name": selected_codebase_state,                   # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,     # Selected external codebases list State
                    "doc_id": selected_code_state                           # Selected code State
                },
                "out": {                                                    ## Out
                    "files_radio": files_radio,                             # Code documents Radio
                    "selected_code_state": selected_code_state,             # Selected code State
                    "delete_code_button": delete_code_button,               # Delete code Button
                    "confirm_code_delete_modal": confirm_code_delete_modal, # Confirm code deletion Modal
                    "status_messages": status_messages                      # Status messages Textbox
                }
            }
            confirm_code_delete_button.click(
                self._handle_delete_doc_click,
                inputs=list(confirm_code_delete_button_click['in'].values()),
                outputs=list(confirm_code_delete_button_click['out'].values())
            )
        except Exception as e:
            logger.error(f'❌ Problem setting component triggers for docs interface: `{str(e)}`')
            raise

    def create_interface(
        self, 
        initial_docs_list: List[str], 
        initial_docs_del_button: bool, 
        initial_docs_name: str, 
        initial_doc_list: List[str], 
        initial_doc_del_button: bool,
        initial_doc: str, 
        initial_doc_content: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create the docs interface.

        Args
        ------------
            initial_docs_list: List[str]
                The initial list of available codebases.
            initial_docs_del_button: Button
                The initial interactivity for the codebase delete button.
            initial_docs_name: str
                The initially selected codebase.
            initial_doc_list: List[str]
                The initial list of available code documents.
            initial_doc: str
                The initially selected code document.
            initial_doc_content: str
                The content of the initially selected code document.

        Returns
        ------------
            Dict[str, Dict[str, Any]]:
                A dictionary of docs interface components to pass to the main app.
            
        Raises
        ------------
            Exception: 
                If creating the docs interface fails, error is logged and raised.
        """
        try:
            docs_interface_config: Dict[str, Dict[str, Any]] = {
                "codebase_name_input": {    # The codebase name input Textbox
                    "component_type": Textbox,
                    "placeholder": "Enter docs name...",
                    "show_label": False,
                    "submit_btn": True
                },
                "codebase_radio": { # The codebase Radio
                    "component_type": Radio,
                    "show_label": False,
                    "choices": initial_docs_list,
                    "value": initial_docs_name,
                    "type": "value"
                },
                "delete_codebase_button": { # The delete codebase Button
                    "component_type": Button,
                    "value": "DELETE",
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm",
                    "interactive": initial_docs_del_button
                },
                "files_upload": {   # The code documents File upload
                    "component_type": File,
                    "label": "Upload Codebase (folder with .py/.md files)",
                    "file_types": [".py", ".md"],
                    "file_count": "multiple"
                },
                "files_radio": {    # The code documents Radio
                    "component_type": Radio,
                    "show_label": False,
                    "choices": initial_doc_list,
                    "value": initial_doc,
                    "type": "value"
                },
                "delete_code_button": { # The delete code Button
                    "component_type": Button,
                    "value": "DELETE",
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm",
                    "interactive": initial_doc_del_button
                },
                "selected_file_text": { # The content of the selected code document
                    "component_type": Markdown,
                    "value": initial_doc_content,
                    "container": True,
                    "render": True
                },
                "confirm_codebase_delete_text": {   # The confirm codebase/code deletion Markdown
                    "component_type": Markdown,
                    "value": ""
                },
                "confirm_codebase_delete_button": { # The confirm codebase/code deletion Button
                    "component_type": Button,
                    "value": "YES",
                    "variant": "primary",
                    "size": "sm"
                },
                "cancel_codebase_delete_button": {  # The cancel codebase/code deletion Button
                    "component_type": Button,
                    "value": "NO",
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm"
                }
            }
            params_dict: Dict[str, Any] = {}
            with Row(visible=False, elem_id='docs_row', equal_height=True) as docs_row:
                params_dict['docs_row'] = docs_row
                with Tab('Codebases'):
                    with Row():
                        with Column(scale=1):
                            with Accordion('⚙️ Codebase Creation'):
                                Markdown('Input a docs name.')
                                params_dict['codebase_name_input'] = utils.create_component(docs_interface_config['codebase_name_input'])
                        with Column(scale=2):
                            with Accordion('📝 Available docs'):
                                Markdown('Select which docs to chat with or delete selected docs')
                                params_dict['codebase_radio'] = utils.create_component(docs_interface_config['codebase_radio'])
                                params_dict['delete_codebase_button'] = utils.create_component(docs_interface_config['delete_codebase_button'])
                with Tab('Codebase Details'):
                    with Row():
                        with Column(scale=1):
                            with Accordion('📂 Availables Files'):
                                params_dict['files_upload'] = utils.create_component(docs_interface_config['files_upload'])
                                params_dict['files_radio'] = utils.create_component(docs_interface_config['files_radio'])
                                params_dict['delete_code_button'] = utils.create_component(docs_interface_config['delete_code_button'])
                        with Column(scale=2):
                            with Accordion('📝 Selected File'):
                                params_dict['selected_file_text'] = utils.create_component(docs_interface_config['selected_file_text'])
            with Modal(visible=False) as modal_codebases:
                params_dict['confirm_codebase_delete_modal'] = modal_codebases
                params_dict['confirm_codebase_delete_text'] = utils.create_component(docs_interface_config['confirm_codebase_delete_text'])
                with Row():
                    params_dict['confirm_codebase_delete_button'] = utils.create_component(docs_interface_config['confirm_codebase_delete_button'])
                    params_dict['cancel_codebase_delete_button'] = utils.create_component(docs_interface_config['cancel_codebase_delete_button'])
            with Modal(visible=False) as modal_files:
                params_dict['confirm_code_delete_modal'] = modal_files
                params_dict['confirm_code_delete_text'] = utils.create_component(docs_interface_config['confirm_codebase_delete_text'])
                with Row():
                    params_dict['confirm_code_delete_button'] = utils.create_component(docs_interface_config['confirm_codebase_delete_button'])
                    params_dict['cancel_code_delete_button'] = utils.create_component(docs_interface_config['cancel_codebase_delete_button'])
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating docs interface: `{str(e)}`')
            raise
