# __Crawler__

특정 url에 대해 지정한 depth까지의 Html & Js 파일 저장

<br><br><br>

## 목차
1. [설치](#설치)
2. [사용법](#사용법)
3. [Error](#Error)

<br><br><br>

## 설치
```python
pip install selenium
pip install beautifulsoup4
pip install lxml
```

<br><br><br>

## 사용법
- chromedriver_path = "chromedriver.exe 경로 입력"
- craw_url = "대상 url 입력"
- save_path = "Html, JS 파일 저장 경로"
- select_depth = "depth 설정"

```python
#Example
chromedriver_path = "C:\\...\\chromedriver.exe"
craw_url = "https://naver.com/"
save_path = "C:\\...\\Desktop\\"
select_depth = 2
```

<br><br><br>

## Error
- 존재하지 않거나 접근할 수 없는 주소의 경우 terminal에 출력
  
<br><br><br>

