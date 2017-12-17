# -*- coding: utf-8 -*-

import os, sys
from eyespy import create_app
from flask_migrate import Migrate, MigrateCommand, command
from eyespy.extensions import db

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

application = create_app()

migrate = Migrate(application, db)

# with application.app_context():
#     command.upgrade(migrate.get_config(), 'head')

if __name__ == "__main__":
    application.run()
