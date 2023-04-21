import numpy as np
import tensorflow as tf

from easymlserve import EasyMLServer, EasyMLService

from api_schema import APIRequest, APIResponse


class GenreDetectionService(EasyMLService):
    """Genre detection service."""

    def load_model(self):
        self.model = tf.keras.models.load_model("model.h5")

    def process(self, request: APIRequest) -> APIResponse:
        """Process REST API request and return genre."""
        prediction = self.model.predict(request.music_array)

        return {"genre": prediction}


service = GenreDetectionService()
server = EasyMLServer(service, uvicorn_args={"host": "0.0.0.0", "port": 8000})
server.deploy()
