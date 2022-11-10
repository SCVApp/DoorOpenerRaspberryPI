import threading
import socketio
import time
import requests

class Controler:
    socketClient = socketio.Client()
    timout_between_commands = 3
    time_lock_open = 1
    tread = None
    stop_tread = False
    door_is_open = False
    door_is_in_timeout = False

    def __init__(self, api_url, code, api_secret):
        self.api_url = api_url
        self.code = code
        self.api_secret = api_secret
        self.tread = threading.Thread(target=self.treadFunction)

    def setup(self):
            self.call_backs()
            self.tread.start()
            self.socketClient.connect(self.api_url, headers={'code': self.code, 'secret': self.api_secret})
        

    def loop(self): 
        try:
            self.socketClient.wait()
        except KeyboardInterrupt:
            self.socketClient.disconnect()
            self.stop_tread = True
            self.tread.join()
            print('disconnected')
        except:
            self.socketClient.disconnect()
            self.run()
    
    def handle_open_door(self):
        if self.door_is_in_timeout or self.door_is_open:
            return
        url = self.api_url + '/pass/door/is_opened'
        res = requests.get(url,headers={"door_code":self.code,"access_secret":self.api_secret})
        if res.status_code == 200:
            self.door_is_open = True
            self.door_is_in_timeout = True
        else:
            print("Error: " + str(res.status_code))
        

    def disconnect_socket(self):
        self.socketClient.disconnect()
    
    def call_backs(self):

        @self.socketClient.event
        def connect():
            print('connection established')
        
        @self.socketClient.event
        def disconnect():
            print('disconnected from server')
        
        @self.socketClient.on('open_door')
        def pass_open(data):
            if self.code == data:
                self.handle_open_door()
    
    def run(self):
            self.setup()
            self.loop()
    
    def handle_hardware_open_door(self):
        print('open door hardware')

    def handle_hardware_close_door(self):
        print('close door hardware')

    def treadFunction(self):
        secunds = 0
        while True:
            time.sleep(0.1)
            if self.door_is_open:
                self.handle_hardware_open_door()
                time.sleep(self.time_lock_open)
                self.handle_hardware_close_door()
                secunds = 0
                self.door_is_in_timeout = True
                self.door_is_open = False
            if self.door_is_in_timeout:
                secunds += 1
                if secunds >= self.timout_between_commands:
                    self.door_is_in_timeout = False
                    secunds = 0
                time.sleep(1)
            if self.stop_tread:
                break

