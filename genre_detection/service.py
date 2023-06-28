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
        """Called once at startup. Loads all models and scalers used in the service.
        The scalers transform the received values so that the model can process them."""

        # get path of this file
        path_to_folder = os.path.dirname(os.path.abspath(__file__))

        # load librosa gtzan model & scaler
        self.librosa_gtzan_model = tf.keras.models.load_model(
            path_to_folder + "/librosa_gtzan_model.h5"
        )
        self.librosa_gtzan_scaler = load(path_to_folder + "/librosa_gtzan_scaler.bin")

        # load librosa fma model & scaler
        self.librosa_fma_model = tf.keras.models.load_model(
            path_to_folder + "/librosa_fma_model.h5"
        )
        self.librosa_fma_scaler = load(path_to_folder + "/librosa_fma_scaler.bin")

        # load jlibrosa gtzan model & scaler
        self.jlibrosa_gtzan_model = tf.keras.models.load_model(
            path_to_folder + "/jlibrosa_gtzan_model.h5"
        )
        self.jlibrosa_gtzan_scaler = load(path_to_folder + "/jlibrosa_gtzan_scaler.bin")

        # load jlibrosa fma model & scaler
        self.jlibrosa_fma_model = tf.keras.models.load_model(
            path_to_folder + "/jlibrosa_fma_model.h5"
        )
        self.jlibrosa_fma_scaler = load(path_to_folder + "/jlibrosa_fma_scaler.bin")

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
                np_array,
                self.librosa_fma_scaler,
                self.librosa_fma_model,
                constants.FMA_GENRES,
            )
        elif request.model_to_use == 2:  # JLibrosa GTZAN
            main_genre, confidences = self.get_return_values(
                np_array,
                self.jlibrosa_gtzan_scaler,
                self.jlibrosa_gtzan_model,
                constants.GTZAN_GENRES,
            )
        elif request.model_to_use == 3:  # JLibrosa FMA
            main_genre, confidences = self.get_return_values(
                np_array,
                self.jlibrosa_fma_scaler,
                self.jlibrosa_fma_model,
                constants.FMA_GENRES,
            )
        else:  # Librosa GTZAN
            main_genre, confidences = self.get_return_values(
                np_array,
                self.librosa_gtzan_scaler,
                self.librosa_gtzan_model,
                constants.GTZAN_GENRES,
            )

        # generate the response as a simple json string
        return {"genre": main_genre, "confidences": confidences}

    def get_return_values(
        self, np_array, scaler, model, genres=constants.GTZAN_GENRES
    ) -> tuple[str, dict]:
        """Process the np_array with the mfcc values and return the main_genre as str and dictionary with the confidences

        Args:
            np_array (np_array): mfcc values
            scaler: The scaler to use with the model
            model: The model used to predict the genres
            genres (list[str], optional): The genres which are returned by the model. Defaults to constants.GTZAN_GENRES.

        Returns:
            tuple[str, dict]: main_genre and confidences with genres as keys
        """

        # up or downscale the values to match the trainigs data
        np_array = scaler.transform(np_array)

        # get the prediction
        prediction = model.predict(np_array)

        # get the highest value, as this is the main genre
        genre = np.argmax(prediction[0])

        confidences = dict()

        # enter all the confidences into the dict
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
