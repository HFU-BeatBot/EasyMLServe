import os
import librosa as librosa

from easymlserve.ui import GradioEasyMLUI, QtEasyMLUI
from easymlserve.ui.type import *

from api_schema import *
from pandas import DataFrame


class BeatBotUI(GradioEasyMLUI):
    """
    This UI accepts any music file, process it and shows the genre of the music
    """

    def prepare_request(self, file: str, music_array: str) -> APIRequest:
        if file:
            array = self.preprocess_music(file)
            os.remove(file)
            return {"use_python_model": True, "music_array": array}
        elif music_array:
            array = music_array.split(",")
            return {"music_array": array}

    def process_response(self, request: APIRequest, response: APIResponse) -> Plot:
        """Process REST API response by searching the image."""
        genre = response["genre"]
        path_to_img =  "assets/genres/404.png"
        if (genre in ("Blues Classical Country Disco HipHop Jazz Metal Pop Reggae Rock").split()):
            path_to_img = "assets/genres/" + genre.lower() + ".png"

        data = DataFrame()
        data["Genre"] = response["confidences"].keys()
        data["Genre Strength"] = response["confidences"].values()

        return (genre,path_to_img,data)

    def preprocess_music(self, songname: str) -> np.ndarray:
        # compute features from music file
        y, sr = librosa.load(songname, mono=True, duration=3)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        array = []
        for e in mfcc:
            array.append(str(np.mean(e)))
            array.append(str(np.std(e)))

        return array


if __name__ == "__main__":
    input_schema = {
        "file": MusicFile(name="Music File"),
        "music_array": TextLong(name="Java Music Array"),
    }
    output_schema = [
        Text(name="Recognized main genre"),
        ImageFile(),
        BarPlot(x_label="Genre", y_label="Genre Strength", vertical=False)
    ]
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
