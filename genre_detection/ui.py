import os
import librosa as librosa

from easymlserve.ui import GradioEasyMLUI, QtEasyMLUI
from easymlserve.ui.type import *
from joblib import load

from api_schema import *


class BeatBotUI(GradioEasyMLUI):
    """
    This UI accepts any music file, process it and shows the genre of the music
    """

    def prepare_request(self, file: str, music_array: str) -> APIRequest:
        if file:
            array = self.preprocess_music(file)
            os.remove(file)
            return {"use_python_model": True, "music_array": array[0].tolist()}
        elif music_array:
            array = music_array.split(",")
            return {"music_array": array}

    def process_response(self, request: APIRequest, response: APIResponse) -> Plot:
        """Process REST API response by searching the image."""
        genre = response["genre"]
        path_to_img =  "assets/genres/404.png"
        if (genre in ("Blues Classical Country Disco HipHop Jazz Metal Pop Reggae Rock").split()):
            path_to_img = "assets/genres/" + genre.lower() + ".png"

        return genre, path_to_img, float("{:.4f}".format(response["confidence"][genre]))

    def preprocess_music(self, songname: str) -> np.ndarray:
        # load scaler
        scaler = load(os.path.dirname(os.path.abspath(__file__)) + "/scaler.bin")

        # compute features from music file
        y, sr = librosa.load(songname, mono=True, duration=3)
        chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
        rmse = librosa.feature.rms(y=y)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        array = [np.mean(chroma_stft), np.mean(rmse), np.mean(spec_cent), np.mean(spec_bw), np.mean(rolloff), np.mean(zcr)]

        for e in mfcc:
            array.append(np.mean(e))

        np_array = np.array([array])
        np_array = scaler.transform(np_array)
        return np_array


if __name__ == "__main__":
    input_schema = {
        "file": MusicFile(name="Music File"),
        "music_array": TextLong(name="Java Music Array"),
    }
    output_schema = [
        Text(name="Recognized genre"),
        ImageFile(),
        Range(0, 1, float, name="Confidence"),
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
