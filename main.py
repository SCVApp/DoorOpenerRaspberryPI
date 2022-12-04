from controler import Controler
import lgpio

API_URL:str = 'https://backend.app.scv.si/'
NUMBER_OF_DOORS:int = 1
gpio_chip = lgpio.gpiochip_open(0)

def main():
    controlers:list[Controler] = []
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
                controler:Controler = Controler(API_URL, controler_code, controler_secret,gpio_chip,23)
                controlers.append(controler)
                interval += 1
                if interval > NUMBER_OF_DOORS:
                    break
                controler_code = None
                controler_secret = None
    run_all_controlers(controlers)

def run_all_controlers(controlers:list[Controler]):
    for controler in controlers:
        controler.run()
    print("end is near")
    lgpio.gpiochip_close(gpio_chip)

if __name__ == '__main__':
    main()
