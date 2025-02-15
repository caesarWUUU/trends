from pytrends.request import TrendReq
from matplotlib import pyplot as plt

pytrends = TrendReq(hl='zh-TW', tz=480)  

keywords = ["Python Programming", "Data Science", "Machine Learning"]
pytrends.build_payload(kw_list=keywords, timeframe='today 12-m', geo='TW')

trending_searches_df = pytrends.trending_searches(pn='taiwan')
# Display trending searches
print(trending_searches_df)