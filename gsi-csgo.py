from http.server import BaseHTTPRequestHandler, HTTPServer
from yeelight import *
import sys
import time
import json
import configparser

alarm_flow = [
    HSVTransition(0, 100, duration=250, brightness=100),
    HSVTransition(0, 100, duration=250, brightness=60),
]
bomb_flow = [
    RGBTransition(255, 0, 0, duration=900, brightness=100),
    RGBTransition(255, 153, 0, duration=100, brightness=100),
]
bulbs = []


class MyServer(HTTPServer):
    # prepare checked items for http server
    def init_state(self):
        self.round_phase = None
        self.round_bomb = None
        self.player_health = None
        #self.weapon_ammo = None


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # receive payload from game
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')
        self.parse_payload(json.loads(body))
        self.send_header('Content-type', 'text/html')
        self.send_response(200)
        self.end_headers()

    def parse_payload(self, payload):
        round_phase = self.get_round_phase(payload)
        round_bomb = self.get_round_bomb(payload)
        player_health = self.get_player_health(payload)
        #weapon_ammo = self.get_weapon_ammo(payload)

        # compare and check if payload changed
        if round_bomb != self.server.round_bomb:
            self.server.round_bomb = round_bomb
            print('changed bomb status: %s' % round_bomb)
            if 'planted' in round_bomb:
                police()
            if 'defused' in round_bomb:
                change_light(0, 0, 255)

        if round_phase != self.server.round_phase:
            self.server.round_phase = round_phase
            print('new round phase: %s' % round_phase)
            if 'over' in round_phase:
                change_light(255, 0, 0)
            if 'live' in round_phase:
                change_light(153, 102, 255)
            if 'freezetime' in round_phase:
                change_light(0, 0, 255)

        if player_health != self.server.player_health:
            self.server.player_health = player_health
            print('player health: %s' % player_health)
            hp_g = int(round(player_health / 100 * 255))
            hp_r = int(round((255 * (1 - player_health / 100))))
            change_light(hp_r, hp_g, 0)
            if player_health <= 10:
                alarm()
                time.sleep(0.8)

        """if weapon_ammo != self.server.weapon_ammo:
            self.server.weapon_ammo = weapon_ammo
            print('weapon ammo: %s' % weapon_ammo)
            if player_health <= 5:
                change_light(255, 255, 255)"""

    def get_round_phase(self, payload):
        if use_phase == True:
            if 'round' in payload and 'phase' in payload['round']:
                return payload['round']['phase']
            else:
                return None

    def get_round_bomb(self, payload):
        if use_bomb == True:
            if 'round' in payload and 'bomb' in payload['round']:
                return payload['round']['bomb']
            else:
                return None

    def get_player_health(self, payload):
        if use_health == True:
            if 'player' in payload and 'state' in payload['player']:
                return payload['player']['state']['health']
            else:
                return None

    """
    def get_weapon_ammo(self, payload):
        if use_ammo == True:
            if 'player_weapons' in payload:
                return payload['player_weapons']['player']['weapons']['weapon_3']['ammo_clip']
            else:
                return None"""

    def log_message(self, format, *args):
        return


def change_light(r, g, b):
    # loop through bulbs with new rgb value
    for bulbn in (bulbs):
        if bulbn != '':
            bulb = Bulb(bulbn)
            bulb.set_rgb(r, g, b)


def alarm():
    for bulbn in (bulbs):
        if bulbn != '':
            bulb = Bulb(bulbn)
            bulb.start_flow(Flow(2, Flow.actions.recover, alarm_flow))


def police():
    for bulbn in (bulbs):
        if bulbn != '':
            bulb = Bulb(bulbn)
            # pulsate 40 times for 1 second each to show bomb timer
            bulb.start_flow(Flow(40, Flow.actions.recover, bomb_flow))


def main():
    print('Welcome to yeelight-valve-gsi by davidramiro')
    print('Reading config...')
    config = configparser.ConfigParser()
    config.read('config.ini')
    bulb_count = int(config.get('general', 'Lamp Count'))
    for n in range(1, (bulb_count + 1)):
        bulbs.append(config.get(str(n), 'ip'))
    global use_phase, use_bomb, use_health, use_ammo
    use_phase = config.getboolean('csgo settings', 'round phase colors')
    use_bomb = config.getboolean('csgo settings', 'c4 status colors')
    use_health = config.getboolean('csgo settings', 'health colors')
    use_ammo = config.getboolean('csgo settings', 'ammo colors')
    print('Initializing...')
    for bulbn in bulbs:
        if bulbn != '':
            print('Initializing Yeelight at %s' % bulbn)
            bulb = Bulb(bulbn)
            bulb.turn_on()
            # turn on music mode on the yeelights for better latency
            bulb.start_music()
            bulb.set_rgb(0, 0, 255)
            bulb.set_brightness(100)
    # start up the listening server
    server = MyServer(('localhost', 3000), MyRequestHandler)
    server.init_state()
    print(time.asctime(), '-', 'yeelight-valve-gsi is running - CTRL+C to stop')
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    server.server_close()
    # turn off music mode
    for bulbn in bulbs:
        if bulbn != '':
            bulb = Bulb(bulbn)
            bulb.stop_music
            bulb.set_rgb(255, 255, 255)
            bulb.set_brightness(100)
    print(time.asctime(), '-', 'Listener stopped. Thanks for using yeelight-valve-gsi!')


main()
