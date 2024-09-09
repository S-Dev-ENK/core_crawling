import os, json, time, urllib
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options



#입력
chromedriver_path = "C:\\Users\\user\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
craw_url = "https://www.navercorp.com/"
save_path = "C:\\Users\\user\\Desktop\\result7\\"



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
    options.add_argument('--headless')
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

def file_save(html, file_name, file_direc):
    
    if html:
        
        file_name = file_direc + "\\" + file_name + ".txt"
        with open(file_name, 'a', encoding='utf-8') as file:
            
            file.write(html)


''' next Depth url in Stack '''
def url_parser(html, depth, file_direc):
    
    file_save(html, "html", file_direc)
    
    html = BeautifulSoup(html, "lxml")
    for tag in html.find_all("a", href=True):
            
        href = tag["href"]
        
        if href.startswith(("http")):    
            
            url_stack.push([href, depth+1])
        
        else:    
            
            continue


''' Js '''
def js_craw(logs, file_direc):
    
    for log in logs:
        
        try:
            
            message = log.get("message")
            message = json.loads(message).get("message")
                
            method = message.get("method")
                
            if method == "Network.responseReceived":
                    
                mimeType = message.get("params").get("response").get("mimeType")
                    
                mimeType_list = {"text/html", "text/javascript", "application/javascript"}
                if mimeType in mimeType_list:
                        
                    url = message.get("params").get("response").get("url")
                    
                    try:
                    
                        js_file = js_re(url)
                        
                        file_name = filename(url)
                        file_save(js_file, file_name, file_direc)
                    
                    except:
                        
                        raise NameError("js_file Error")
                            
        except:
            
            raise NameError("js_craw Error")

def js_re(js):
    
    headers = {
                    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
            }   
    
    try:
        
        request = urllib.request.Request(url=js, headers=headers)
        response = urllib.request.urlopen(request)
        
        return response.read().decode('utf-8')
    
    except:
        
        print(NameError(js + " js_re Error"))
    
        return None


''' MAIN '''
def url_craw(url, depth):
    
    if depth == 3:    return []
    
    
    file_directory = create_folder(depth, url)
    
    driver.get(url)
        
    html = driver.page_source
    url_parser(html, depth, file_directory)
        
    logs = driver.get_log("performance")
    js_craw(logs, file_directory)

    
    


url_stack = stack()

driver = sel_option()
url_craw(craw_url, 1)


while not url_stack.isEmpty():
   
    craw_url = url_stack.pop()
    
    url_craw(craw_url[0], craw_url[1])
    