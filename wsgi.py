# -*- coding: utf-8 -*-

import sys, os
from flask_migrate import Migrate, MigrateCommand, command

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from eyespy import create_app

application = create_app()

migrate = Migrate(app, db)

with app.app_context():
     command.upgrade(migrate.get_config(), 'head')