from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

options = Options()
options.use_chromium = True

# 用 webdriver_manager 取得正确版本的 msedgedriver 路径
edge_driver_path = EdgeChromiumDriverManager().install()
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=options)
driver.get("https://trends.google.com.tw/trending?geo=TW&hl=zh-TW")

input("按 Enter 鍵退出...")
driver.quit()