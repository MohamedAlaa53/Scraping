#importing the used libraries in the project
import requests,csv,os,json,time,platform,concurrent.futures,random
from bs4 import BeautifulSoup
from dataclasses import dataclass,field,InitVar,asdict
from itertools import cycle

#clearing the screen
def screen_clear():
    os.system("cls") if platform.system()=="Windows" else os.system("clear")
