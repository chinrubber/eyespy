# -*- coding: utf-8 -*-

from flask import Flask, current_app
from eyespy.config import DefaultConfig
from eyespy.utils import INSTANCE_FOLDER_PATH
from eyespy.extensions import db
from eyespy.components import discovery

__all__ = ['create_app']

def create_app(config=None, app_name=None):
    if app_name is None:
        app_name = DefaultConfig.PROJECT
    app = Flask(app_name, instance_path=INSTANCE_FOLDER_PATH, instance_relative_config=True)
    configure_app(app, config)
    configure_blueprints(app)
    configure_logging(app)
    configure_extensions(app)
    return app

def configure_app(app, config=None):
    app.config.from_object(DefaultConfig)

    if config:
        app.config.from_object(config)

def configure_blueprints(app):
    from eyespy.api import api
    from eyespy.ui import ui

    for bp in [api, ui]:
        app.register_blueprint(bp)

def configure_extensions(app):
    db.init_app(app)
    discovery.init(app)

def configure_logging(app):
    if app.debug or app.testing:
        return

    import logging
    import os
    from logging.handlers import RotatingFileHandler

    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    
    app.logger.addHandler(info_file_handler)



