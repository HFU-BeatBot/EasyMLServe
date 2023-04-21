from easymlserve.ui import GradioEasyMLUI, QtEasyMLUI
from easymlserve.ui.type import *

from api_schema import *


class BeatBotUI(GradioEasyMLUI):
    """
    This UI accepts any music file, process it and shows the genre of the music
    """

    def prepare_request(self, path: str) -> APIRequest:
        print(path)
        return {"music_array": "test"}

    def process_response(self, request: APIRequest, response: APIResponse) -> Plot:
        """Process REST API response by searching the image."""
        genre = response["genre"]
        path_to_img =  "assets/genres/404.png"
        if (genre in ("blues classical country disco hiphop jazz metal pop reggae rock").split()):
            path_to_img = "assets/genres/" + genre + ".png"
        
        return genre, path_to_img


if __name__ == "__main__":
    input_schema = {
        "file": MusicFile(name="Music File"),
    }
    output_schema = [Text(name="Recognized genre"), ImageFile(name="Genre Image")]
    gradio_interface_args = {"allow_flagging": "never"}
    gradio_launch_args = {
        "server_name": "0.0.0.0",
        "server_port": 8080,
        "favicon_path": "assets/favicon.ico",
    }
    app = BeatBotUI(
        name="HFU-BeatBot",
        input_schema=input_schema,
        output_schema=output_schema,
        gradio_interface_args=gradio_interface_args,
        gradio_launch_args=gradio_launch_args,
        rest_api_port=8000,
    )
    app.run()
