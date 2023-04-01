from flask import Flask
from .view import views

def create_app():
    generator_log_app = Flask(__name__, template_folder="templates")

    generator_log_app.register_blueprint(views, url_prefix="/")

    return generator_log_app