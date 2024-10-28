import json, urllib
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests

# 입력
chromedriver_path = "C:\\Users\\syc\\Desktop\\chromedriver-win64\\chromedriver.exe"
craw_url = "https://naver.com/"
select_depth = 1
BACKEND_API_URL = "http://127.0.0.1:8000/apis/malicious-domain/receive-crawler-data"

class stack():
    def __init__(self):
        self.stack = []
        
    def push(self, value):
        self.stack.append(value)
    
    def pop(self):
        if self.isEmpty():
            return IndexError("Stack Empty")
        
        return self.stack.pop()
    
    def isEmpty(self):
        return len(self.stack) == 0
        
    def __str__(self):
        return str(self.stack)

''' Driver/Sel Options '''
def sel_option():
    options = Options()
    options.add_argument('--disable-gpu')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

''' Filename Generation '''
def filename(url):
    url = url[:100]
    url = str(url).replace('//', '_')
    url = str(url).replace(':', '')
    url = str(url).replace('/', "_")
    url = str(url).replace('?', '')
    url = str(url).replace('-', '')
    return url

''' Send data to Backend '''
def send_to_backend(url, combined_data):
    payload = {
        "url": url,
        "result": combined_data
    }
    try:
        response = requests.post(BACKEND_API_URL, json=payload)
    except Exception as e:
        print(f"Error sending data to backend: {e}")

''' URL Parser '''
def url_parser(response, depth):
    html = response.get("body")
    html = BeautifulSoup(html, "lxml")
    
    url_link = set()
    for tag in html.find_all("a", href=True):
        href = tag["href"]
        if href.startswith(("http")):
            url_link.add(href)
    
    for link in url_link:
        url_stack.push([link, depth+1])

''' Collect html/JS response into a single dictionary '''
def craw(url, depth):
    combined_data = {}
    driver.get(url)
    
    logs = driver.get_log('performance')
    
    for log in logs:
        message = json.loads(log["message"])
        message = message["message"]
        
        if message.get("method") == "Network.responseReceived":
            mimeType_list = {"text/html", "text/javascript", "application/javascript"}
            mimeType = message.get("params").get("response").get("mimeType")
            
            if mimeType in mimeType_list:
                request_id = message["params"]["requestId"]
                response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                
                file_url = message.get("params").get("response").get("url")
                file_name = filename(file_url)
                
                # Save the content in the combined_data dictionary
                if mimeType == "text/html":
                    combined_data[f"{file_name}"] = response.get("body")
                    url_parser(response, depth)
                elif mimeType in {"text/javascript", "application/javascript"}:
                    combined_data[f"{file_name}"] = response.get("body")
    
    # Send all collected data to backend
    send_to_backend(url, combined_data)

''' MAIN '''
def url_craw(url, depth):
    if depth == select_depth + 1:
        return []
    craw(url, depth)
    return []

url_stack = stack()
driver = sel_option()
url_craw(craw_url, 1)

while not url_stack.isEmpty():
    craw_url = url_stack.pop()
    url_craw(craw_url[0], craw_url[1])
