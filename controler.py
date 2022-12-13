import threading
import socketio
import time
import requests
# import lgpio

class Controler:
    timout_between_commands:float = 3
    time_lock_open:float = 1
    tread:threading.Thread = None
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

    def run(self):
        if self.tread.is_alive():
            return
        if self.door_is_in_timeout:
            return
        self.tread.start()

    def treadFunction(self):
        if self.door_is_in_timeout:
            return
        url = self.api_url + '/pass/door/is_opened'
        res = requests.get(url,headers={"door_code":self.code,"access_secret":self.api_secret})
        if res.status_code == 200:
            self.door_is_in_timeout = True
            self.hardware_open_door()
            time.sleep(self.time_lock_open)
            self.hardware_close_door()
            time.sleep(self.timout_between_commands)
            self.door_is_in_timeout = False

    def hardware_open_door(self):
        print('close door hardware')
        # lgpio.gpio_write(self.gpio_chip, self.pin_number, 1)
    
    def hardware_close_door(self):
        print('open door hardware')
        # lgpio.gpio_write(self.gpio_chip, self.pin_number, 0)

        
