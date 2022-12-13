from controler import Controler
import lgpio
import threading
import time

API_URL:str = 'https://backend.app.scv.si/'
NUMBER_OF_DOORS:int = 1
gpio_chip = lgpio.gpiochip_open(0)

def main():
    lgpio.gpio_claim_output(gpio_chip, 22)
    lgpio.gpio_write(gpio_chip, 22, 1)
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
    run_all_controlers(controlers)

def run_all_controlers(controlers:list[Controler]):
    threads:list[threading.Thread] = []
    for controler in controlers:
        thread = threading.Thread(target=run_controler, args=(controler,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        print("Thread start")
    if int(len(threads)) > 0:
        while threads[0].is_alive():
            print("Program is running. Number of threads: {}".format(str(len(threading.enumerate()))))
            time.sleep(5) 

def run_controler(controler:Controler):
    while True:
        try:
            print("Thread started. Controller pin_n: {}".format(controler.pin_number))
            controler.reset()
            controler.setup()
            controler.loop()
        except:
            print("Error with controler")
            time.sleep(5)
            continue

if __name__ == '__main__':
    main()
