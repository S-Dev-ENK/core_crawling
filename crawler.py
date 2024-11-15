from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests
import json

class Stack:
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

def sel_option():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.binary_location = '/usr/bin/chromium-browser'

    # CDP 로깅 활성화
    chrome_options.set_capability('goog:loggingPrefs', {
        'performance': 'ALL'
    })
    
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.set_page_load_timeout(300)  # 5분
    driver.implicitly_wait(300)  # 5분
    # CDP 명령어 활성화
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Performance.enable', {})
    
    return driver

def filename(url):
    url = url[:100]
    url = str(url).replace('//', '_')
    url = str(url).replace(':', '')
    url = str(url).replace('/', "_")
    url = str(url).replace('?', '')
    url = str(url).replace('-', '')
    return url

def url_parser(response, depth, url_stack):
    html = response.get("body")
    html = BeautifulSoup(html, "lxml")
    
    url_link = set()
    for tag in html.find_all("a", href=True):
        href = tag["href"]
        if href.startswith(("http")):
            url_link.add(href)
    
    for link in url_link:
        url_stack.push([link, depth+1])

def check_server(url):
    
    headers = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"}
    response = requests.get(url, headers=headers, timeout=300)
    
    return response

def craw(url, uuid, driver):
    
    res = check_server(url)
    if res.status_code != 200:
    
        print("server error")
    
    url_stack = Stack()
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
                
                if mimeType == "text/html":
                    combined_data[f"{file_name}"] = response.get("body")
                    url_parser(response, 1, url_stack)  # depth는 1로 고정
                elif mimeType in {"text/javascript", "application/javascript"}:
                    combined_data[f"{file_name}"] = response.get("body")
    
    # 결과를 코어 서버로 전송
    send_to_core(url, uuid, combined_data)
    return combined_data

def send_to_core(url, uuid, combined_data):
    payload = {
        "url": url,
        "uuid": uuid,
        "result": combined_data
    }
    try:
        response = requests.post(
            "http://172.26.10.213:8002/receive-crawler-data",
            json=payload
        )
        if response.status_code != 200:
            print(f"Failed to send data to core server: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to core server: {e}") 