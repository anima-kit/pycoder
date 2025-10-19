### pyfiles.ui.interface_user
## This file creates the user interface for the Gradio app.
## Gradio components and component triggers are created for user management.

## External imports
from gradio import (
    Button, 
    Markdown, 
    Progress, 
    Radio, 
    Textbox, 
    Accordion, 
    Row, 
    State,
    Column,
    HTML
)
from gradio_modal import Modal # type: ignore
from typing import List, Dict, Any, Tuple

## Internal imports
from pyfiles.bases.logger import logger
from pyfiles.bases.users import Users
from pyfiles.ui import utils


## Create the user interface handler
class UserInterface:
    """
    A class to create a user interface handler.
    This creates the Gradio app components and component triggers for the user interface.

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
        Initialize the user interface handler.

        Args
        ------------
            users: Users
                The users handler.
            
        Raises
        ------------
            Exception: 
                If initializing the user interface fails, error is logged and raised.
        """
        try:
            self.users = users
        except Exception as e:
            logger.error(f'❌ Problem creating user interface: `{str(e)}`')
            raise

    def _confirm_deletion_modal(
        self, 
        selected_user: str
    ) -> Tuple[Modal, Markdown]:
        """
        Create the confirm deletion modal for user deletion.

        Args
        ------------
            selected_user: str
                The user to delete.

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
            message: str = f"⚠️ Are you sure you want to delete user `{selected_user}`?"
            return (
                Modal(visible=True),    # Confirm deletion modal
                Markdown(value=message) # Confirm deletion text
            )
        except Exception as e:
            logger.error(f'❌ Problem creating user deletion modal: `{str(e)}`')
            raise

    async def _handle_new_user_submit(
        self, 
        selected_user: str,
        name: str, 
        progress: Progress = Progress()
    ) -> Tuple[str, Radio, Button, str, str]:
        """
        Handle the creation of new users.

        Args
        ------------
            name: str
                The name of the new user.
            progress (Optional): Progress
                The progress bar to display status.
        
        Returns
        ------------
            Tuple[str, Radio, Button, str, str]:
                A tuple of the UI properties for the newly selected user after creation.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new user fails, error is logged and raised.
        """
        try:
            if self.users!=None:
                ## Create the new user
                name, status_message = await self.users.create_new_user(
                    name=name, 
                    selected_user=selected_user
                )
                progress(0, desc=f"⚙️ Creating new user: `{name}`")
                ## Get the UI for the newly selected user
                users = self.users.get_users_list()
                del_button = utils.toggle_del_button(users)
                return(
                    name,                               # Selected user
                    Radio(choices=users, value=name),   # User radio    
                    del_button,                         # User delete button
                    '',                                 # User name input
                    status_message                      # Status message
                )
            else:
                message = f'❌ Attribute `users` should not be None.'
                raise ValueError(message)
        except Exception as e:
            logger.error(f'❌ Problem creating user: `{str(e)}`')
            raise

    async def _handle_delete_user_click(
        self, 
        name: str, 
        progress: Progress = Progress()
    ) -> Tuple[str | None, Radio, Button, Modal, str]:
        """
        Handle the deletion of selected users.

        Args
        ------------
            name: str
                The name of the selected user to delete.
            progress (Optional): Progress
                The progress bar to display status.
        
        Returns
        ------------
            Tuple[str | None, Radio, Button, Modal, str]:
                A tuple of the UI properties for the newly selected user after deletion.
            
        Raises
        ------------
            Exception: 
                If handling the creation of a new user fails, error is logged and raised.
        """
        try:
            progress(0, desc=f"⚙️ Deleting user: {name}")
            if self.users!=None:
                ## Delete the user
                selected_user, status_message = await self.users.delete_user(name)
                ## Get properties for newly selected user
                users = self.users.get_users_list()
                del_button = utils.toggle_del_button(users)
                return (
                    selected_user,                              # Selected user
                    Radio(choices=users, value=selected_user),  # User radio
                    del_button,                                 # User delete button
                    Modal(visible=False),                       # Confirm deletion modal
                    status_message                              # Status message
                )
            else:
                message = f'❌ Attribute `users` should not be None.'
                raise ValueError(message)
        except Exception as e:
            logger.error(f'❌ Problem deleting user: `{str(e)}`')
            raise

    def component_triggers(
        self,
        selected_user_state: State,
        user_radio: Radio,
        delete_user_button: Button,
        user_name_input: Textbox,
        confirm_delete_modal: Modal,
        confirm_delete_text: str,
        confirm_delete_button: Button,
        cancel_delete_button: Button,
        status_messages: str
    ) -> None:
        """
        Create the component triggers for all components of the user interface.

        Args
        ------------
            selected_user_state: State
                The selected user state.
            user_radio: Radio
                The user radio.
            delete_user_button: Button
                The delete user button.
            user_name_input: Textbox
                The user name input textbox.
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
            ## User radio
            # Set triggers for a new value being selected
            user_radio_change: Dict[str, dict] = {
                "in": {                                         ## In
                    "user_radio": user_radio                    # User radio
                },
                "out": {                                        ## Out
                    "selected_user_state": selected_user_state  # Selected user state
                }
            }
            user_radio.change(
                lambda x: x,
                inputs=list(user_radio_change['in'].values()),
                outputs=list(user_radio_change['out'].values())
            )

            ## User name input
            # Set triggers for the user inputing a new user name
            user_name_input_submit: Dict[str, dict] = {
                "in": {                                         ## In
                    "selected_user": selected_user_state,       # Selected user State
                    "name": user_name_input                     # User name input Textbox
                },
                "out": {                                        ## Out
                    "selected_user_state": selected_user_state, # Selected user State
                    "user_radio": user_radio,                   # User Radio
                    "delete_user_button": delete_user_button,   # Delete user Button
                    "user_name_input": user_name_input,         # User name input Textbox
                    "status_messages": status_messages          # Status messages Textbox
                }
            }
            user_name_input.submit(
                self._handle_new_user_submit,
                inputs=list(user_name_input_submit['in'].values()),
                outputs=list(user_name_input_submit['out'].values())
            )

            ## Deleting user button
            # Deal with the user clicking the delete user button
            delete_user_button_click: Dict[str, dict] = {
                "in": {                                             ## In
                    "selected_user_state": selected_user_state      # Selected user State
                },
                "out": {                                            ## Out
                    "confirm_delete_modal": confirm_delete_modal,   # Confirm deletion Modal
                    "confirm_delete_text": confirm_delete_text      # Confirm deletion Textbox
                }
            }
            delete_user_button.click(
                self._confirm_deletion_modal,
                inputs=list(delete_user_button_click['in'].values()),
                outputs=list(delete_user_button_click['out'].values())
            )

            ## Cancel deletion button
            # Deal with the user clicking the cancel deleting button
            cancel_delete_button_click: Dict[str, dict] = {
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

            ## Confirm deletion button
            # Deal with the user clicking the confirm deletion button
            confirm_delete_button_click: Dict[str, dict] = {
                "in": {                                             ## In
                    "selected_user_state": selected_user_state      # Selected user State
                },  
                "out": {                                            ## Out
                    "selected_user_state": selected_user_state,     # Selected user State
                    "user_radio": user_radio,                       # User Radio
                    "delete_user_button": delete_user_button,       # Delete user Button
                    "confirm_delete_modal": confirm_delete_modal,   # Confirm deletion Modal
                    "status_messages": status_messages              # Status messages Textbox
                }
            }
            confirm_delete_button.click(
                self._handle_delete_user_click,
                inputs=list(confirm_delete_button_click['in'].values()),
                outputs=list(confirm_delete_button_click['out'].values())
            )
        except Exception as e:
            logger.error(f'❌ Problem setting component triggers for user interface: `{str(e)}`')
            raise

    def create_interface(
        self, 
        initial_del_button: bool
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create the user interface.

        Args
        ------------
            initial_del_button: bool
                Defines the interactivity of the user delete button initially.

        Returns
        ------------
            Dict[str, Dict[str, Any]]:
                A dictionary of user interface components to pass to the main app.
            
        Raises
        ------------
            Exception: 
                If creating the user interface fails, error is logged and raised.
        """
        try:
            if self.users!=None:
                user_interface_config: Dict[str, Dict[str, Any]] = {
                    "user_name_input": {    # User name input textbox                  
                        "component_type": Textbox, 
                        "placeholder": "Enter user name...", 
                        "show_label": False, 
                        "submit_btn": True
                    },
                    "delete_user_button": { # Delete user button
                        "component_type": Button,
                        "interactive": initial_del_button,
                        "value": "DELETE",
                        "variant": "huggingface",
                        "elem_classes": ["delete-button"],
                        "size": "sm"
                    },
                    "user_radio": { # User radio
                        "component_type": Radio, 
                        "label": None, 
                        "show_label": False, 
                        "choices": self.users.get_users_list(), 
                        "value": self.users.get_users_list()[0], 
                        "type": "value"
                    },
                    "confirm_user_delete_text": {   # Confirm user deletion text
                        "component_type": Markdown,
                        "value": ""
                    },
                    "confirm_user_delete_button": { # Confirm user deleting button
                        "component_type": Button,
                        "value": "YES",
                        "variant": "primary",
                        "size": "sm"
                    },
                    "cancel_user_delete_button": {  # Cancel user deletion button
                        "component_type": Button,
                        "value": "NO",
                        "variant": "huggingface",
                        "elem_classes": ["delete-button"],
                        "size": "sm"
                    }
            }
            else:
                message = f'❌ Attribute `users` should not be None.'
                raise ValueError(message)
            params_dict: Dict[str, Dict[str, Any]] = {}
            with Row(visible=True, elem_id='user_row') as user_row:
                params_dict['user_row'] = user_row
                with Column(scale=1):
                    with Accordion('⚙️ User Creation'):
                        Markdown('Input a user name.')
                        params_dict['user_name_input'] = utils.create_component(user_interface_config['user_name_input'])
                with Column(scale=2):
                    with Accordion('📝 Available users'):
                        Markdown('Select your preferred user or delete selected user')
                        params_dict['user_radio'] = utils.create_component(user_interface_config['user_radio'])
                        params_dict['delete_user_button'] = utils.create_component(user_interface_config['delete_user_button'])
            with Modal(visible=False) as modal:
                params_dict['confirm_user_delete_modal'] = modal
                params_dict['confirm_user_delete_text'] = utils.create_component(user_interface_config['confirm_user_delete_text'])
                with Row():
                    params_dict['confirm_user_delete_button'] = utils.create_component(user_interface_config['confirm_user_delete_button'])
                    params_dict['cancel_user_delete_button'] = utils.create_component(user_interface_config['cancel_user_delete_button'])
            return params_dict
        except Exception as e:
            logger.error(f'❌ Problem creating user interface: `{str(e)}`')
            raise