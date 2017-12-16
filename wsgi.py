# -*- coding: utf-8 -*-

from eyespy import create_app
import os, sys

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

application = create_app()

if __name__ == "__main__":
    application.run()
