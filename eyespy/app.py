# -*- coding: utf-8 -*-

from flask import Flask, current_app
from eyespy.config import DefaultConfig
from eyespy.extensions import db, mail
from eyespy.components import discovery
import logging
import os

__all__ = ['create_app']

def create_app():
    app_name = DefaultConfig.PROJECT
    app = Flask(app_name)
    configure_logging(app)
    configure_app(app)
    configure_blueprints(app)
    configure_extensions(app)
    return app

def configure_app(app):
    app.config.from_object('eyespy.data.settings.settings')
    app.config.from_envvar('EYESPY_SETTINGS', silent=True)
    app.config.from_object(DefaultConfig)

def configure_blueprints(app):
    from eyespy.api import api
    from eyespy.ui import ui

    app.register_blueprint(api)
    app.register_blueprint(ui)

def configure_extensions(app):
    db.init_app(app)
    discovery.init_app(app)
    mail.init_app(app)

def configure_logging(app):
    if app.debug or app.testing:
        return

    import logging
    import os, sys
    from logging.handlers import RotatingFileHandler

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(
         '%(asctime)s %(levelname)s: %(message)s'
         )

    info_stdout_handler = logging.StreamHandler(sys.stdout)
    info_stdout_handler.setLevel(logging.DEBUG)
    info_stdout_handler.setFormatter(log_formatter)

    if not os.path.isdir(DefaultConfig.LOG_FOLDER):
        os.makedirs(DefaultConfig.LOG_FOLDER)

    info_log = os.path.join(DefaultConfig.LOG_FOLDER, 'eyespy.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.DEBUG)
    info_file_handler.setFormatter(log_formatter)
    
    root.addHandler(info_file_handler)
    root.addHandler(info_stdout_handler)





