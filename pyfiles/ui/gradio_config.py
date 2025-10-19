### pyfiles.ui.gradio_config
## This file creates the theme for the Gradio app

## External imports
from gradio.themes import Base, Ocean # type: ignore

## Internal imports
from pyfiles.bases.logger import logger

## Create delete buttons (red)
custom_css: str = """
.delete-button {
    background-color: darkred !important;
    border-color: darkred !important;
}
.icon-color {
    color: #00DDFF
}
"""

## Create the Gradio theme
class Config:
    """
    A class to create a Gradio theme to be pass to a Gradio app.

    Attributes
    ------------
        custom_css: str
            The custom CSS to pass to the Gradio app.
            Default to def`ining one element for delete buttons.
        theme: Base
            A base Gradio theme.
    """
    def __init__(
        self, 
        custom_css: str = custom_css
    ):
        """
        Initialize the Gradio config.

        Args
        ------------
            custom_css (Optional): str
                The custom CSS to pass to the Gradio app.
                Default to defining one element for delete buttons.
            
        Raises
        ------------
            Exception: 
                If initializing the Gradio config fails, error is logged and raised.
        """
        try:
            self.custom_css: str = custom_css
            ## Set the theme
            self.theme: Base = Ocean(
                primary_hue="indigo",
                neutral_hue="neutral",
                secondary_hue="sky",
                spacing_size='lg',
                radius_size='lg',
                text_size='lg',
            ).set(
                code_background_fill='*primary_300',
                code_background_fill_dark='*primary_950',
                block_background_fill='*neutral_50',
                block_background_fill_dark='*neutral_950',
                block_border_color='*primary_300',
                block_border_color_dark='*primary_950',
                block_label_background_fill='none',
                block_label_background_fill_dark='none',
                block_label_border_color='*primary_300',
                block_label_border_color_dark='*primary_950',
                block_radius='calc(*radius_sm - 1px) 0 calc(*radius_sm - 1px) 0',
                block_title_border_color='*primary_300',
                block_title_border_color_dark='*primary_950',
                block_title_border_width='1px',
                block_title_border_width_dark='1px',
                block_title_padding='*spacing_sm',
                block_title_radius='calc(*radius_sm - 1px) 0 calc(*radius_sm - 1px) 0',
                panel_background_fill='*primary_50',
                panel_background_fill_dark='*neutral_900',
                panel_border_color='*primary_300',
                panel_border_color_dark='*primary_950',
                panel_border_width='1px',
                panel_border_width_dark='1px',
                section_header_text_size='*text_lg',
                accordion_text_color='*primary_500',
                accordion_text_color_dark='*primary_500',
                checkbox_background_color_selected='*primary_600',
                checkbox_border_color_focus='*neutral_300',
                checkbox_border_color_focus_dark='*neutral_700',
                checkbox_border_color_selected='*neutral_300',
                checkbox_border_color_selected_dark='*neutral_700',
                checkbox_border_width='1px',
                checkbox_border_width_dark='1px',
                checkbox_label_background_fill='*primary_400',
                checkbox_label_background_fill_dark='*primary_500',
                checkbox_label_background_fill_hover='*primary_200',
                checkbox_label_background_fill_hover_dark='*primary_300',
                checkbox_label_background_fill_selected='*secondary_300',
                checkbox_label_background_fill_selected_dark='*secondary_500',
                checkbox_label_border_width='*input_border_width',
                input_background_fill_dark='*neutral_900',
                input_background_fill_focus_dark='*neutral_900',
                input_border_color='*neutral_200',
                input_border_color_dark='*neutral_800',
                input_border_color_focus_dark='*secondary_950',
                input_border_width='1px',
                input_border_width_dark='1px',
                input_radius='calc(*radius_sm - 1px) 0 calc(*radius_sm - 1px) 0',
                button_border_width='2px',
                button_border_width_dark='2px',
                button_transform_hover='scale(1.01)',
                button_primary_background_fill='linear-gradient(120deg, *primary_500 0%, *secondary_300 50%, *primary_500 100%)',
                button_primary_background_fill_dark='linear-gradient(120deg, *primary_600 0%, *secondary_600 25%, *secondary_500 50%, *secondary_600 75%, *primary_600 100%)',
                button_primary_background_fill_hover='*secondary_300',
                button_primary_background_fill_hover_dark='*secondary_500',
                button_primary_border_color_dark='*primary_900',
                button_primary_border_color_hover='*primary_300',
                button_secondary_background_fill='linear-gradient(120deg, *secondary_500 0%, *primary_300 50%, *secondary_500 100%)',
                button_secondary_background_fill_dark='linear-gradient(120deg, *secondary_600 0%, *primary_600 25%, *primary_500 50%, *primary_600 75%, *secondary_600 100%)',
                button_secondary_background_fill_hover='*primary_300',
                button_secondary_background_fill_hover_dark='*primary_500',
                button_secondary_border_color='*secondary_500',
                button_secondary_border_color_dark='*secondary_900',
                button_secondary_border_color_hover='*secondary_300',
                button_secondary_border_color_hover_dark='*secondary_500',
            )
        except Exception as e:
            logger.error(f'❌ Problem creating custom Gradio theme: `{str(e)}`')
            raise
