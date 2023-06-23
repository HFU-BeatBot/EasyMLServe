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

    def prepare_request(
        self, music_array: str, model_to_use: int
    ) -> APIRequest:  ###TODO: music_array str?
        """Create a simple json string that will be send to the service/server

        Args:
            music_array (str): Array of all 20 mfcc values mean and std
            model_to_use (int): The model which should be used by the service/server for interpreting

        Returns:
            APIRequest: json string
        """

        return {"model_to_use": model_to_use, "music_array": music_array}

    def process_response(self, request: APIRequest, response: APIResponse) -> Plot:
        """Process REST API response by extracting the valuable informations.

        Args:
            request (APIRequest): The request we sent to the service/server
            response (APIResponse): The response of the service/server

        Returns:
            Plot: The information of what we want to show in the ui
        """

        genre = response["genre"]
        path_to_img = "assets/genres/404.png"  # set default image (only shown when no genre image is available)

        used_model = request["model_to_use"]
        genres = constants.GTZAN_GENRES
        if used_model == 1 or used_model == 3:
            genres = constants.FMA_GENRES

        if genre in genres:
            path_to_img = "assets/genres/" + genre.lower() + ".png"

        # remove the lowest values of confidences
        while len(response["confidences"]) > 5:
            min_key = min(
                response["confidences"].keys(), key=lambda k: response["confidences"][k]
            )
            del response["confidences"][min_key]

        # create a DataFrame to visualize the (highest) confidences in a bar chart
        data = DataFrame()
        data["Genre"] = response["confidences"].keys()
        data["Genre Strength"] = response["confidences"].values()

        return (genre, path_to_img, data)

    def preprocess_music(self, file: str):
        """Compute features of music file, splits the song in multiple snippets and extracts the information of them. The duration of the snippet is specifyed in the constants.py file.

        Args:
            file (str): Path to the sound file

        Returns:
            list: List of mfcc lists
        """

        max_duration = constants.TRAINED_MUSIC_DURATION_IN_SECONDS
        offset = 0
        song_duration = librosa.get_duration(path=file)

        arrays = list()

        # if the given song is shorter than the duration the model is trained for we send it anyways as we get a result also. It might not be the best result but still we want it.
        if song_duration <= max_duration:
            array = self.get_song_array(file)
            arrays.append(array)
            return arrays

        # split the song to max_duration and save them in the return array
        while song_duration - offset > max_duration:
            array = self.get_song_array(file, max_duration, offset)
            arrays.append(array)
            offset += max_duration

        return arrays

    def get_song_array(
        self, file: str, duration: int = None, offset: int = None
    ) -> list:
        """Generates the mfcc values of the given file in the specified snippet

        Args:
            file (str): Path to the sound file
            duration (int, optional): Duration in seconds of the processed snippet. Defaults to None.
            offset (int, optional): Offset in seconds. Defaults to None.

        Returns:
            list: MFCC Values of the snippet in the order: [mfcc1_mean,mfcc1_std,mfcc2_mean,...,mfcc20_std]
        """

        y, sr = librosa.load(file, mono=True, duration=duration, offset=offset)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        array = []
        for e in mfcc:
            array.append(str(np.mean(e)))
            array.append(str(np.std(e)))
        return array


if __name__ == "__main__":
    # creates basically the left ui side
    input_schema = {
        "file": MusicFile(name="Music File"),
        "music_array": TextLong(name="Music Array"),
        "model_to_use": SingleChoice(
            name="Model to use",
            choices=[
                "Librosa - GTZAN",
                "Librosa - FMA",
                "JLibrosa - GTZAN",
                "JLibrosa - FMA",
            ],
        ),
    }

    # creates basically the right ui side
    output_schema = [
        Text(name="Recognized main genre"),
        ImageFile(),
        BarPlot(x_label="Genre", y_label="Genre Strength", vertical=False),
    ]

    # create a more matching theme than the default one. It uses the colors of hfu and hfm.
    theme = gradio.themes.Default().set(
        loader_color=constants.COLOR_HFU,
        loader_color_dark=constants.COLOR_HFU,
        button_primary_text_color="#FFFFFF",
        button_primary_text_color_dark="#FFFFFF",
        button_primary_background_fill=constants.COLOR_HFU,
        button_primary_background_fill_dark=constants.COLOR_HFU,
        button_primary_background_fill_hover=constants.COLOR_HFU_DARK,
        button_primary_background_fill_hover_dark=constants.COLOR_HFU_DARK,
        button_primary_border_color="*button_primary_background_fill",
        button_primary_border_color_dark="*button_primary_background_fill",
        button_primary_border_color_hover="*button_primary_background_fill_hover",
        button_primary_border_color_hover_dark="*button_primary_background_fill_hover",
        button_secondary_text_color="#FFFFFF",
        button_secondary_text_color_dark="#FFFFFF",
        button_secondary_background_fill=constants.COLOR_HFM,
        button_secondary_background_fill_dark=constants.COLOR_HFM,
        button_secondary_background_fill_hover=constants.COLOR_HFM_DARK,
        button_secondary_background_fill_hover_dark=constants.COLOR_HFM_DARK,
        button_secondary_border_color="*button_secondary_background_fill",
        button_secondary_border_color_dark="*button_secondary_background_fill",
        button_secondary_border_color_hover="*button_secondary_background_fill_hover",
        button_secondary_border_color_hover_dark="*button_secondary_background_fill_hover",
    )

    # specify some server arguments
    gradio_interface_args = {"allow_flagging": "never", "theme": theme}
    gradio_launch_args = {
        "server_name": "0.0.0.0",
        "server_port": 8080,
        "favicon_path": "assets/beat_bot_icon.png",  # set favicon
    }

    # create the ui
    app = BeatBotUI(
        name="HFU-BeatBot",
        input_schema=input_schema,
        output_schema=output_schema,
        gradio_interface_args=gradio_interface_args,
        gradio_launch_args=gradio_launch_args,
        rest_api_port=8000,  # specify the port of the service
    )

    # run the server including the ui
    app.run()
