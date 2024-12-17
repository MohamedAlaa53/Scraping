import requests
from bs4 import BeautifulSoup
import csv


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
                productPrice=product.select("span.price")[0].get_text().replace("\nSale price","")
                productURL="https://www.chocolate.co.uk{link_extension}".format(
                    link_extension=product.select("a.product-item-meta__title")[0].get("href")
                    )
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
    csvSaver(data_list=scrapedData,filename="chocolateData")