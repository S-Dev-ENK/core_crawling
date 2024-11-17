from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from crawler import sel_option, craw
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Crawler Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str
    uuid: str
    
@app.get("/")
async def root():
    return {"message": "Crawler Service is running"}

@app.post("/crawl")
async def crawl_url(request: URLRequest):
    driver = None
    try:
        print(f"URL: {request.url}, UUID: {request.uuid}")
        #print("Selenium 드라이버 초기화 시작")
        driver = sel_option()
        #print("드라이버 초기화 완료")
        
        print("크롤링 시작")
        result = craw(request.url, request.uuid, driver)
        print("크롤링 완료")
        
        if driver:
            driver.quit()
        #response = {"status": "success", "data": result}
        #print(f"응답 전송: {response}")  # 응답 로깅 추가
        return {"status": "success"}
    except Exception as e:
        print(f"크롤링 중 오류 발생: {str(e)}")
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=str(e))
