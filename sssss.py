import os, json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options



#입력
chromedriver_path = "C:\\Users\\user\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
craw_url = "https://naver.com/"
save_path = "C:\\Users\\user\\Desktop\\me\\"
select_depth = 1



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
    #options.add_argument('--headless=old')
    options.add_argument('--disable-gpu')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})


    service = Service(executable_path=chromedriver_path)
    
    driver = webdriver.Chrome(service=service, options=options)

    return driver


''' File Save '''
def filename(url):

    url = url[:100]
    
    url = str(url).replace('//', '_')
    url = str(url).replace(':', '')
    url = str(url).replace('/', "_")
    url = str(url).replace('?', '')
    url = str(url).replace('-', '')
    
    return url

def create_folder(depth, url):
    
    url = filename(url)
    
    file_directory = save_path + str(depth) + "\\" + str(url)
    
    try:
        
        os.makedirs(file_directory)
            
    except:
        
        pass
        
    return file_directory

def file_save(response, file_name, file_direc):
    
    file_name = file_direc + "\\" + file_name + ".txt"
    with open(file_name, 'a', encoding='utf-8') as file:
            
        file.write(str(response))


''' next Depth url in Stack '''
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


''' html/JS response Save '''
def craw(url, file_directory, depth):
    
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
                
                file_save(response, file_name, file_directory)
                
                if mimeType == "text/html":
                    
                    url_parser(response, depth)


''' MAIN '''
def url_craw(url, depth):
    
    if depth == select_depth + 1:    return []
    
    
    file_directory = create_folder(depth, url)

    craw(url, file_directory, depth)
    
    return []
    


url_stack = stack()

driver = sel_option()
url_craw(craw_url, 1)

print(url_stack)

while not url_stack.isEmpty():
   
    craw_url = url_stack.pop()
    
    url_craw(craw_url[0], craw_url[1])
