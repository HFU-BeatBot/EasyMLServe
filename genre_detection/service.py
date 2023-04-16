import os

import numpy as np

from easymlserve import EasyMLServer, EasyMLService

from api_schema import APIRequest, APIResponse


class HistogramImageService(EasyMLService):
    """Histogram calculation example service."""

    def load_model(self):
        model_path = os.path.join('model', 'model.xml')
        #TODO Save to self.model

    def process(self, request: APIRequest) -> APIResponse:
        """ Process REST API request and return genre."""
        #TODO get genre
        #detections = self.model.detectGenre(request)
        
        response = {'genre': ['metal']}
        print(response)
        return response


service = HistogramImageService()
server = EasyMLServer(service, uvicorn_args={'host': '0.0.0.0', 'port': 8000})
server.deploy()