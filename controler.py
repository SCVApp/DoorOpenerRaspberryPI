import threading
import socketio
import time
import requests
import lgpio

class Controler:
    socketClient = socketio.Client()
    timout_between_commands:float = 3
    time_lock_open:float = 1
    tread:threading.Thread = None
    stop_tread:bool = False
    door_is_open:bool = False
    door_is_in_timeout:bool = False
    gpio_chip=None
    pin_number:int=None

    def __init__(self, api_url:str, code:str, api_secret:str,gpio_chip,pin_number:int):
        self.api_url:str = api_url
        self.code:str = code
        self.api_secret:str = api_secret
        self.tread = threading.Thread(target=self.treadFunction)
        self.gpio_chip = gpio_chip
        self.pin_number = pin_number

    def reset(self):
        self.door_is_open = False
        self.door_is_in_timeout = False
        if self.thread.is_alive():
            self.stop_tread = True
            self.tread.join()
        self.stop_tread = False
        lgpio.gpio_write(self.gpio_chip, self.pin_number, 0)
        self.socketClient.disconnect()
        self.tread = threading.Thread(target=self.treadFunction)
        self.tread.daemon = True
        self.socketClient = socketio.Client()

    def setup(self):
            self.stop_tread = False
            self.call_backs()
            if not self.tread.is_alive():
                self.tread.daemon = True
                self.tread.start()
            while True:
                if self.socketClient.connected:
                    break
                try:
                    self.socketClient.connect(self.api_url, headers={'code': self.code, 'secret': self.api_secret})
                    time.sleep(5)
                    print("Connecting to socket...")
                except:
                    print("Error connecting to socket")
                    time.sleep(5)
                    continue
            lgpio.gpio_claim_output(self.gpio_chip, self.pin_number)

    def loop(self): 
        try:
            self.socketClient.wait()
        except KeyboardInterrupt:
            self.reset()
        except:
            self.reset()
            print("Error with socket")
    
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
            self.run()
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
        lgpio.gpio_write(self.gpio_chip, self.pin_number, 1)

    def handle_hardware_close_door(self):
        print('close door hardware')
        lgpio.gpio_write(self.gpio_chip, self.pin_number, 0)

    def treadFunction(self):
        secunds:float = 0
        print("tread started")
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

