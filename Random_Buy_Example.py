import random
import requests
from datetime import datetime
import time

# 取得股票資訊
# Input:
#   stock_code: 股票ID
#   start_date: 開始日期，YYYYMMDD
#   stop_date: 結束日期，YYYYMMDD
# Output: 股票資訊陣列
'''
    Example output:
    {   
        'capacity': 1214965,
        'change': 0.5,
        'close': 136,
        'date': 1649376000,
        'high': 137.5,
        'low': 135.5,
        'open': 136.5,
        'shdid': 23948326,
        'stock_code_id': '2492',
        'transaction_volume': 1189,
        'turnover': 165453618
    }
'''


def Get_Stock_Informations(stock_code, start_date, stop_date):
    information_url = ('http://140.116.86.242:8081/stock/' +
                       'api/v1/api_get_stock_info_from_date_json/' +
                       str(stock_code) + '/' +
                       str(start_date) + '/' +
                       str(stop_date)
                       )
    result = requests.get(information_url).json()
    if(result['result'] == 'success'):
        return result['data']
    return dict([])

# 取得持有股票
# Input:
#   account: 使用者帳號
#   password: 使用者密碼
# Output: 持有股票陣列


def Get_User_Stocks(account, password):
    data = {'account': account,
            'password': password
            }
    search_url = 'http://140.116.86.242:8081/stock/api/v1/get_user_stocks'
    result = requests.post(search_url, data=data).json()
    if(result['result'] == 'success'):
        return result['data']
    return dict([])

# 預約購入股票
# Input:
#   account: 使用者帳號
#   password: 使用者密碼
#   stock_code: 股票ID
#   stock_shares: 購入張數
#   stock_price: 購入價格
# Output: 是否成功預約購入(True/False)


def Buy_Stock(account, password, stock_code, stock_shares, stock_price):
    print('Buying stock...')
    data = {'account': account,
            'password': password,
            'stock_code': stock_code,
            'stock_shares': stock_shares,
            'stock_price': stock_price}
    buy_url = 'http://140.116.86.242:8081/stock/api/v1/buy'
    result = requests.post(buy_url, data=data).json()
    print('Result: ' + result['result'] + "\nStatus: " + result['status'])
    return result['result'] == 'success'

# 預約售出股票
# Input:
#   account: 使用者帳號
#   password: 使用者密碼
#   stock_code: 股票ID
#   stock_shares: 售出張數
#   stock_price: 售出價格
# Output: 是否成功預約售出(True/False)


def Sell_Stock(account, password, stock_code, stock_shares, stock_price):
    print('Selling stock...')
    data = {'account': account,
            'password': password,
            'stock_code': stock_code,
            'stock_shares': stock_shares,
            'stock_price': stock_price}
    sell_url = 'http://140.116.86.242:8081/stock/api/v1/sell'
    result = requests.post(sell_url, data=data).json()
    print('Result: ' + result['result'] + "\nStatus: " + result['status'])
    return result['result'] == 'success'


# 隨機購入或出售
# Input: None
# Output: None
def Random_Buy_Or_Sell():

    account = '帳號'  # 使用者帳號
    password = '密碼'  # 使用者密碼

    today = datetime.today().strftime('%Y%m%d')  # 今日日期，YYYYMMDD

    action = random.randrange(0, 10000000) & 1  # 決定操作為隨機購買或售出，0=購買、1=售出
    user_stocks = Get_User_Stocks(account, password)  # 取得使用者持有股票S
    if(len(user_stocks) == 0):  # 若使用者不持有任何股票
        action = 0  # 指定操作為購買股票
    if(action == 0):  # 如果操作為購買股票
        target_stocks_id = [2330]  # 購買股票清單，隨機購買將於該清單內隨機挑選一個股票來進行購買

        selected_stock_id = target_stocks_id[random.randrange(
            0, 100000000) % len(target_stocks_id)]  # 於購買清單隨機挑選一張股票

        today_stock_information = Get_Stock_Informations(
            selected_stock_id, '20200101', today)  # 取得選定股票往日資訊
        if(len(today_stock_information) == 0):  # 若選定股票沒有任何資訊
            print('未曾開市')
            return  # 結束操作
        today_stock_information = today_stock_information[0]  # 取得選定股票最新資訊
        # 股票隨機浮動範圍設定為最高價-最低價
        random_trading_price_offset_range = today_stock_information['high'] - \
            today_stock_information['low']

        buy_shares = random.randrange(1, 10)  # 股票隨機數量選定1~10張

        #購買價格以收盤價格-浮動範圍*(隨機浮點數0.0~1.0)
        buy_price = today_stock_information['close'] - random.random() * random_trading_price_offset_range
        # buy_price = today_stock_information['high']  # 購買價格設定為股票最高價

        Buy_Stock(account, password, selected_stock_id,
                  buy_shares, buy_price)  # 購買股票
    else:  # 操作為售出股票
        selected_stock = user_stocks[random.randrange(
            0, 100000000) % len(user_stocks)]  # 隨機選定一個使用者持有的股票

        selected_stock_id = selected_stock['stock_code_id']  # 取得選定的股票ID

        today_stock_information = Get_Stock_Informations(
            selected_stock_id, '20200101', today)  # 取得選定股票最新資訊
        if(len(today_stock_information) == 0):  # 若選定股票沒有任何資訊
            print('未曾開市')
            return  # 結束操作
        today_stock_information = today_stock_information[0]  # 取得選定股票最新資訊
        # 股票隨機浮動範圍設定為最高價-最低價
        random_trading_price_offset_range = today_stock_information['high'] - \
            today_stock_information['low']

        keeping_shares = selected_stock['shares']  # 取得使用者在選定股票所持有的張數
        sell_shares = random.randrange(
            1, keeping_shares)  # 隨機取得售出張數(1~使用者持有張數)
        sell_price = today_stock_information['close'] + random.random(
        ) * random_trading_price_offset_range  # 購買價格以收盤價格+浮動範圍*(隨機浮點數0.0~1.0)

        Sell_Stock(account, password, selected_stock_id,
                   sell_shares, sell_price)  # 售出股票


Random_Buy_Or_Sell()
