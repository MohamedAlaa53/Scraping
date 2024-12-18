import requests
from bs4 import BeautifulSoup
import csv
import os
from dataclasses import dataclass,field,InitVar,asdict

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

class productpipeline:
    def __init__(self,csv_file_name="",storage_limit=5):
        self.namesList=[]
        self.storageLimit=storage_limit
        self.csv_file_name=csv_file_name
        self.queue=[]
    def addproduct(self,scrapeddata:dict):
        rawdata=self.rawdata(scrapeddata=scrapeddata)
        if self.is_duplicate(rawdata.name):
            print("Data with name {name} is duplicate. dropping entry....".format(name=rawdata.name))
        else:
            self.queue.append(asdict(rawdata))
            if len(self.queue)>=self.storageLimit:
                self.save_to_csv()
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
        self.queue=[]
    def rawdata(self,scrapeddata:dict):
        return product(
            name=scrapeddata.get("name"),
            uncleaned_price=scrapeddata.get("price"),
            URL=scrapeddata.get("url")
        )
    def close(self):
        if len(self.queue)>0:
            self.save_to_csv()


#Defining Holding structure
urlsList=[
    "https://www.chocolate.co.uk/collections/all",
]
#Scraping function
def dataScrap():
    for url in urlsList:
        #code is written here
        #sending HTTP request and getting response
        response=requests.get(url)
        if response.status_code==200:
            #souping
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
            
if __name__=="__main__":
    #dataScrap()
    #csvSaver(data_list=scrapedData,filename="chocolateData")
    datapipeline=productpipeline(csv_file_name="chocolateData")
    dataScrap()
    datapipeline.close()