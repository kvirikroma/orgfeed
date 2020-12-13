from flask import Blueprint, current_app
from flask_restx import Api

from .attachment_api import api as attachment_api
from .employee_api import api as employee_api
from .subunit_api import api as subunit_api
from .post_api import api as post_api
from .feed_api import api as feed_api


api_bp = Blueprint('api', __name__)

authorization = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}


class CustomApi(Api):
    def handle_error(self, e):
        for val in current_app.error_handler_spec.values():
            for handler in val.values():
                registered_error_handlers = list(filter(lambda x: isinstance(e, x), handler.keys()))
                if len(registered_error_handlers) > 0:
                    raise e
        return super().handle_error(e)


api = CustomApi(
    api_bp,
    title='OrgFeed API',
    version='0.0.2-dev',
    doc='/',
    description='API for news feed of some organization',
    authorizations=authorization
)


api.namespaces.clear()
api.add_namespace(employee_api)
api.add_namespace(subunit_api)
api.add_namespace(post_api)
api.add_namespace(feed_api)
api.add_namespace(attachment_api)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "*"
}
