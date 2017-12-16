from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, command
from eyespy.config import DefaultConfig
from eyespy import create_app
from eyespy.extensions import db

application = create_app()

migrate = Migrate(application, db)
manager = Manager(application)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()