from flask_restx import Resource
from flask_restx.namespace import Namespace


api = Namespace("")


class OptionsResource(Resource):
    @api.hide
    def options(self):
        return None, 200
