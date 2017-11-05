# -*- coding: utf-8 -*-

import os

from datetime import datetime

INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')

def get_current_time():
    return datetime.utcnow()