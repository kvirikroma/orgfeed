from flask import Flask, render_template, request, jsonify


def custom_abort_page(message: str, code: int):
    return render_template("error_page.html", code=str(code), text=message)


def bind_error_pages(app: Flask):
    @app.errorhandler(500)
    def error500(err):
        if request.path.startswith("/api/v"):
            return jsonify(message=err.description), err.code
        return custom_abort_page(err.description, err.code), err.code

    @app.errorhandler(404)
    def error404(err):
        if request.path.startswith("/api/v"):
            return jsonify(message=err.description), err.code
        return custom_abort_page(err.description, err.code), err.code

    @app.errorhandler(400)
    def error400(err):
        if request.path.startswith("/api/v"):
            return jsonify(message=err.description), err.code
        return custom_abort_page(err.description, err.code), err.code
