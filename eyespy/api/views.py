# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, current_app
from flask_restful import Api
from eyespy.device import Device
from eyespy.extensions import db

api = Blueprint('api', __name__, url_prefix='/api/v1')
api_wrap = Api(api)

@api.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([d.serialize for d in devices])

@api.route('/devices/<macaddress>', methods=['GET'])
def get_device(macaddress):
    device = Device.query.get(macaddress)
    return jsonify(device.serialize)

@api.route('/devices/<macaddress>', methods=['DELETE'])
def delete_device(macaddress):
    device = Device.query.get(macaddress)
    db.session.delete(device)
    db.session.commit()
    return jsonify(status='ok')