import os
import numpy as np
import tensorflow as tf

from easymlserve import EasyMLServer, EasyMLService

from api_schema import APIRequest, APIResponse
from joblib import load


class GenreDetectionService(EasyMLService):
    """Genre detection service."""

    def load_model(self):
        # get path
        path_to_folder = os.path.dirname(os.path.abspath(__file__))

        # load legacy scaler
        self.legacy_model = tf.keras.models.load_model(
            path_to_folder + "/legacy_model.h5"
        )

        # load fma model
        self.fma_model = tf.keras.models.load_model(path_to_folder + "/fma_model.h5")

        # load legacy scaler
        self.legacy_scaler = load(path_to_folder + "/legacy_scaler.bin")

        # load fma scaler
        self.fma_scaler = load(path_to_folder + "/fma_scaler.bin")

    def process(self, request: APIRequest) -> APIResponse:
        """Process REST API request and return genre."""

        np_array = np.array([request.music_array])

        if request.use_legacy_model:
            genres = "Blues Classical Country Disco HipHop Jazz Metal Pop Reggae Rock"
            main_genre, confidences = self.get_return_values(
                np_array, self.legacy_scaler, self.legacy_model, genres
            )
        else:
            genres = "Blues Classical Country Disco HipHop Jazz Metal Pop Reggae Rock"
            main_genre, confidences = self.get_return_values(
                np_array, self.fma_scaler, self.fma_model, genres
            )

        return {"genre": main_genre, "confidences": confidences}

    def get_return_values(self, np_array, scaler, model, genres):
        np_array = scaler.transform(np_array)
        prediction = model.predict(np_array)
        genre = np.argmax(prediction[0])

        genres = genres.split()

        confidences = dict()

        for x in range(len(genres)):
            confidences[genres[x]] = float(prediction[0][x])

        return genres[genre], confidences


service = GenreDetectionService()
server = EasyMLServer(service, uvicorn_args={"host": "0.0.0.0", "port": 8000})
server.deploy()
