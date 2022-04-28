import json
import prophet
import pandas as pd
from twstock import *

print(prophet.__version__)
# 印出所有台股證券編碼
# print(json.dumps(twstock.codes, indent=4, ensure_ascii=False))

stock_name = {
    '2330': u'台積電',
    '2317': u'鴻海',
    '1301': u'台塑',
    '1326': u'台化',
    '2412': u'中華電',
    '3008': u'大立光',
    '1303': u'南亞',
    '2308': u'台達電',
    '2454': u'聯發科',
    '2881': u'富邦金',
    '8299': u'群聯',
    '6223': u'旺矽'
}

stock_list = [
    '2330',  # 台積電
    '2317',  # 鴻海
    '1301',  # 台塑
    '1326',  # 台化
    '2412',  # 中華電
    '3008',  # 大立光
    '1303',  # 南亞
    '2308',  # 台達電
    '2454',  # 聯發科
    '2881',  # 富邦金
    '8299',  # 群聯
    '6223',  # 旺矽
]



stock = Stock('2330')
# 印出近31日 [2330] 收盤價 
print(stock.price)
# # 印出近31日 [2330] 最高價 
# print(stock.high)
# # 印出近31日 [2330] 成交量
# print(stock.transaction)

'''
    Prophet單變量時間序列預測
'''
df = pd.array(stock.price)
print(df)