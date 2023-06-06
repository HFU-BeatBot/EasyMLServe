import os
from typing import List
import librosa as librosa

from easymlserve.ui import GradioEasyMLUI, QtEasyMLUI
from easymlserve.ui.type import *

from api_schema import *
from pandas import DataFrame

import constants


class BeatBotUI(GradioEasyMLUI):
    """
    This UI accepts any music file, process it and shows the genre of the music
    """

    def clicked(self, *kwargs) -> List:
        """Gradio clicked process event to prepare and send REST API request.

        Returns:
            List: List of UI elements to display.
        """
        parent_kwargs = {}
        for i, key in enumerate(self.input_schema):
            parent_kwargs[key] = kwargs[i]

        file = parent_kwargs["file"]
        music_array = parent_kwargs["music_array"]
        model_to_use = parent_kwargs["model_to_use"]

        if file:
            arrays = self.preprocess_music(file)
            sum_array = {}
            for array in arrays:
                request = self.prepare_request(array, model_to_use)
                response = self.call_process_api(request)

                # sum up all confidences
                for x in response["confidences"]:
                    if x in sum_array.keys():
                        sum_array[x] += response["confidences"][x]
                    else:
                        sum_array[x] = response["confidences"][x]

            # mean of all confidences
            for key in sum_array.keys():
                sum_array[key] /= len(arrays)
            response = {
                "genre": max(sum_array, key=sum_array.get),
                "confidences": sum_array,
            }

            # Delete the temorary file
            os.remove(file)

        elif music_array:
            request = self.prepare_request(**parent_kwargs)
            response = self.call_process_api(request)

        else:
            # Create little help text
            response = {
                "genre": "You should really upload a song or paste in a song array :-)",
                "confidences": {},
            }

        return self.process_response(request, response)

    def prepare_request(self, music_array: str, model_to_use: int) -> APIRequest:
        return {"model_to_use": model_to_use, "music_array": music_array}

    def process_response(self, request: APIRequest, response: APIResponse) -> Plot:
        """Process REST API response by searching the image."""
        genre = response["genre"]
        path_to_img = "assets/genres/404.png"  # set default image (only shown when no genre image is available)

        genres = constants.GENRES

        if genre in genres:
            path_to_img = "assets/genres/" + genre.lower() + ".png"

        # remove the lowest values of confidences
        while len(response["confidences"]) > 5:
            min_key = min(
                response["confidences"].keys(), key=lambda k: response["confidences"][k]
            )
            del response["confidences"][min_key]

        data = DataFrame()
        data["Genre"] = response["confidences"].keys()
        data["Genre Strength"] = response["confidences"].values()

        return (genre, path_to_img, data)

    def preprocess_music(self, file: str):
        """Compute features of music file

        Returns:
            List: List of Music arrays.
        """
        max_duration = constants.TRAINED_MUSIC_DURATION_IN_SECONDS
        offset = 0
        song_duration = librosa.get_duration(path=file)

        arrays = list()

        if song_duration <= max_duration:
            array = self.get_song_array(file)
            arrays.append(array)
            return arrays

        while song_duration - offset > max_duration:
            array = self.get_song_array(file, max_duration, offset)
            arrays.append(array)
            offset += max_duration

        return arrays

    def get_song_array(self, file, duration=None, offset=None):
        y, sr = librosa.load(file, mono=True, duration=duration, offset=offset)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        array = []
        for e in mfcc:
            array.append(str(np.mean(e)))
            array.append(str(np.std(e)))
        return array


if __name__ == "__main__":
    input_schema = {
        "file": MusicFile(name="Music File"),
        "music_array": TextLong(name="Music Array"),
        "model_to_use": SingleChoice(
            name="Model to use",
            choices=["Librosa - GTZAN", "Librosa - FMA", "JLibrosa - GTZAN"],
        ),
    }
    output_schema = [
        Text(name="Recognized main genre"),
        ImageFile(),
        BarPlot(x_label="Genre", y_label="Genre Strength", vertical=False),
    ]
    gradio_interface_args = {"allow_flagging": "never"}
    gradio_launch_args = {
        "server_name": "0.0.0.0",
        "server_port": 8080,
        "favicon_path": "assets/beat_bot_icon.png",
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
