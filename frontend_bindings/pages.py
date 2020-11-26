import os

from flask import Flask, render_template, send_from_directory


def bind_frontend_pages(app: Flask):
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static/metal-in-blood/'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/<string:page_name>.html", methods=["GET"])
    def page(page_name: str):
        return render_template(page_name + ".html")
