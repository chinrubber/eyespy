# -*- coding: utf-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
from eyespy.extensions import db, mail
from eyespy.device import Device
from datetime import datetime, timedelta
from requests import RequestException, Timeout
from flask_mail import Message
import scapy.config
import scapy.layers.l2
import scapy.route
import math
import netifaces
import socket
import errno
import requests
import logging
from flask import render_template
from os import environ

logger = logging.getLogger()

class Discovery():

    def __init__(self):
        self.app = None
        self.scaninterface = None
        self.scannet = None
        self.scheduler = None
        self.logger = None

    def init_app(self, app):
        self.app = app
        self.set_net()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.scheduler.add_job(self.scan, 'interval', seconds=15, max_instances=1)
               
    def shutdown(self):
        self.scheduler.shutdown()

    def set_net(self):
        for network, netmask, _, interface, address in scapy.config.conf.route.routes:
            if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
                continue
            if netmask <= 0 or netmask == 0xFFFFFFFF:
                continue
            if environ.get('EYESPY_NET') is not None:
                logging.info('EYESPY_NET value is %s ' % environ.get('EYESPY_NET') )
                net = environ.get('EYESPY_NET')
            else :
                net = self.to_CIDR_notation(network, netmask)
                logging.info('EYESPY_NET was not present so using %s ' % net)
            if interface != scapy.config.conf.iface:
                continue
            if net:
                self.scaninterface = interface
                self.scannet = net

    def to_CIDR_notation(self, bytes_network, bytes_netmask):
        network = scapy.utils.ltoa(bytes_network)
        netmask = self.long2net(bytes_netmask)
        net = "%s/%s" % (network, netmask)
        if netmask < 16:
            return None

        return net

    def long2net(self, arg):
        if (arg <= 0 or arg >= 0xFFFFFFFF):
            raise ValueError("illegal netmask value", hex(arg))
        return 32 - int(round(math.log(0xFFFFFFFF - arg, 2)))

    def scan(self):
        logging.info('Scanning for devices on if %s with net %s ' % (self.scaninterface, self.scannet) )
        discovereddevices = []
        local = netifaces.ifaddresses(self.scaninterface)
        localhwaddress =  local[netifaces.AF_LINK][0]['addr']
        localipaddress =  local[netifaces.AF_INET][0]['addr']
        device = Device()
        device.macaddress = localhwaddress
        device.ipaddress = localipaddress
        device.hostname = self.resolve(localipaddress)
        device.lastseen = datetime.now().replace(microsecond=0)
        device.up = True
        discovereddevices.append(device)
        discovereddevices.extend(self.scan_all(self.scannet, self.scaninterface))
        self.persist(discovereddevices)

    def persist(self, discovered_devices):
        with self.app.app_context():
            state_change_devices = []
            for device in Device.query.all():
                if not device.vendor:
                    device.vendor = self.lookup_vendor(device.macaddress)
                d_device = self.find_device(discovered_devices, device)
                if not d_device:
                    if device.up and device.important and (datetime.now() - device.lastseen).total_seconds() > 45:
                        logging.info('State for important device %s (%s) has changed from up to down' % (device.macaddress, device.name))
                        state_change_devices.append(device)
                        device.up = False
                else:
                    if not device.up and device.important:
                        logging.info('State for important device %s (%s) has changed from down to up' % (device.macaddress, device.name))
                        state_change_devices.append(device)
                    if d_device.ipaddress != device.ipaddress:
                        logging.info('Ip address for % has changed from %s to %s' % (device.macaddress, device.ipaddress, d_device.ipaddress))
                    if d_device.hostname !=device.hostname:
                        logging.info('Hostname for %s has changed from %s to %s' % (device.macaddress, device.hostname, d_device.hostname))

                    device = db.session.merge(d_device)

            for device in discovered_devices:
                device = db.session.merge(device)
                device.vendor = self.lookup_vendor(device.macaddress)

            db.session.commit()

            if len(state_change_devices) > 0:
                self.send_state_change_device_email(state_change_devices)

            if len(discovered_devices) > 0:
                self.send_new_devices_email(discovered_devices)

    def find_device(self, devices, src_device):
        i = 0
        while i < len(devices):
            if devices[i].macaddress == src_device.macaddress:
                return devices.pop(i)
            else:
                i+=1

        return None

    def scan_all(self, net, interface, timeout=10):
        discovereddevices = []
        try:
            ans, unans = scapy.layers.l2.arping(net, iface=interface, timeout=timeout, verbose=False)
            for s, r in ans.res:
                device = Device()
                device.macaddress = r.src
                device.ipaddress = r.psrc
                device.hostname = self.resolve(r.psrc)
                device.lastseen = datetime.now().replace(microsecond=0)
                device.up = True
                logging.debug('Discovered device %s with hostname %s (%s)' % (r.src, device.hostname, r.psrc))
                discovereddevices.append(device)
        except socket.error as e:
            if e.errno == errno.EPERM:
                pass
            else:
                raise
        return discovereddevices

    def resolve(self, ipaddress):
        try:
            hostname = socket.gethostbyaddr(ipaddress)[0]
        except socket.herror:
            return None

        return hostname

    def lookup_vendor(self, macaddress):
        try:
            response = requests.get('http://api.macvendors.com/%s' % macaddress, timeout=1.5)
            if response.status_code == 200:
                return response.text
            if response.status_code == 404:
                return 'Unknown'
        except Timeout as t:
            logging.warn("Timed out resolving mac address from api.macvendors.com")
            return None
        except RequestException as e:
            logging.error("Unable to resolve mac address from api.macvendors.com")
            return None
   
    def send_email(self, subject, text_body, html_body):
        sender = self.app.config['NOTIFY_FROM_ADDRESS']
        recipients = [self.app.config['NOTIFY_TO_ADDRESS']]
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)

    def send_new_devices_email(self, devices):
        self.send_email('EyesPy - New Device(s) Detected', 'Test',
            render_template('email_new_devices.html', devices=devices))

    def send_state_change_device_email(self, devices):
        self.send_email('EyesPy - Device State Change(s) Detected', 'Test',
            render_template('email_state_change_devices.html', devices=devices))
