import requests
from bs4 import BeautifulSoup
import csv
import os
import json
from dataclasses import dataclass,field,InitVar,asdict
import time
import platform
import concurrent.futures
import random
#making our code concurrent
def concurrency(threadNum:int=5):
    while len(urlsList)>0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threadNum) as executor:
            executor.map(dataScrap,urlsList)

#clearing the screen
def screen_clear():
    os.system("cls") if platform.system()=="Windows" else os.system("clear")
#product class
@dataclass
class product:
    name:str=""
    uncleaned_price:InitVar[str]=""
    price:float=field(init=False)
    EGP_price:float=field(init=False)
    URL:str=""
    #post initialization method
    def __post_init__(self,uncleaned_price):
        self.name=self.clean_name()
        self.price=self.get_price(uncleaned_price)
        self.EGP_price=self.get_EGP_price()
        self.URL=self.clean_URL()
    #Getting clean name
    def clean_name(self):
        if self.name:
            return self.name.strip()
        else:
            return "missing"
    #Getting price value
    def get_price(self,uncleaned_price:str):
        if uncleaned_price:
            #removing any character doesn't represent numerical value
            alligble_characters="1234567890."
            for character in uncleaned_price:
                if character not in alligble_characters:
                    uncleaned_price=uncleaned_price.replace(character,"")
            return float(uncleaned_price)
        else:
            return 0.0
    #converting to EGP
    def get_EGP_price(self):
        USD=64.60
        return self.price*USD
    #getting an absolute link
    def clean_URL(self):
        return "https://www.chocolate.co.uk{link_extension}".format(
                    link_extension=self.URL
                    )
# a pipeline that add takes data processing it using data class and storing after collecting 5 entries
class productpipeline:
    def __init__(self,csv_file_name="",json_file_name="",storage_limit=5):
        self.namesList=[]
        self.storageLimit=storage_limit
        self.csv_file_name=csv_file_name
        self.json_file_name=json_file_name
        self.queue=[]
    def addproduct(self,scrapeddata:dict):
        rawdata=self.rawdata(scrapeddata=scrapeddata)
        if self.is_duplicate(rawdata.name):
            print("Data with name {name} is duplicate. dropping entry....".format(name=rawdata.name))
        else:
            self.queue.append(asdict(rawdata))
            if len(self.queue)>=self.storageLimit:
                self.save_to_csv() if self.csv_file_name else None
                self.save_to_json() if self.json_file_name else None
                self.queue=[]
    def is_duplicate(self,name):
        if name in self.namesList:
            return True
        else:
            self.namesList.append(name)
            return False
    def save_to_csv(self):
        headers=self.queue[0].keys()
        csvfile="{filename}.csv".format(filename=self.csv_file_name)
        fileexistence=os.path.isfile(csvfile)
        with open(csvfile,"a",newline="",encoding="UTF-8") as file:
            writer=csv.DictWriter(file,fieldnames=headers)
            if not fileexistence:
                writer.writeheader()
            writer.writerows(self.queue)
    def save_to_json(self):
        jsonfile="{filename}.json".format(filename=self.json_file_name)
        data=[]
        jsonExistence=os.path.isfile(jsonfile)
        if jsonExistence:
            with open(jsonfile,"r",encoding="UTF-8") as file:
                data=json.load(file)
        data.extend(self.queue)
        with open(jsonfile,"w",encoding="UTF-8") as file:
            json.dump(data,file,indent=2)
    def rawdata(self,scrapeddata:dict):
        return product(
            name=scrapeddata.get("name"),
            uncleaned_price=scrapeddata.get("price"),
            URL=scrapeddata.get("url")
        )
    def close(self):
        if len(self.queue)>0:
            self.save_to_csv()

#fakeuser agent middleware
class fakeuseragent:
    def __init__(self,api_key:str,results:int=2):
        self.api=api_key
        self.results=results
    def get_user_agents(self):
        response=requests.get(
            url='http://headers.scrapeops.io/v1/browser-headers?api_key={api_key}&num_results={results}'.format(
                api_key=self.api,
                results=self.results
            )
        )
        if response.status_code==200:
            userAgents_list=response.json()['result']
            if userAgents_list:
                return userAgents_list
            else:
                return self.fallback()
        else:
            return self.fallback()
    def user_agent(self):
        return random.choice(self.get_user_agents()) 
    def fallback(self):
        return [
            {
              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
              'accept-language': 'en-US', 
              'accept-encoding': 'gzip, deflate, br, zstd', 
              'upgrade-insecure-requests': '1',
              'sec-fetch-dest': 'document',
              'sec-fetch-mode': 'navigate',
              'sec-fetch-site': 'same-site',
              'sec-fetch-user': '?1', 
              'te': 'trailers', 
              'dnt': '1'
              },
              {
              'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"', 
              'sec-ch-ua-mobile': '?0', 
              'sec-ch-ua-platform': '"Windows"', 
              'upgrade-insecure-requests': '1', 
              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 
              'sec-fetch-site': 'same-site', 
              'sec-fetch-mode': 'navigate', 
              'sec-fetch-user': '?1', 
              'sec-fetch-dest': 'document', 
              'accept-encoding': 'gzip, deflate, br, zstd', 
              'accept-language': 'en-US'
              },

        ]
#adding a retry logic
class retrylogic:
    def __init__(self,limitOfRetries:int=5,antibotCheck:bool=False,FakeUserAgent:bool=False,period:int=3):
        self.retriesLimit=limitOfRetries
        self.antibotCheck=antibotCheck
        self.sleepPeriod=period
        self.fakeUserAgent=FakeUserAgent
    def retry(self,url:str):
        for retry in range(0,self.retriesLimit):
            try:
                headers={}
                if self.fakeUserAgent:
                  headers=userAgent.user_agent()
                  headers["accept-encoding"]="utf-8"
                response=requests.get(url=url,headers=headers)
                if response.status_code in [200,404]:
                    if self.antibotCheck and response.status_code==200:
                        if self.antibotCheck(response=response):
                            return False,response
                    return True if response.status_code==200 else False,response
                
            except Exception as e:
                print(str(e))
            time.sleep(self.sleepPeriod)
            screen_clear()
        return False,None
    def antibotCheck(self,response):
        pass
        #code for antiSbot is written here


#Defining Holding structure
urlsList=[
    "https://www.chocolate.co.uk/collections/all",
]
#Scraping function
def dataScrap(url):
        #code is written here
        #sending HTTP request and getting response
        urlsList.remove(url)
        validity,response=responseTillGet.retry(url=url)
        #souping
        if validity:
            soup=BeautifulSoup(response.content,"html.parser")
            products=soup.select("product-item")
            for product in products:
                productTitle=product.select("a.product-item-meta__title")[0].get_text()
                productPrice=product.select("span.price")[0].get_text()
                productURL=product.select("a.product-item-meta__title")[0].get("href")
                datapipeline.addproduct({
                    "name":productTitle,
                    "price":productPrice,
                    "url":productURL
                })
            next_page=soup.select("a[rel='next']")
            if next_page:
                urlsList.append("https://www.chocolate.co.uk{next}".format(next=next_page[0]["href"]))
        else:
            print("Scraping is invalid")
            
if __name__=="__main__":
    screen_clear()
    datapipeline=productpipeline(csv_file_name="chocolateData",json_file_name="chocolateData")
    userAgent=fakeuseragent(api_key="f447fb5c-5b34-44f3-81ba-a9de30f68e51",results=10)
    responseTillGet=retrylogic(FakeUserAgent=True)
    concurrency(threadNum=3)
    datapipeline.close()