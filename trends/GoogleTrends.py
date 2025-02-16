import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json

options = Options()
options.use_chromium = True
url = "https://trends.google.com.tw/trending?geo=TW&hl=zh-TW"

def parse_search_volume(volume_str: str) -> int:
    """
    將類似 "1萬+ 次搜尋"、"2,000+ 次搜尋" 這種字串，
    解析成對應的整數（例如 10000、2000）。
    """
    # 1) 以 "+" 分割，取第一部分
    s = volume_str.split("+")[0]
    # 2) 去掉逗號
    s = s.replace(",", "")
    # 3) 如果包含 "萬" 就表示要乘以 10000
    if "萬" in s:
        num_str = s.replace("萬", "")
        return int(num_str) * 10000
    else:
        return int(s)

# 用 webdriver_manager 自動取得正確版本的 msedgedriver 路徑
edge_driver_path = EdgeChromiumDriverManager().install()
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=options)
driver.get(url)
driver.maximize_window()
time.sleep(8)
driver.get(url)
time.sleep(10)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# 取得更新時間，格式為 "更新時間：2月16日中午12:14"
SearchTime = soup.find('span', class_='Q2m0Gb')
date_str = SearchTime.text  # 例如 "更新時間：2月16日中午12:14"
# 取冒號後面的部分
date_time = date_str.split("：")[1]
# 用正則表達式提取 "2月16日"
match = re.search(r"(\d+月\d+日)", date_time)
if match:
    date_only = match.group(1)  # 例如 "2月16日"
    print("抓到的日期:", date_only)
else:
    print("找不到符合的日期格式")
    date_only = "未知日期"

# 轉換成 datetime 物件，並指定年份為2025
dt = datetime.strptime(date_only, "%m月%d日")
dt = dt.replace(year=2025)
formatted_date = dt.strftime("%Y-%m-%d")  # 例如 "2025-02-16"

# 取得所有趨勢標題與搜尋量
titles = soup.find_all('div', class_='mZ3RIc')
SearchVolumes = soup.find_all('div', class_='qNpYPd')

trends = []
# 使用 zip 將標題和搜尋量對應起來
for title_tag, volume_tag in zip(titles, SearchVolumes):
    title = title_tag.get_text().strip()
    volume_text = volume_tag.get_text().strip()
    intSV = parse_search_volume(volume_text)
    trends.append({
        "title": title,
        "searchVolume": intSV
    })

# 以日期為 key 建立大字典
data = {
    formatted_date: trends
}

# 輸出結果（使用 JSON 格式化印出方便閱讀）
print(json.dumps(data, ensure_ascii=False, indent=2))

input("按 Enter 鍵退出...")
driver.quit()
