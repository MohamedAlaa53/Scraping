import requests
from bs4 import BeautifulSoup
import csv
from dataclasses import dataclass,field,fields,InitVar,asdict

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



#Defining Holding structure
urlsList=[
    "https://www.chocolate.co.uk/collections/all",
]
scrapedData=[]

#CSv saving function
def csvSaver(data_list:dict,filename:str):
    #using first item in data list to define headers
    headers=data_list[0].keys()
    with open("{filename}.csv".format(filename=filename),'w',newline='') as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_list)


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
                scrapedData.append({
                    "name":productTitle,
                    "price":productPrice,
                    "url":productURL
                })
            next_page=soup.select("a[rel='next']")
            if next_page:
                urlsList.append("https://www.chocolate.co.uk{next}".format(next=next_page[0]["href"]))
            
if __name__=="__main__":
    dataScrap()
    #csvSaver(data_list=scrapedData,filename="chocolateData")