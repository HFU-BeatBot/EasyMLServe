import os
import numpy as np
import tensorflow as tf

from easymlserve import EasyMLServer, EasyMLService

from api_schema import APIRequest, APIResponse
from joblib import load


class GenreDetectionService(EasyMLService):
    """Genre detection service."""

    def load_model(self):
        self.python_model = tf.keras.models.load_model(
            os.path.dirname(os.path.abspath(__file__))
            + "/model.h5"  # TODO: "/python_model.h5"
        )

        self.java_model = tf.keras.models.load_model(
            os.path.dirname(os.path.abspath(__file__))
            + "/model.h5"  # TODO: "/java_model.h5"
        )

        # load scaler
        self.scaler = load(os.path.dirname(
            os.path.abspath(__file__)) + "/scaler.bin")

    def process(self, request: APIRequest) -> APIResponse:
        """Process REST API request and return genre."""

        np_array = np.array([request.music_array])
        np_array = self.scaler.transform(np_array)

        if request.use_python_model:
            prediction = self.python_model.predict(np_array)
        else:
            prediction = self.java_model.predict(np_array)
        genre = np.argmax(prediction[0])

        genres = ("Blues Classical Country Disco HipHop Jazz Metal Pop Reggae Rock").split()

        confidences = dict()

        for x in range(len(genres)):
            confidences[genres[x]] = float(prediction[0][x])

        return {"genre": genres[genre], "confidences": confidences}


service = GenreDetectionService()
server = EasyMLServer(service, uvicorn_args={"host": "0.0.0.0", "port": 8000})
server.deploy()
