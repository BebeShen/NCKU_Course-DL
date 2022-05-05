import json
import requests
from datetime import datetime, timedelta

class Stock:
    data = []
    def __init__(
            self, 
            stockNo:int, 
            days:int = 30, 
            start:str = (datetime.today() - timedelta(days=30)).strftime("%Y%m%d"), 
            end:str = datetime.today().strftime("%Y%m%d")
        ):
        '''
        Parameters
        ----------
        stockNo   : int (required) 
            個股代號
        days      : int (optional) 
            日期區間
        start     : str (optional) 
            查詢區間的起始時間, 預設為30天前, 必須是YYYYMMDD格式
        end       : str (optional) 
            查詢區間的結束時間, 預設為當天日期, 必須是YYYYMMDD格式
        
        '''
        self.stockNo = stockNo
        self.start_time = start
        self.end_time = end
        print(self.stockNo, self.start_time, self.end_time)

        print(json.dumps(self.getStockInfo(), indent=4, sort_keys=True))
        # print(self.getStockInfo())

    # 從MMDB獲取個股資訊
    def getStockInfo(self):
        information_url = ('http://140.116.86.242:8081/stock/' +
                            'api/v1/api_get_stock_info_from_date_json/' +
                            str(self.stockNo) + '/' +
                            str(self.start_time) + '/' +
                            str(self.end_time)
                            )
        result = requests.get(information_url).json()
        if(result['result'] == 'success'):
            return result['data']
        return dict([])

    # 計算移動平均線
    def getMA(self):
        pass

    # 計算KD

    # 計算MACD

    # 計算RSI

    # 計算乖離率

    # 計算威廉指標

    # 多空指標乖離

    # CDP

    # DMI

    

def main():
    stock=Stock(2330)

if __name__ == "__main__":
    main()