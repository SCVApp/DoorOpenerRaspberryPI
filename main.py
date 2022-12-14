from controler import Controler
import lgpio
import threading
import socketio
import time

API_URL:str = 'https://backend.app.scv.si'
NUMBER_OF_DOORS:int = 2
gpio_chip = lgpio.gpiochip_open(0)

def getControllersFromENVFile():
    controlers:list[Controler] = []
    list_of_pins:list[int] = [23,24]
    interval:int = 1
    with open('.env', 'r') as f:
        controler_code:str = None
        controler_secret:str = None
        for line in f.readlines():
            line = line.strip()
            if line.startswith('CONTROLER{}_CODE'.format(interval)):
                controler_code = line.split('=')[1].strip()
            elif line.startswith('CONTROLER{}_SECRET'.format(interval)):
                controler_secret = line.split('=')[1].strip()
            if controler_code and controler_secret:
                controler:Controler = Controler(API_URL, controler_code, controler_secret,gpio_chip,list_of_pins[interval-1])
                controlers.append(controler)
                interval += 1
                if interval > NUMBER_OF_DOORS:
                    break
                controler_code = None
                controler_secret = None
    return controlers

def main():
    lgpio.gpio_claim_output(gpio_chip, 22)
    lgpio.gpio_write(gpio_chip, 22, 1)
    controlers:list[Controler] = getControllersFromENVFile()
    if len(controlers) == 0:
        print('No controlers found')
        return

    sio = socketio.Client()

    @sio.event
    def connect():
        print('connection established')

    @sio.event
    def disconnect():
        print('disconnected from server')

    @sio.on('open_door')
    def pass_open_door(data):
        for controler in controlers:
            if controler.code == data:
                controler.run()
                return "ok"


    sio.connect(API_URL,headers={'code': controlers[0].code, 'secret': controlers[0].api_secret})
    sio.wait()

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            time.sleep(5)
