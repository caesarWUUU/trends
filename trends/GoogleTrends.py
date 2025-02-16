import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager


options = Options()
options.use_chromium = True
url = "https://trends.google.com.tw/trending?geo=TW&hl=zh-TW"

def parse_search_volume(volume_str: str) -> int:
    """
    將類似 "1萬+ 次搜尋"、"2,000+ 次搜尋" 這種字串，
    解析成對應的整數（例如 10000、2000）。
    """
    # 1) 去掉 "+ 次搜尋"
    s = volume_str.split("+")[0]
    # 2) 去掉逗號
    s = s.replace(",", "")
    # 3) 如果包含 "萬" 就表示要乘以 10000
    if "萬" in s:
        # 先把 '萬' 拿掉，剩下數字部分
        num_str = s.replace("萬", "")
        # 將它轉成整數後再乘 10000
        return int(num_str) * 10000
    else:
        # 沒有 "萬" 就直接轉整數
        return int(s)

# 用 webdriver_manager 取得正确版本的 msedgedriver 路径
edge_driver_path = EdgeChromiumDriverManager().install()
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=options)
driver.get(url)
driver.maximize_window()
time.sleep(8)
driver.get(url)
time.sleep(10)

soup = BeautifulSoup(driver.page_source, 'html.parser')

SearchTime = soup.find('span', class_='Q2m0Gb')
# print(Time.text)
date_str = SearchTime.text
date_time = date_str.split("：")[1]
match = re.search(r"(\d+月\d+日)", date_time)
if match:
    date_only = match.group(1)
    print(date_only)  # 輸出：2月16日
else:
    print("找不到符合的日期格式")

dt = datetime.strptime(date_only, "%m月%d日")
# 指定年份為2025
dt = dt.replace(year=2025)
formatted_date = dt.strftime("%Y-%m-%d")
# print(formatted_date)  # 輸出：2025-02-16


titles = soup.find_all('div', class_='mZ3RIc')
# for title in titles:
#     print(title.text)

SearchVolumes = soup.find_all('div', class_='qNpYPd')
for SearchVolume in SearchVolumes:
   volume_text = SearchVolume.get_text()
   intSV = parse_search_volume(volume_text)  
   print(intSV)


input("按 Enter 鍵退出...")
driver.quit()