import os
import json

from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from injector import Module, singleton
from flask_jwt_extended import JWTManager
from flask_restx.api import Api
from flask_injector import FlaskInjector
from werkzeug.datastructures import Headers

from apis import api, cors_headers
from frontend_bindings.pages import bind_frontend_pages
from frontend_bindings.errors import bind_error_pages
from repositories import db

app = Flask(__name__)
app.register_blueprint(api.blueprint, url_prefix='/api/v1')


with open(os.path.join(app.root_path, 'config.json'), 'r') as config_file:
    app.config.update(json.loads(config_file.read()))

if not (os.environ.get('JWT_KEY') and os.environ.get("PGPASSWORD")):
    raise RuntimeError("Cannot find some env variables related to security")

app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY'] = os.environ.get('JWT_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'postgresql+psycopg2://mib_api:' + os.environ.get("PGPASSWORD") + '@/metalinblood'

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
app.config["MAX_CONTENT_PATH"] = app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 5


class AppModule(Module):
    def __init__(self, flask_app):
        self.app = flask_app
        self.db = SQLAlchemy(flask_app)

    def configure(self, binder):
        """Configure the application."""
        binder.bind(SQLAlchemy, to=self.db, scope=singleton)
        binder.bind(Api, to=api, scope=singleton)
        binder.bind(JWTManager, to=self.configure_jwt(), scope=singleton)
        binder.bind(Flask, to=self.app, scope=singleton)

    def configure_jwt(self):
        jwt = JWTManager(self.app)
        jwt._set_error_handler_callbacks(api)  # This is needed to automatically send 401 on token expiration
        return jwt


FlaskInjector(app=app, modules=[AppModule(app)])
bind_frontend_pages(app)
bind_error_pages(app)


@app.after_request
def after_request(response: Response):
    db.session.rollback()

    headers = dict(response.headers)
    headers["Cache-Control"] = "no-transform"
    if response.status_code in (200, 201):
        headers.update(**cors_headers)
    response.headers = Headers(headers)

    path = request.path
    if path.startswith("/api/v") and path.endswith("/") and path.count("/") == 3:
        body = response.get_data().replace(b"<head>", b"<head><style>.models {display: none !important}</style>")
        return Response(body, response.status_code, response.headers)
    return response


if __name__ == "__main__":
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] *= 32
    app.run(debug=True, host='0.0.0.0', port=5000)
