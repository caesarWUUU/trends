import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json
import mysql.connector
from mysql.connector import errorcode
DB_NAME = 'googletrends'
try:
  cnx = mysql.connector.connect(user='root',password='414616',host='127.0.0.1')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  print("success connect to MySQL")

cursor = cnx.cursor()

#create database
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)
# create table
TABLES = {}
TABLES['trend_dates'] = (
    "CREATE TABLE `trend_dates` ("
    "  `date_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `formatted_date` date NOT NULL UNIQUE,"
    "  PRIMARY KEY (`date_id`)"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
)

TABLES['trends'] = (
    "CREATE TABLE `trends` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `date_id` int(11) NOT NULL,"
    "  `title` varchar(100) NOT NULL,"
    "  `searchVolume` int(11) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  INDEX idx_date_id (`date_id`),"
    "  FOREIGN KEY (`date_id`) REFERENCES `trend_dates` (`date_id`)"
    "    ON DELETE CASCADE ON UPDATE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
)

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
# insert data
add_date = (
    "INSERT INTO trend_dates (formatted_date) "
    "VALUES (%s) "
    "ON DUPLICATE KEY UPDATE formatted_date = formatted_date"
)
add_trend = (
    "INSERT INTO trends (date_id, title, searchVolume) "
    "VALUES (%s, %s, %s)"
)

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
# 將日期存入資料庫
date_data = (formatted_date, )
cursor.execute(add_date, date_data)
cnx.commit()
# 取得 date_id
cursor.execute("SELECT date_id FROM trend_dates WHERE formatted_date = %s", (formatted_date,))
result = cursor.fetchone()
if result:
    date_id = result[0]
else:
    raise Exception("無法取得日期對應的 date_id")
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
for trend in trends:
    trend_data = (date_id, trend["title"], trend["searchVolume"])
    cursor.execute(add_trend, trend_data)
    cnx.commit()

cursor.execute("SELECT * FROM trends")
rows = cursor.fetchall()
for row in rows:
    print(row)

input("按 Enter 鍵退出...")
driver.quit()

print("closing...")
cursor.close()
cnx.close()

