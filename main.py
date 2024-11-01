from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from crawler import sel_option, craw

app = FastAPI(title="Crawler Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str
    uuid: str

@app.post("/crawl")
async def crawl_url(request: URLRequest):
    print(f"크롤링 시작 URL: {request.url}, UUID: {request.uuid}")
    try:
        print("Selenium 드라이버 초기화 시작")
        driver = sel_option()
        print("드라이버 초기화 완료")
        
        print("크롤링 시작")
        result = craw(request.url, request.uuid, driver)
        print("크롤링 완료")
        
        driver.quit()
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"크롤링 중 오류 발생: {str(e)}")
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=f"크롤링 오류: {str(e)}")
