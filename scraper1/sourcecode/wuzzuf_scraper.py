#importing the used libraries in the project
import requests,csv,os,json,time,platform,concurrent.futures,random,cloudscraper
from bs4 import BeautifulSoup
from dataclasses import dataclass,asdict
from itertools import cycle

#clearing the screen
def screen_clear():
    os.system("cls") if platform.system()=="Windows" else os.system("clear")

#data class that recieve and clean data
@dataclass
class jobs_data:
    jobTitle:str=""
    companyName:str=""
    jobReq:str=""
    jobSalary:str=""
    jobLevel:str=""
    jobURL:str=""
    def __post_init__(self):
        self.jobTitle=self.clean_jobTitle()
        self.companyName=self.clean_companyName()
        self.jobReq=self.clean_jobReq()
        self.jobSalary=self.clean_jobSalary()
        self.jobLevel=self.clean_jobLevel()
        self.jobURL=self.clean_jobURL()
    def clean_jobTitle(self):
        pass
    def clean_companyName(self):
        pass
    def clean_jobReq(self):
        pass
    def clean_jobSalary(self):
        pass
    def clean_jobLevel(self):
        pass
    def clean_jobURL(self):
        pass

#jobs pipeline
class jobs_pipeline:
    def __init__(self,csv_file_name="",json_file_name="",storage_limit=5):
        self.csv=csv_file_name
        self.json=json_file_name
        self.limit=storage_limit
        self.queue=[]
        self.namesList=[]
    def save_to_csv(self):
        headers=self.queue[0].keys()
        with open(self.csv,"a",newline="",encoding="UTF-8") as file:
            writer=csv.DictWriter(file,fieldnames=headers)
            if os.path.isfile(self.csv):
                writer.writeheader()
            writer.writerows(self.queue)
    def save_to_json(self):
        data=[]
        if os.path.isfile(self.json):
            with open(self.json,"r",encoding="UTF-8") as file:
                data=json.load(file)
        data.extend(self.queue)
        with open(self.json,"w",encoding="UTF-8") as file:
            json.dump(data,file,indent=2)
    def get_raw_data(self,data:dict):
        return jobs_data(
            jobTitle=data["jobtitle"]
            ,companyName=data["companyname"]
            ,jobReq=data["jobreq"]
            ,jobSalary=data["jobsalary"]
            ,jobLevel=data["joblevel"]
            ,jobURL=data["joburl"]
            )
    def store_data(self,data:dict):
        newEntry=self.get_raw_data(data)
        if newEntry.jobTitle not in self.namesList:
            self.namesList.append(newEntry.jobTitle)
            self.queue.append(asdict(newEntry))
            if len(self.queue)>=self.limit:
                self.save_to_csv()
                self.save_to_json
                self.queue=[]
        else:
            print("job is already existed .....")

#fakeuseragent
class fakeuseragent:
    def __init__(self,api_key:str,results:int=2):
        self.api=api_key
        self.results=results
    def get_fake_user_agents(self):
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
        return random.choice(self.get_fake_user_agents()) 
    def fallback(self):
        return[
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

#urls
urls_to_be_scraped=[
    "https://wuzzuf.net/search/jobs/?q=&a=hpb",
                    ]

#Scraper
def scraper():
    for url in urls_to_be_scraped:
        response=requests.request(method="GET",url=url,headers=useragent.user_agent())
        soup=BeautifulSoup(response.content,"html.parser")
        print(soup.select("script")[0])

if __name__=="__main__":
    screen_clear()
    useragent=fakeuseragent(api_key="f447fb5c-5b34-44f3-81ba-a9de30f68e51",results=10)
    scraper()
        