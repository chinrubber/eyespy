# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app

ui = Blueprint('ui', __name__)

@ui.route('/')
def index():
    return render_template('index.html')

@ui.route('/devices/<macaddress>')
def edit_device(macaddress):
    return render_template('device.html')
