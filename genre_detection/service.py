import os
import numpy as np
import tensorflow as tf

from easymlserve import EasyMLServer, EasyMLService

from api_schema import APIRequest, APIResponse
from joblib import load

import constants


class GenreDetectionService(EasyMLService):
    """Genre detection service."""

    def load_model(self):
        """Loads all models which are used in the service. Called once on start up."""

        # get path of this file
        path_to_folder = os.path.dirname(os.path.abspath(__file__))

        # load gtzan model & scaler
        self.gtzan_model = tf.keras.models.load_model(
            path_to_folder + "/gtzan_model.h5"
        )
        self.gtzan_scaler = load(path_to_folder + "/gtzan_scaler.bin")

        # load fma model & scaler
        self.fma_model = tf.keras.models.load_model(path_to_folder + "/fma_model.h5")
        self.fma_scaler = load(path_to_folder + "/fma_scaler.bin")

        # load jlibrosa model & scaler
        self.jlibrosa_model = tf.keras.models.load_model(
            path_to_folder + "/jlibrosa_model.h5"
        )
        self.jlibrosa_scaler = load(path_to_folder + "/jlibrosa_scaler.bin")

    def process(self, request: APIRequest) -> APIResponse:
        """Process REST API request and return genre.

        Args:
            request (APIRequest): The request received

        Returns:
            APIResponse: The response that will be send
        """

        np_array = np.array([request.music_array])

        if request.model_to_use == 1:  # Librosa FMA
            main_genre, confidences = self.get_return_values(
                np_array, self.fma_scaler, self.fma_model
            )
        elif request.model_to_use == 2:  # JLibrosa GTZAN
            main_genre, confidences = self.get_return_values(
                np_array, self.jlibrosa_scaler, self.jlibrosa_model
            )
        else:  # Librosa GTZAN
            main_genre, confidences = self.get_return_values(
                np_array, self.gtzan_scaler, self.gtzan_model
            )

        # generate the response as a simple json string
        return {"genre": main_genre, "confidences": confidences}

    def get_return_values(self, np_array, scaler, model, genres=constants.GENRES):
        np_array = scaler.transform(np_array)
        prediction = model.predict(np_array)
        genre = np.argmax(prediction[0])

        confidences = dict()

        for x in range(len(genres)):
            confidences[genres[x]] = float(prediction[0][x])

        return genres[genre], confidences


if __name__ == "__main__":
    # create the service
    service = GenreDetectionService()

    # create a server with the service and some arguments
    server = EasyMLServer(service, uvicorn_args={"host": "0.0.0.0", "port": 8000})
    # start the server
    server.deploy()
