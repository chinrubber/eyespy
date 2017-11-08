# -*- coding: utf-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
from eyespy.extensions import db
from eyespy.device import Device
from datetime import datetime
from requests import RequestException
import scapy.config
import scapy.layers.l2
import scapy.route
import math
import netifaces
import socket
import errno
import requests

class Discovery():

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.scan, 'interval', seconds=15, max_instances=1)
        self.set_net()

    def init(self, app):
        self.app = app
        self.scheduler.start()
     
    def shutdown(self):
        self.scheduler.shutdown()

    def set_net(self):
        for network, netmask, _, interface, address in scapy.config.conf.route.routes:
            if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
                continue
            if netmask <= 0 or netmask == 0xFFFFFFFF:
                continue
            net = self.to_CIDR_notation(network, netmask)
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
        discovereddevices = []
        local = netifaces.ifaddresses(self.scaninterface)
        localhwaddress =  local[netifaces.AF_LINK][0]['addr']
        localipaddress =  local[netifaces.AF_INET][0]['addr']
        device = Device()
        device.macaddress = localhwaddress
        device.ipaddress = localipaddress
        discovereddevices.append(device)
        discovereddevices.extend(self.scan_all(self.scannet, self.scaninterface))
        self.persist(discovereddevices)

    def persist(self, discovered_devices):
        with self.app.app_context():
            for discovered_device in discovered_devices:
                device = db.session.merge(discovered_device)
                if not device.lastseen:
                    device.vendor = self.lookup_vendor(device.macaddress)
                device.lastseen = datetime.now().replace(microsecond=0)
                device.hostname = self.resolve(device.ipaddress)
                db.session.commit()

    def scan_all(self, net, interface, timeout=10):
        discovereddevices = []
        try:
            ans, unans = scapy.layers.l2.arping(net, iface=interface, timeout=timeout, verbose=False)
            for s, r in ans.res:
                device = Device()
                device.macaddress = r.src
                device.ipaddress = r.psrc
                discovereddevices.append(device)
        except socket.error as e:
            if e.errno == errno.EPERM:
                print('Operation not permitted')
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
            response = requests.get('http://api.macvendors.com/%s' % macaddress)
            if response.status_code == 200:
                return response.text
        except RequestException as e:
            pass
        
        return None