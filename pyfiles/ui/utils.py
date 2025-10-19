## pyfiles.ui.utils
## This file creates methods to be used through the Gradio app interfaces.

## External imports
from gradio import Row, Button, Markdown
from gradio_modal import Modal # type: ignore
from typing import List, Dict, Any, Tuple

## Internal imports
from pyfiles.bases.codebases import Codebases
from pyfiles.bases.logger import logger
from pyfiles.bases.users import Users

## Toggle the delete button based on available items
def toggle_del_button(
        list_in: List[Any]
    ) -> Button:
        """
        Toggle the delete button interactivity based on the length of the given list.

        Args
        ------------
            list_in: List[Any]:
                A list of available items.

        Returns
        ------------
            Button:
                The resulting button.
            
        Raises
        ------------
            Exception: 
                If toggling the delete button fails, error is logged and raised.
        """
        try:
            ## If only one item available, make button non-interactive
            del_button = Button(interactive=False) if len(list_in)<=1 else Button(interactive=True)
            return del_button
        except Exception as e:
            logger.error(f'❌ Problem toggling delete button: `{str(e)}`')
            raise

## Trigger after canceling the deletion of an item
def cancel_deletion_trigger(
) -> Modal:
    """
    Create the confirm deletion modal for user deletion.

    Returns
    ------------
        Modal:
            The modal to handle after canceling deletion.
        
    Raises
    ------------
        Exception: 
            If canceling the deletion fails, error is logged and raised.
    """
    try:
        return Modal(visible=False)
    except Exception as e:
        logger.error(f'❌ Problem triggering canceling deletion: `{str(e)}`')
        raise

## Create a Gradio component
def create_component(
    config: Dict[str, dict]
) -> Any:
    """
    Create a Gradio component given the config dictionary.

    Args
    ------------
        config: Dict[str, dict]
            The dictionary defining the component attributes.

    Returns
    ------------
        Any:
            Any Gradio component.
        
    Raises
    ------------
        Exception: 
            If creating the Gradio component fails, error is logged and raised.
    """
    try:
        component_type: Any = config.get("component_type")
        params: Dict[str, Any] = {k: v for k, v in config.items() if k != "component_type"}
        return component_type(**params)
    except Exception as e:
        logger.error(f'❌ Problem creating Gradio component: `{str(e)}`')
        raise

## Toggle the visibility of the Gradio interfaces
def toggle_visibility(
) -> List[Row]:
    """
    Toggle the visibility of interface rows.

    Returns
    ------------
        List[Row]:
            A list of interface rows with visibility definitions.
        
    Raises
    ------------
        Exception: 
            If toggling the visibility of interface rows fails, error is logged and raised.
    """
    try:
        vis_list: List[Row] = [Row(visible=False) for _ in range(0,3)]
        vis_list.extend([Row(visible=True)])
        return vis_list
    except Exception as e:
        logger.error(f'❌ Problem toggling visibility for interface rows: `{str(e)}`')
        raise

## Get the current user
async def handle_current_user(
    users: Users | None, 
    user: str, 
    docs: str, 
    external_docs: List[str]
) -> Tuple[Codebases, Codebases]:
    """
    Get the codebase handlers for the main and external codebases of the selected user.

    Args
    ------------
        users: Users
            The users handler.
        user: str
            The selected user.
        docs: str
            The selected main codebase. 
        external_docs: List[str]
            A list of the selected external codebases.

    Returns
    ------------
        Tuple[Codebases, Codebases]:
            A tuple of the codebase handlers for the main and external codebases.
        
    Raises
    ------------
        Exception: 
            If getting the current user fails, error is logged and raised.
    """
    try:
        if users!=None:
            current_user, current_ext_docs = await users.get_current_user(
                name=user,
                selected_codebase_name=docs,
                selected_ext_codebases=external_docs
            )
            return current_user, current_ext_docs
        else:
            message = f'❌ Attribute `users` should not be None.'
            raise ValueError(message)
    except Exception as e:
        logger.error(f'❌ Problem getting current user: `{str(e)}`')
        raise