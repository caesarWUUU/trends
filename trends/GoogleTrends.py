from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt

pytrends = TrendReq(hl='zh-TW', tz=480)  

keywords = ["Python Programming", "Data Science", "Machine Learning"]
pytrends.build_payload(kw_list=keywords, timeframe='today 12-m', geo='US')

data = pytrends.interest_over_time()
print(data)

