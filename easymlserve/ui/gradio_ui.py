from typing import Dict, List

import gradio

from . import BaseEasyMLUI


class GradioEasyMLUI(BaseEasyMLUI):
    """Gradio UI class to display a Gradio Web UI."""

    def __init__(self,
                 gradio_interface_args: Dict = {},
                 gradio_launch_args: Dict = {},
                 **kwargs):
        """Initialize Gradio UI class.

        Args:
            gradio_interface_args (Dict, optional): Gradio Interface arguments. Defaults to {}.
            gradio_launch_args (Dict, optional): Gradio launch arguments. Defaults to {}.
        """
        super().__init__(**kwargs)
        self.gradio_interface_args = gradio_interface_args
        self.gradio_launch_args = gradio_launch_args
        inputs = [self.input_schema[param].to_gradio()
                  for param in self.input_schema]
        outputs = [output.to_gradio()
                   for output in self.output_schema]
        self.app = gradio.Interface(self.clicked,
                                    title=self.name,
                                    inputs=inputs, outputs=outputs,
                                    theme=gradio.themes.Default().set(
                                        loader_color="#03B670",
                                        loader_color_dark="#03B670",
                                        button_primary_text_color="#FFFFFF",
                                        button_primary_text_color_dark="#FFFFFF",
                                        button_primary_background_fill="#03B670",
                                        button_primary_background_fill_dark="#03B670",
                                        button_primary_background_fill_hover="#008A54",
                                        button_primary_background_fill_hover_dark="#008A54",
                                        button_primary_border_color="*button_primary_background_fill",
                                        button_primary_border_color_dark="*button_primary_background_fill",
                                        button_primary_border_color_hover="*button_primary_background_fill_hover",
                                        button_primary_border_color_hover_dark="*button_primary_background_fill_hover",
                                        button_secondary_text_color="#FFFFFF",
                                        button_secondary_text_color_dark="#FFFFFF",
                                        button_secondary_background_fill="#003DA5",
                                        button_secondary_background_fill_dark="#003DA5",
                                        button_secondary_background_fill_hover="#000A29",
                                        button_secondary_background_fill_hover_dark="#000A29",
                                        button_secondary_border_color="*button_secondary_background_fill",
                                        button_secondary_border_color_dark="*button_secondary_background_fill",
                                        button_secondary_border_color_hover="*button_secondary_background_fill_hover",
                                        button_secondary_border_color_hover_dark="*button_secondary_background_fill_hover",
                                    ),
                                    **gradio_interface_args)

    def run(self):
        """Run Gradio UI web server."""
        self.app.launch(**self.gradio_launch_args)

    def clicked(self, *kwargs) -> List:
        """Gradio clicked process event.

        Returns:
            List: List of UI elements to display.
        """
        parent_kwargs = {}
        for i, key in enumerate(self.input_schema):
            parent_kwargs[key] = kwargs[i]
        return super().clicked(**parent_kwargs)
