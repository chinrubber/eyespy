# -*- coding: utf-8 -*-

from sqlalchemy import Column, desc
from eyespy.extensions import db
from eyespy.constants import STRING_LEN
from datetime import datetime

class Device(db.Model):

    macaddress = Column(db.String(STRING_LEN), primary_key=True)
    ipaddress = Column(db.String(STRING_LEN), nullable=False, unique=False)
    name = Column(db.String(STRING_LEN), nullable=True, unique=True)
    vendor = Column(db.String(STRING_LEN), nullable=True, unique=False)
    hostname = Column(db.String(STRING_LEN), nullable=True, unique=False)
    lastseen = Column(db.DateTime(), nullable=False, unique=False, default=datetime.now().replace(microsecond=0))

    def up(self):
        return (datetime.now() - self.lastseen).total_seconds() < 120

    @property
    def serialize(self):
        return {
            'macaddress': self.macaddress,
            'ipaddress': self.ipaddress,
            'name': self.name,
            'vendor': self.vendor,
            'hostname': self.hostname,
            'up': self.up()
        }