import threading
import socketio
import time
import requests

class Controler:
    socketClient = socketio.Client()
    timout_between_commands:float = 3
    time_lock_open:float = 1
    tread:threading.Thread = None
    stop_tread:bool = False
    door_is_open:bool = False
    door_is_in_timeout:bool = False

    def __init__(self, api_url:str, code:str, api_secret:str):
        self.api_url:str = api_url
        self.code:str = code
        self.api_secret:str = api_secret
        self.tread = threading.Thread(target=self.treadFunction)

    def setup(self):
            self.call_backs()
            self.tread.start()
            while True:
                try:
                    self.socketClient.connect(self.api_url, headers={'code': self.code, 'secret': self.api_secret})
                except:
                    print("Error connecting to socket")
                    time.sleep(15)
                    continue
                if self.socketClient.connected:
                    break

    def loop(self): 
        try:
            self.socketClient.wait()
        except KeyboardInterrupt:
            self.stop_tread = True
            self.tread.join()
            self.socketClient.disconnect()
        except:
            self.socketClient.disconnect()
            print("Error with socket")
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
                return "ok"
    
    def run(self):
            self.setup()
            self.loop()
    
    def handle_hardware_open_door(self):
        print('open door hardware')

    def handle_hardware_close_door(self):
        print('close door hardware')

    def treadFunction(self):
        secunds:float = 0
        while True:
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

