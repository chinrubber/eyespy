# -*- coding: utf-8 -*-

from sqlalchemy import Column, desc
from eyespy.extensions import db
from eyespy.constants import STRING_LEN

class Setting(db.Model):

    name = Column(db.String(STRING_LEN), primary_key=True)
    value = Column(db.String(STRING_LEN), nullable=False, unique=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'value': self.value
        }