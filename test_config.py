import psutil
import os , time , configparser

config = configparser.ConfigParser()
config.read("config.ini")

py_ver = config.get("python","version")

print(py_ver)