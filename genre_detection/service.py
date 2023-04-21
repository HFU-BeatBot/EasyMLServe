import os
import numpy as np
import tensorflow as tf

from easymlserve import EasyMLServer, EasyMLService

from api_schema import APIRequest, APIResponse


class GenreDetectionService(EasyMLService):
    """Genre detection service."""

    def load_model(self):
        self.model = tf.keras.models.load_model(
            os.path.dirname(os.path.abspath(__file__)) + "/model.h5"
        )

    def process(self, request: APIRequest) -> APIResponse:
        """Process REST API request and return genre."""
        prediction = self.model.predict(request.music_array)

        genre = np.argmax(prediction[0])
        confidence = prediction[0][genre]

        genre = ("blues classical country disco hiphop jazz metal pop reggae rock").split()[genre]
        return {"genre": genre, "confidence": confidence}


service = GenreDetectionService()
server = EasyMLServer(service, uvicorn_args={"host": "0.0.0.0", "port": 8000})
server.deploy()
