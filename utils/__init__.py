from flask import Flask


def get_current_app() -> Flask:
    from server import app
    return app
