import requests
from bs4 import BeautifulSoup

#Defining Holding structure
urlsList=[
    "https://www.chocolate.co.uk/collections/all",
]
scrapedData=[]

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
if __name__=="__main__":
    dataScrap()
    print(scrapedData)