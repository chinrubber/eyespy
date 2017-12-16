from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, command
from eyespy.config import DefaultConfig
from eyespy import create_app
from eyespy.extensions import db

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

with app.app_context():
     command.upgrade(migrate.get_config(), 'head')

if __name__ == '__main__':
    manager.run()