import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import json_normalize
from datetime import date, datetime, timedelta

def getStockInformations(stockNo, start_date, end_date):
    information_url = ('http://140.116.86.242:8081/stock/' +
                       'api/v1/api_get_stock_info_from_date_json/' +
                       str(stockNo) + '/' +
                       str(start_date) + '/' +
                       str(end_date)
                       )
    result = requests.get(information_url).json()
    if(result['result'] == 'success'):
        return result['data']
    return dict([])

def SUM(S:pd.DataFrame, N:int):
    return  pd.Series(S).rolling(N).sum() if N>0 else pd.Series(S).cumsum()

#   對Series整體下移動 N, 返回 Series(shift後會產生NAN)
def REF(S:pd.DataFrame, N:int):
    return pd.Series(S).shift(N)  

def IF(S_BOOL,S_TRUE,S_FALSE):          
    return np.where(S_BOOL, S_TRUE, S_FALSE)

#   Series max
def MAX(S1,S2):  
    return np.maximum(S1,S2)    

def __changePeriod(stockInfo, period='W-mon'):
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    rf = df.resample(period).last()
    rf['high'] = df['high'].resample(period).max()
    rf['low'] = df['low'].resample(period).min()
    rf['change'] = df['change'].resample(period).sum()
    # weekdf.fillna(method='ffill', inplace=True)

    return json.loads(rf.to_json(orient='records'))

def __calculateMA(df):
    '''計算移動平均線(MA), 將N天的收盤價加總後再除以N, 即得到第N天的算術平均線數值。
    
    常用的日線有: 5日線, 10日線, 20日線, 60日線, 120日線, 240日線。
    '''
    # 分別計算5天, 10天, 20天和60天的移動平均線
    df['MA_5'] = df['close'].rolling(5).mean()
    df['MA_10'] = df['close'].rolling(10).mean()
    df['MA_20'] = df['close'].rolling(20).mean()
    df['MA_60'] = df['close'].rolling(60).mean()
    return df
    
def __calculateKD(df):
    '''計算KD值
    
    '''

    # 計算9日內最高成交價
    df['9daymax'] = df['high'].rolling(9).max()
    df['9daymin'] = df['low'].rolling(9).min()
    # print(df['9daymax'], df['9daymin'])
    df['RSV'] = 0
    df['RSV'] = (df['close'] - df['9daymin']) / (df['9daymax'] - df['9daymin'])*100
    # print(df['RSV'])

    # 計算k值 計算d值
    df['K9'] = df['RSV'].ewm(com=2, adjust=False).mean()
    df['D9'] = df["K9"].ewm(com=2, adjust=False).mean()
    df["3K-2D"] = 3 * df["K9"] - 2 * df["D9"]
    # df.reset_index(inplace=True)
    # df['date'] = pd.to_datetime(df['date'], unit='s')
    df = df.drop(['9daymax', '9daymin'], axis=1)
    return df

def __calculateMACD(df):
    '''MACD, Moving Average Convergence and Divergence, 股市中常說的平滑異同移動平均線。由DIF、DEA、MACD組成

    MA分成EMA(exponential)和SMA(mean), 這裡使用EMA

    '''
    # com=1 代表權重為 1/(com+1) = 1/2
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
    # df['EMA_12'] = df['EMA_12'].rolling(12).mean()
    # df['EMA_26'] = df['EMA_26'].rolling(26).mean()
    # 差離值
    df['DIF9'] = df['EMA_12'] - df['EMA_26']
    # 差離平均值
    df['DEA'] = df['DIF9'].ewm(span=9, adjust=False).mean()
    # yahoo 以 DEA 為 MACD
    df['MACD'] = df['DEA']
    # 柱狀值
    # df['MACD'] = 2*(df['DIF'] - df['DEA'])
    return df.drop(['DEA'], axis=1)

def __calculateRSI(df):
    '''計算RSI值
    
    RSI是計算過去一段時間的相對強弱, 這個"一段時間"是看個人選擇要多長的時間, 一般比較常見的是6日、12日、14日、24日。

    一樣預設使用EMA

    '''
    close_delta = df['close'].diff()

    high = close_delta.clip(lower=0)
    low = -1*close_delta.clip(upper=0)

    period = 5
    maHigh = high.ewm(com=period-1, adjust=True, min_periods=period).mean()
    maLow = low.ewm(com=period-1, adjust=True, min_periods=period).mean()

    df['RSI5'] = maHigh/maLow
    df['RSI5'] = 100-(100/(1+df['RSI5']))

    period = 10
    maHigh = high.ewm(com=period-1, adjust=True, min_periods=period).mean()
    maLow = low.ewm(com=period-1, adjust=True, min_periods=period).mean()

    df['RSI10'] = maHigh/maLow
    df['RSI10'] = 100-(100/(1+df['RSI10']))

    return df

def __calculateBIAS(df):
    '''計算乖離率(bias), 公式為: (目前價格 - MA) / MA, 乖離率所衡量的就是現行股價與均線的差異程度。
    
    乖離率為正, 意即股價>平均線；乖離率為負, 意即股價<平均線。
    因為乖離率的計算和MA有關, 因此乖離率也會因為使用的日均線天數而有所不同。

    '''
    df['BIAS_5'] = 100*((df['close']-df['MA_5'])/df['MA_5'])
    df['BIAS_10'] = 100*((df['close']-df['MA_10'])/df['MA_10'])
    df['BIAS_20'] = 100*((df['close']-df['MA_20'])/df['MA_20'])
    df['B10-B20'] = df['BIAS_10'] - df['BIAS_20']
    return df

def __calculateWR(df):
    '''計算威廉指標
    
    以14天為計算週期

    原本的威廉指標，值越小時（收盤價越接近最高價），代表市場越處於超買中。
    
    有些會乘上(-1)使得該指標符合"指標值越大代表超買、越小則代表超賣的統一認知"。
    
    '''
    high = df['high'].rolling(9).max()
    low = df['low'].rolling(9).min()
    close = df['close']
    df['W%R9'] = 100 * ((high - close) / (high - low))
    return df

def __calculateBBI(df):
    '''計算多空指標(BBI), Bull and Bear Index, 將不同日數移動平均線加權平均之後的綜合指標, 屬於均線型指標。

    一般將3日、6日、12日和24日的四種sma(或ema)作為計算的參數。

    計算公式: BBI=(3日均價+6日均價+12日均價+24日均價)÷4

    '''
    # 分別計算3天, 6天, 12天和24天的移動平均線
    df['MA_3'] = df['close'].rolling(3).mean()
    df['MA_6'] = df['close'].rolling(6).mean()
    df['MA_12'] = df['close'].rolling(12).mean()
    df['MA_24'] = df['close'].rolling(20).mean()
    # df['MA_3'] = df['close'].ewm(span=3, adjust=False).mean()
    # df['MA_6'] = df['close'].ewm(span=6, adjust=False).mean()
    # df['MA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    # df['MA_24'] = df['close'].ewm(span=20, adjust=False).mean()
    df['M3'] = df['MA_3']
    df['BS'] = (df['MA_3']+df['MA_6']+df['MA_12']+df['MA_24'])/4
    df['M3-BS'] = df['M3'] - df['BS']
    # return df
    return df.drop(['MA_3', 'MA_6', 'MA_12', 'MA_24'], axis=1)

def __calculateCDP(df):
    '''計算CDP, Contrarian Operation 
    
    計算公式: CDP = (H+L+C*2)÷4 , H: 前一日最高價, L: 前一日最低價, C: 前一日收盤價

    '''

    df['CDP'] = (df['high']+df['low']+df['close']*2)/4
    df['AN'] = df['CDP'] + (df['high'] - df['low'])
    df['NH'] = df['CDP']*2 - df['low']
    df['AL'] = df['CDP'] - (df['high'] - df['low'])
    df['NL'] = df['CDP']*2 - df['high']

    return df

def __calculateDI(df):
    '''計算DI, Directional Movement Index, 這個指標是由四個指標組合而成, 分別是ADX,ADXR,PDI,MDI。
    
    '''

    df['HL'] = df['high'] - df['low']
    df['DM+'] = (df['high'] - df['close'].shift(1)).abs()
    df['DM-'] = (df['low'] - df['close'].shift(1)).abs()
    df['TR'] = df[['HL','DM+','DM-']].max(axis=1)
    del df['HL'], df['DM+'], df['DM-']

    # df['ATR'] = df['TR'].ewm(span=14, adjust=False).mean()
    df['ATR'] = df['TR'].rolling(14).mean()

    # +-DX
    df['HD'] = df['high'] - REF(df['high'], 1)
    df['LD'] = REF(df['low'], 1) - df['low'] 
    df['+DX'] = IF((df['HD'] > 0) & (df['HD'] > df['LD']), df['HD'], 0)
    df['S+DX'] = df['+DX'].rolling(14).mean()
    # df['S+DX'] = df['+DX'].ewm(span=14, adjust=False).mean()
    df['-DX'] = IF((df['LD'] > 0) & (df['LD'] > df['HD']), df['LD'], 0)
    df['S-DX'] = df['-DX'].rolling(14).mean()
    # df['S-DX'] = df['-DX'].ewm(span=14, adjust=False).mean()

    # +-DI
    df['+DI'] = (df['S+DX'] / df['ATR'])*100         
    df['-DI'] = (df['S-DX'] / df['ATR'])*100

    # ADX
    df['ADX'] = (np.abs(df['+DI'] - df['-DI'])/(df['+DI'] + df['-DI']))*100
    # df['ADX'] = pd.Series(np.abs(df['-DI'] - df['+DI']) / (df['+DI'] + df['-DI'])*100)
    df['ADX'] = df['ADX'].rolling(14).mean()
    df['S-DX'] = df['-DX'].ewm(span=14, adjust=False).mean()
    df['ADXR'] = (df['ADX'] + REF(df['ADX'], 14)) / 2

    # return df
    return df.drop(['+DX','-DX', 'S+DX','S-DX', 'TR', 'HD', 'LD'], axis=1)

def getStock(stockNo:int, start_date:str=None, end_date:str=None, period:str='D'):
    '''
    Parameters
    ----------
    stockNo   : int (required) 
        個股代號
    start     : str (optional) 
        查詢區間的起始時間, 預設為90天前(一個季), 必須是YYYYMMDD格式
    end       : str (optional) 
        查詢區間的結束時間, 預設為當天日期, 必須是YYYYMMDD格式
    period    : str (optional)
        指定使用日線周線月線
    '''
    if start_date == None:
        start_date = (datetime.today() - timedelta(days=180)).strftime("%Y%m%d")
    if end_date == None:
        end_date = datetime.today().strftime("%Y%m%d")

    stockInfo = getStockInformations(stockNo, start_date, end_date)
    stockName:str = ""
    with open('search.json', 'r', encoding='utf8') as inf:
        slist = json.load(inf)
        stockName = slist[str(stockNo)]
    
    
    if period=='W':
        stockInfo = __changePeriod(stockInfo)
    elif period=='M':
        stockInfo = __changePeriod(stockInfo, period='M')


    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')

    df = __calculateMA(df)

    df = __calculateKD(df)
    
    df = __calculateMACD(df)

    df = __calculateRSI(df)
    
    df = __calculateBIAS(df)

    df = __calculateWR(df)

    df = __calculateBBI(df)
    
    df = __calculateCDP(df)

    df = __calculateDI(df)

    df = df.drop(['stock_code_id'], axis=1)
    
    response = dict()
    response['stockNo'] = stockNo
    response['stockName'] = stockName
    data = json.loads(df.to_json(orient='records'))
    response['start_date'] = datetime.fromtimestamp(data[0]['date']).strftime('%Y%m%d')
    response['end_date'] = datetime.fromtimestamp(data[-1]['date']).strftime('%Y%m%d')
    dataList = []
    dateList = dict()
    for d in data:
        time = datetime.fromtimestamp(d['date']).strftime('%Y%m%d')
        d.pop('date')
        dataList.append(dict({time:d}))
        dateList[time] = d
    
    response['data'] = dateList
    return response