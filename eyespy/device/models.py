# -*- coding: utf-8 -*-

from sqlalchemy import Column, desc
from eyespy.extensions import db
from datetime import datetime

class Device(db.Model):

    macaddress = Column(db.String(255), primary_key=True)
    ipaddress = Column(db.String(255), nullable=False, unique=False)
    name = Column(db.String(255), nullable=True, unique=False)
    vendor = Column(db.String(255), nullable=True, unique=False)
    hostname = Column(db.String(255), nullable=True, unique=False)
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