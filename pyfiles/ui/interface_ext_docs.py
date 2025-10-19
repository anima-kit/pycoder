### pyfiles.ui.interface_ext_docs
## This file creates the external docs interface for the Gradio app.
## Gradio components and component triggers are created for external codebase management.

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
from pyfiles.ui import utils, interface_docs

## Create the ext docs interface handler
class ExtDocsInterface:
    """
    A class to create an external docs interface handler.
    This creates the Gradio app components and component triggers for the external docs interface.

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
        Initialize the external docs interface handler.

        Args
        ------------
            users: Users
                The users handler.
            
        Raises
        ------------
            Exception: 
                If initializing the external docs interface fails, error is logged and raised.
        """ 
        try:
            self.users = users
        except Exception as e:
            logger.error(f'❌ Problem creating external docs interface: `{str(e)}`')
            raise

    def _confirm_deletion_modal(
        self, 
        selected_codebase: str
    ) -> Tuple[Modal, Markdown]:
        """
        Create the confirm deletion modal for external docs deletion.

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
        ext_docs_list: List[str], 
        selected_ext_docs: str
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
            selected_ext_docs: str
                The selected external codebase.

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
            ## Get the current codebase handler
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get the threads handler for the current codebase
            docs: Threads = ext_docs.get_current_codebase(selected_ext_docs)
            ## Get the doc name
            codes: List[Tuple[str, str]] = await docs.get_list("code")
            file_name: str | None = None
            for key, value in codes:
                if value==selected_code_state:
                    file_name = key
            message: str = f"⚠️ Are you sure you want to delete file `{file_name}`?"
            return (
                Modal(visible=True), 
                Markdown(value=message)
            )
        except Exception as e:
            logger.error(f'❌ Problem creating confirm deletion modal: `{str(e)}`')
            raise

    
    async def _handle_create_ext_docs_submit(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        ext_docs_name: str, 
        progress=Progress()
    ) -> Tuple[str, CheckboxGroup, Radio, Button, str | None, str, str]:
        """
        Handle the creation of a new external codebase.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            ext_docs_name: str
                The name of the external codebase.
            progress: Progress
                The progress bar.
        
        Returns
        ------------
            Tuple[str, CheckboxGroup, Radio, Button, str, str, str]:
                A tuple of the UI properties for the newly selected codebase after creation.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new codebase fails, error is logged and raised.
        """
        try:
            ## Get codebase handler for current user
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Create new external codebase
            codebase_type, codebases, name, thread_ids, status_message = await ext_docs.create_new_codebase(ext_docs_name)
            progress(0, desc=f'⚙️ Creating external codebase "{name}"')
            ## Get properties for newly selected codebase
            del_button: Button = utils.toggle_del_button(codebases)  
            thread_id: str | None = None 
            if thread_ids:
                thread_id = thread_ids[0]
            return (
                name,                                               # Selected external codebase State
                CheckboxGroup(choices=codebases, value=codebases),  # External codebases CheckboxGroup
                Radio(choices=codebases, value=name),               # External codebases Radio
                del_button,                                         # External codebases delete Button
                thread_id,                                          # Selected code State
                '',                                                 # External codebase name input
                status_message                                      # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling external codebase creation: `{str(e)}`')
            raise

    async def _handle_delete_ext_docs_click(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        ext_docs_name: str, 
        progress=Progress()
    ) -> Tuple[str | None, CheckboxGroup, Radio, Button, List[str | None] | str | None, Modal, str]:
        """
        Handle the deletion of a selected external codebase.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            ext_docs_name: str
                The name of the external codebase.
            progress: Progress
                The progress bar.
        
        Returns
        ------------
            Tuple[str | None, CheckboxGroup, Radio, Button, List[str | None] | str | None, Modal, str]:
                A tuple of the UI properties for the newly selected codebase after deletion.
            
        Raises
        ------------
            Exception: 
                If handling the deletion of a selected codebase fails, error is logged and raised.
        """
        try:
            progress(0, desc=f'⚙️ Deleting codebase `{ext_docs_name}`.')
            ## Get codebase handler for selected user
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Delete selected external codebase
            codebase_type, selected_codebase, codebases, thread_ids, status_message = await ext_docs.delete_codebase(ext_docs_name)
            ## Get properties for newly selected codebase
            del_button: Button = utils.toggle_del_button(codebases)
            thread_id: str | None = None 
            if thread_ids:
                thread_id = thread_ids[0]
            return (
                selected_codebase,                                  # Selected external codebase State
                CheckboxGroup(choices=codebases, value=codebases),  # External codebases CheckboxGroup
                Radio(choices=codebases, value=selected_codebase),  # External codebases Radio
                del_button,                                         # External codebases delete Button
                thread_id,                                          # Selected external code State
                Modal(visible=False),                               # Confirm codebase deletion Modal
                status_message                                      # Status messages Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling external codebase deletion: `{str(e)}`')
            raise

    async def _handle_create_ext_doc_upload(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        ext_docs_name: str, 
        files: List[str] | None
    ) -> Tuple[Radio, str, Button, str]:
        """
        Handle the creation of new external codebase documents.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            ext_docs_name: str
                The name of the external codebase.
            files: List[str]
                The files to be uploaded and converted to documents.
        
        Returns
        ------------
            Tuple[Radio, str, Button, str]:
                A tuple of the UI properties for the newly selected code after creation.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new code fails, error is logged and raised.
        """
        try:
            ## Get external codebase handler for selected user
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected external codebase
            docs: Threads = ext_docs.get_current_codebase(ext_docs_name)
            ## Create the new documents
            choices, thread_id, _, status_message = await docs.create("code", files=files)
            ## Get properties or newly selected external code
            del_button: Button = utils.toggle_del_button(choices)
            thread_radio: Radio = Radio(choices=choices, value=thread_id)
            return (
                thread_radio,   # External code document Radio
                thread_id,      # Selected code document State
                del_button,     # Delete code document Button
                status_message  # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling code creation: `{str(e)}`')
            raise

    async def _handle_delete_ext_doc_click(
        self, 
        user_name: str, 
        docs_name: str, 
        ext_docs_list: List[str], 
        ext_docs_name: str, 
        doc_id: str
    ) -> Tuple[Radio, str | None, Button, Modal, str]:
        """
        Handle the deletion of the selected external codebase document.

        Args
        ------------
            user_name: str 
                The selected user name.
            docs_name: str
                The selected codebase name.
            ext_docs_list: List[str]
                The list of selected external codebases.
            ext_docs_name: str
                The name of the external codebase.
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
        try:
            ## Get external codebase handler for selected user
            _, ext_docs = await utils.handle_current_user(self.users, user_name, docs_name, ext_docs_list)
            ## Get threads handler for selected external codebase
            docs: Threads = ext_docs.get_current_codebase(ext_docs_name)
            ## Delete the selected external code
            choices, next_selected, status_message = await docs.delete("code", doc_id)
            ## Get properties for newly selected code
            thread_radio: Radio = Radio(
                choices=choices,
                value=next_selected,
            )
            del_button: Button = utils.toggle_del_button(choices)
            return (
                thread_radio,           # External code document Radio
                next_selected,          # Selected external code document State
                del_button,             # Delete external code document Button
                Modal(visible=False),   # Confirm external code deletion Modal
                status_message          # Status message Textbox
            )
        except Exception as e:
            logger.error(f'❌ Problem handling code deletion: `{str(e)}`')
            raise

    def component_triggers(
        self,
        selected_user_state: State,
        selected_codebase_state: State,
        external_docs_name_input: Textbox,
        selected_external_docs_list_state: State,
        selected_external_codebase_state: State,
        external_codebases_checkbox: CheckboxGroup,
        external_codebases_radio: Radio,
        external_docs_upload: File,
        delete_external_docs_button: Button,
        external_codebases_files_radio: Radio,
        selected_external_docs_file_state: State,
        delete_external_code_button: Button,
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
            external_docs_name_input: Textbox
                User input for external codebase name.
            selected_external_docs_list_state: State
                The selected external codebases list.
            selected_external_codebase_state: State
                The selected external codebase.
            external_codebases_checkbox: CheckboxGroup
                The external codebases checkbox.
            external_codebases_radio: Radio
                The external codebase radio.
            external_docs_upload: File
                The file component to upload files.
            delete_external_docs_button: Button
                The button to delete a codebase.
            external_codebases_files_radio: Radio
                The codebase document radio.
            selected_external_docs_file_state: State
                The selected external codebase code document.
            delete_external_code_button: Button
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
            external_codebases_checkbox_change: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "external_codebases_checkbox": external_codebases_checkbox              # External codebases CheckboxGroup
                },
                "out": {                                                                    ## Out
                    "selected_external_docs_list_state": selected_external_docs_list_state  # Selected external codebases list State
                }
            }
            external_codebases_checkbox.change(
                lambda x: x, 
                inputs=list(external_codebases_checkbox_change['in'].values()),
                outputs=list(external_codebases_checkbox_change['out'].values())
            )

            external_codebases_radio_change: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "external_codebases_radio": external_codebases_radio                    # External codebases Radio
                },
                "out": {                                                                    ## Out
                    "selected_external_codebase_state": selected_external_codebase_state    # Selected external codebase State
                }
            }
            external_codebases_radio.change(
                lambda x: x,
                inputs=list(external_codebases_radio_change['in'].values()),
                outputs=list(external_codebases_radio_change['out'].values())
            )

            external_codebases_files_radio_change: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "external_codebases_files_radio": external_codebases_files_radio        # External codebase code Radio
                },
                "out": {                                                                    ## Out
                    "selected_external_docs_file_state": selected_external_docs_file_state  # Selected external codebase code State
                }
            }
            external_codebases_files_radio.change(
                lambda x: x,
                inputs=list(external_codebases_files_radio_change['in'].values()),
                outputs=list(external_codebases_files_radio_change['out'].values())
            )

            external_docs_name_input_submit: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "user_name": selected_user_state,                                       # Selected user State
                    "docs_name": selected_codebase_state,                                   # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,                     # Selected external codebases list State
                    "ext_docs_name": external_docs_name_input                               # External codebase name input Textbox
                },
                "out": {                                                                    ## Out
                    "selected_external_codebase_state": selected_external_codebase_state,   # Selected external codebase State
                    "external_codebases_checkbox": external_codebases_checkbox,             # External codebases CheckboxGroup
                    "external_codebases_radio": external_codebases_radio,                   # External codebases Radio
                    "delete_external_docs_button": delete_external_docs_button,             # Delete external codebases Button
                    "selected_external_docs_file_state": selected_external_docs_file_state, # Selected external codebase code State
                    "external_docs_name_input": external_docs_name_input,                   # External codebase name input Textbox
                    "status_messages": status_messages                                      # Status messages Textbox
                }
            }
            external_docs_name_input.submit(
                self._handle_create_ext_docs_submit,
                inputs=list(external_docs_name_input_submit['in'].values()),
                outputs=list(external_docs_name_input_submit['out'].values())
            )

            delete_external_docs_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                     ## In
                    "selected_codebase": selected_external_codebase_state   # Selected external codebase State
                },
                "out": {                                                    ## Out
                    "confirm_delete_modal": confirm_delete_modal,           # Confirm codebase deletion Modal
                    "confirm_delete_text": confirm_delete_text              # Confirm codebase deletion Markdown
                }
            }
            delete_external_docs_button.click(
                self._confirm_deletion_modal,
                inputs=list(delete_external_docs_button_click['in'].values()),
                outputs=list(delete_external_docs_button_click['out'].values())
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
                "in": {                                                                     ## In                                  
                    "user_name": selected_user_state,                                       # Selected user State
                    "docs_name": selected_codebase_state,                                   # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,                     # Selected external codebases list State
                    "ext_docs_name": selected_external_codebase_state                       # Selected external codebase State
                },
                "out": {
                    "selected_external_codebase_state": selected_external_codebase_state,   # Selected external codebase State
                    "external_codebases_checkbox": external_codebases_checkbox,             # External codebases CheckboxGroup
                    "external_codebases_radio": external_codebases_radio,                   # External codebases Radio
                    "delete_external_docs_button": delete_external_docs_button,             # Delete external codebases Button
                    "selected_external_docs_file_state": selected_external_docs_file_state, # Selected external codebase code State
                    "confirm_delete_modal": confirm_delete_modal,                           # Confirm codebase deletion Modal
                    "status_messages": status_messages                                      # Status messages Textbox
                }
            }
            confirm_delete_button.click(
                self._handle_delete_ext_docs_click,
                inputs=list(confirm_delete_button_click['in'].values()),
                outputs=list(confirm_delete_button_click['out'].values())
            )

            external_docs_upload_upload: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "user_name": selected_user_state,                                       # Selected user State
                    "docs_name": selected_codebase_state,                                   # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,                     # Selected external codebases list State
                    "ext_docs_name": selected_external_codebase_state,                      # Selected external codebase State
                    "files": external_docs_upload                                           # External codebase code document File upload
                },
                "out": {                                                                    ## Out
                    "external_codebases_files_radio": external_codebases_files_radio,       # Selected external codebase document Radio
                    "selected_external_docs_file_state": selected_external_docs_file_state, # Selected external document State
                    "delete_external_code_button": delete_external_code_button,             # Delete external document Button
                    "status_messages": status_messages                                      # Status messages Textbox

                }
            }
            external_docs_upload.upload(
                self._handle_create_ext_doc_upload,
                inputs=list(external_docs_upload_upload['in'].values()),
                outputs=list(external_docs_upload_upload['out'].values())
            )

            delete_external_code_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                         ## In
                    "selected_code_state": selected_external_docs_file_state,   # Selected external document State
                    "user_name": selected_user_state,                           # Selected user State
                    "docs_name": selected_codebase_state,                       # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,         # Selected external codebases list State
                    "selected_ext_docs": selected_external_codebase_state       # Selected external codebase State
                },
                "out": {                                                        ## Out
                    "confirm_code_delete_modal": confirm_code_delete_modal,     # Confirm document deletion Modal
                    "confirm_code_delete_text": confirm_code_delete_text        # Confirm document deletion Markdown
                }
            }
            delete_external_code_button.click(
                self._confirm_code_deletion_modal,
                inputs=list(delete_external_code_button_click['in'].values()),
                outputs=list(delete_external_code_button_click['out'].values())
            )

            cancel_code_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                     ## In
                },                                                          # None
                "out": {                                                    ## Out
                    "confirm_code_delete_modal": confirm_code_delete_modal  # Confirm document deletion Modal
                }
            }
            cancel_code_delete_button.click(
                utils.cancel_deletion_trigger,
                inputs=list(cancel_code_delete_button_click['in'].values()),
                outputs=list(cancel_code_delete_button_click['out'].values())
            )

            confirm_code_delete_button_click: Dict[str, Dict[str, Any]] = {
                "in": {                                                                     ## In
                    "user_name": selected_user_state,                                       # Selected user State
                    "docs_name": selected_codebase_state,                                   # Selected codebase State
                    "ext_docs_list": selected_external_docs_list_state,                     # Selected external codebases list State
                    "ext_docs_name": selected_external_codebase_state,                      # Selected external codebase State
                    "selected_ext_docs": selected_external_docs_file_state                  # Selected external codebase document State
                },
                "out": {                                                                    ## Out
                    "external_codebases_files_radio": external_codebases_files_radio,       # Selected external codebase document Radio
                    "selected_external_docs_file_state": selected_external_docs_file_state, # Selected external codebase document State
                    "delete_external_code_button": delete_external_code_button,             # Delete external codebase document Button
                    "confirm_code_delete_modal": confirm_code_delete_modal,                 # Confirm document deletion Modal
                    "status_messages": status_messages                                      # Status messages Textbox
                }
            }
            confirm_code_delete_button.click(
                self._handle_delete_ext_doc_click,
                inputs=list(confirm_code_delete_button_click['in'].values()),
                outputs=list(confirm_code_delete_button_click['out'].values())
            )
        except Exception as e:
            logger.error(f'❌ Problem setting component triggers for ext docs interface: `{str(e)}`')
            raise

    def create_interface(
        self,
        initial_external_docs_list_all: List[str],
        initial_external_codebase: str,
        initial_external_code_list: List[str],
        initial_external_docs_file: str,
        initial_external_docs_file_content: str,
        initial_external_codebase_del_button: Button,
        initial_external_codebase_files_del_button: Button
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create the external docs interface.

        Args
        ------------
            initial_external_docs_list_all: List[str]
                The initial list of available codebases.
            initial_external_codebase: str
                The initially selected codebase.
            initial_external_code_list: List[str]
                The initial list of available code documents.
            initial_external_docs_file: str
                The initially selected code document.
            initial_external_docs_file_content: str
                The content of the initially selected code document.
            initial_external_codebase_del_button: Button
                The initial delete external codebases button.
            initial_external_codebase_files_del_button: Button
                The initial delete external codebase document button.

        Returns
        ------------
            Dict[str, Dict[str, Any]]:
                A dictionary of external docs interface components to pass to the main app.
            
        Raises
        ------------
            Exception: 
                If creating the external docs interface fails, error is logged and raised.
        """
        try:
            ext_docs_interface_config: Dict[str, Dict[str, Any]] = {
                "ext_docs_name_input": {    # User input for external codebase name
                    "component_type": Textbox,
                    "placeholder": "Enter external codebase name...",
                    "show_label": False,
                    "submit_btn": True
                },
                "ext_docs_checkbox": {  # Checkboxgroup for selecting external codebases
                    "component_type": CheckboxGroup,
                    "show_label": False,
                    "choices": initial_external_docs_list_all,
                    "value": initial_external_docs_list_all,
                    "type": "value"
                },
                "ext_docs_upload": {    # The file upload for external codebase documents
                    "component_type": File,
                    "label": "Upload External Codebases (folder or .py/.md files)",
                    "file_types": ["directory", ".py", ".md"],
                    "file_count": "multiple",
                    "interactive": initial_external_codebase_del_button
                },
                "delete_ext_docs_button": { # The delete external codebases button
                    "component_type": Button,
                    "value": "DELETE EXT DOCS",
                    "interactive": initial_external_codebase_del_button,
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm"
                },
                "ext_docs_radio": { # The external codebases radio
                    "component_type": Radio,
                    "label": "External Docs",
                    "choices": initial_external_docs_list_all,
                    "value": initial_external_codebase,
                    "type": "value"
                },
                "delete_ext_code_button": { # The delete external codebase document button
                    "component_type": Button,
                    "value": "DELETE FILE",
                    "elem_classes": ["delete-button"],
                    "variant": "huggingface",
                    "interactive": initial_external_codebase_files_del_button,
                    "size": "sm"
                },
                "ext_docs_files_radio": {   # The external codebase document Radio
                    "component_type": Radio,
                    "label": "External Docs Files",
                    "choices": initial_external_code_list,
                    "value": initial_external_docs_file,
                    "type": "value"
                },
                "selected_ext_doc_text": {  # The selected external codebase doc content
                    "component_type": Markdown,
                    "value": initial_external_docs_file_content,
                    "container": True,
                    "render": True
                },
                "confirm_ext_docs_delete_text": {   # The confirm codebase/code deletion text
                    "component_type": Markdown,
                    "value": ""
                },
                "confirm_ext_docs_delete_button": { # The confirm codebase/code deletion button
                    "component_type": Button,
                    "value": "YES",
                    "variant": "primary",
                    "size": "sm"
                },
                "cancel_ext_docs_delete_button": {  # The cancel codebase/code deletion button
                    "component_type": Button,
                    "value": "NO",
                    "variant": "huggingface",
                    "elem_classes": ["delete-button"],
                    "size": "sm"
                }
            }
            params_dict: Dict[str, Any] = {}
            with Row(visible=False, elem_id='external_docs_row', equal_height=True) as external_docs_row:
                params_dict['ext_docs_row'] = external_docs_row
                with Tab('External Docs'):
                    with Row(equal_height=True):
                        with Column(scale=1):
                            with Accordion('⚙️ External Docs Creation'):
                                Markdown('Input an external docs name.')
                                params_dict['ext_docs_name_input'] = utils.create_component(ext_docs_interface_config['ext_docs_name_input'])
                        with Column(scale=2):
                            with Accordion('📝 Available external docs'):
                                Markdown('Select which external docs to chat with')
                                params_dict['ext_docs_checkbox'] = utils.create_component(ext_docs_interface_config['ext_docs_checkbox'])         
                with Tab('External Docs Details'):
                    with Row():
                        with Column(scale=1):
                            with Accordion('📂 Availables Files'):
                                params_dict['ext_docs_upload'] = utils.create_component(ext_docs_interface_config['ext_docs_upload'])  
                                params_dict['delete_ext_docs_button'] = utils.create_component(ext_docs_interface_config['delete_ext_docs_button'])
                                params_dict['ext_docs_radio'] = utils.create_component(ext_docs_interface_config['ext_docs_radio'])
                                params_dict['delete_ext_code_button'] = utils.create_component(ext_docs_interface_config['delete_ext_code_button'])
                                params_dict['ext_docs_files_radio'] = utils.create_component(ext_docs_interface_config['ext_docs_files_radio'])
                        with Column(scale=2):
                            with Accordion('📝 Selected File'):
                                params_dict['selected_ext_doc_text'] = utils.create_component(ext_docs_interface_config['selected_ext_doc_text'])
            with Modal(visible=False) as modal_codebases:
                params_dict['confirm_ext_docs_delete_modal'] = modal_codebases
                params_dict['confirm_ext_docs_delete_text'] = utils.create_component(ext_docs_interface_config['confirm_ext_docs_delete_text'])
                with Row():
                    params_dict['confirm_ext_docs_delete_button'] = utils.create_component(ext_docs_interface_config['confirm_ext_docs_delete_button'])
                    params_dict['cancel_ext_docs_delete_button'] = utils.create_component(ext_docs_interface_config['cancel_ext_docs_delete_button'])
            with Modal(visible=False) as modal_files:
                params_dict['confirm_ext_code_delete_modal'] = modal_files
                params_dict['confirm_ext_code_delete_text'] = utils.create_component(ext_docs_interface_config['confirm_ext_docs_delete_text'])
                with Row():
                    params_dict['confirm_ext_code_delete_button'] = utils.create_component(ext_docs_interface_config['confirm_ext_docs_delete_button'])
                    params_dict['cancel_ext_code_delete_button'] = utils.create_component(ext_docs_interface_config['cancel_ext_docs_delete_button'])
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating external docs interface: `{str(e)}`')
            raise