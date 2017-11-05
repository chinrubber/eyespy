# -*- coding: utf-8 -*-

import os

from eyespy.utils import INSTANCE_FOLDER_PATH

class BaseConfig(object):

    PROJECT = "eyespy"
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')

class DefaultConfig(BaseConfig):

    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + INSTANCE_FOLDER_PATH + '/eyespy.db'
