from http.server import BaseHTTPRequestHandler, HTTPServer
from yeelight import Bulb
import sys
import time
import json
import configparser


class MyServer(HTTPServer):
    def init_state(self):
        self.daytime = None
        self.nighttime = None

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')

        self.parse_payload(json.loads(body))

        self.send_header('Content-type', 'text/html')
        self.send_response(200)
        self.end_headers()

    def parse_payload(self, payload):
        daytime = self.get_daytime(payload)
        nighttime = self.get_nighttime(payload)

        if daytime != self.server.daytime:
            self.server.daytime = daytime
            print('Day time toggled')
            
            if bulb1 != '':
                bulb = Bulb(bulb1)
                bulb.set_rgb(153, 102, 255)
                bulb.set_brightness(100)
                
            if bulb2 != '':
                bulb = Bulb(bulb2)
                bulb.set_rgb(153, 102, 255)
                bulb.set_brightness(100)
                
            if bulb3 != '':
                bulb = Bulb(bulb3)
                bulb.set_rgb(153, 102, 255)
                bulb.set_brightness(100)
                
        if nighttime != self.server.nighttime:
            self.server.nighttime = nighttime
            print('Night time toggled')
            
            if bulb1 != '':
                bulb = Bulb(bulb1)
                bulb.set_rgb(255, 0, 0)
                bulb.set_brightness(20)
                
            if bulb2 != '':
                bulb = Bulb(bulb2)
                bulb.set_rgb(255, 0, 0)
                bulb.set_brightness(20)
                
            if bulb3 != '':
                bulb = Bulb(bulb3)
                bulb.set_rgb(255, 0, 0)
                bulb.set_brightness(20)        
            
    def get_daytime(self, payload):
        if 'Map' in payload and 'IsDayTime' in payload['Map']:
            return payload['Map']['IsDayTime']
        else:
            return None
            
    def get_nighttime(self, payload):           
        if 'Map' in payload and 'IsNightstalker_Night' in payload['Map']:
            return payload['Map']['IsNightstalker_Night']
        else:
            return None

    def log_message(self, format, *args):
        return

server = MyServer(('localhost', 3000), MyRequestHandler)
server.init_state()

config = configparser.ConfigParser()
config.read('config.ini')
bulb1 = config.get('lamps','ip1')
bulb2 = config.get('lamps','ip2')
bulb3 = config.get('lamps','ip3')

if bulb1 != '':
    print('Initializing first Yeelight')
    bulb = Bulb(bulb1)
    bulb.turn_on()
    bulb.start_music()
    bulb.set_rgb(0, 0, 255)
    bulb.set_brightness(100)

if bulb2 != '':
    print('Initializing second Yeelight')
    bulb = Bulb(bulb2)
    bulb.turn_on()
    bulb.start_music()
    bulb.set_rgb(0, 0, 255)
    bulb.set_brightness(100)

if bulb3 != '':
    print('Initializing third Yeelight')
    bulb = Bulb(bulb3)
    bulb.turn_on()
    bulb.start_music()
    bulb.set_rgb(0, 0, 255)
    bulb.set_brightness(100)

print(time.asctime(), '-', 'GSI running - CTRL+C to stop')
try:
    server.serve_forever()
except (KeyboardInterrupt, SystemExit):
    pass

server.server_close()

if bulb1 != '':
    bulb = Bulb(bulb1)
    bulb.stop_music
    
if bulb2 != '':
    bulb = Bulb(bulb2)
    bulb.stop_music
    
if bulb3 != '':
    bulb = Bulb(bulb3)
    bulb.stop_music

print(time.asctime(), '-', 'GSI server stopped')
