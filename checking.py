import psutil
import os , time , configparser

config = configparser.ConfigParser()
config.read("config.ini")

py_ver = config.get("python","version")

while True:
    program_name = py_ver
    running = False

    for process in psutil.process_iter(['name']):
        if process.info['name'] == program_name:
            running = True
            break


    if running:
        print("Program is running")
    else:
        print("Program is NOT running")
        os.system("start cmd /k python main.py")
    time.sleep(5)