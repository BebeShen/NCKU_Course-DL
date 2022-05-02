import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import json_normalize
from datetime import datetime, timedelta

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
    return  S.rolling(N).sum() if N>0 else pd.Series(S).cumsum()

#   對序列整體下移動N,返回序列(shift後會產生NAN)
def REF(S:pd.DataFrame, N:int):
    return pd.Series(S).shift(N).values  

def IF(S_BOOL,S_TRUE,S_FALSE):          
    return np.where(S_BOOL, S_TRUE, S_FALSE)

#   序列max
def MAX(S1,S2):  
    return np.maximum(S1,S2)    

def __calculateMA(stockInfo):
    '''計算移動平均線(MA), 將N天的收盤價加總後再除以N, 即得到第N天的算術平均線數值。
    
    常用的日線有: 5日線, 10日線, 20日線, 60日線, 120日線, 240日線。
    '''
    if stockInfo == None:
        return "No stock information to calculate MA"

    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    df['close'] = pd.to_numeric(df['close'])
    # 分別計算5天, 10天, 20天和60天的移動平均線
    df['MA_5'] = df['close'].rolling(5).mean()
    df['MA_10'] = df['close'].rolling(10).mean()
    df['MA_20'] = df['close'].rolling(20).mean()
    # df['MA_60'] = df['close'].rolling(60).mean()
    # close = [d['close'] for d in stockInfo]
    # ma5 = np.round(np.mean(close[0:5]),2)
    # ma10 = np.round(np.mean(close[0:10]),2)
    # ma20 = np.round(np.mean(close[0:20]),2)
    # ma60 = np.round(np.mean(close[0:60]),2)
    return df.loc[:, ['MA_5','MA_10','MA_20']]
    
def __calculateKD(stockInfo):
    '''計算KD值
    
    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    close, high, low = df.close, df.high, df.low
    
    # 計算9日內最高成交價
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df = df.set_index('date')

    df['9daymax'] = df['high'].rolling('9D').max()
    df['9daymin'] = df['low'].rolling('9D').min()
    # print(df['9daymax'], df['9daymin'])
    df['RSV'] = 0
    df['RSV'] = 100 * (df['close'] - df['9daymin']) / (df['9daymax'] - df['9daymin'])
    # print(df['RSV'])

    # 計算k值 計算d值
    K=[50]
    D=[50]
    for i in range(len(df['RSV'])):
        KValue = (2/3)*K[-1] + (df['RSV'][i]/3)
        DValue = (2/3)*D[-1] + KValue/3
        K.append(KValue)
        D.append(DValue)
    K=pd.Series(K[1:], index=df['RSV'].index)
    K.name='KValue'
    D=pd.Series(D[1:], index=df['RSV'].index)
    D.name='DValue'
    df['k'] = K
    df['d'] = D
    # df.reset_index(inplace=True)
    # df['date'] = pd.to_datetime(df['date'], unit='s')
    return df.loc[:, ['RSV','k','d']]

def __calculateMACD(stockInfo):
    '''MACD, Moving Average Convergence and Divergence, 股市中常說的平滑異同移動平均線。由DIF、DEA、MACD組成

    MA分成EMA(exponential)和SMA(mean), 這裡使用EMA

    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    df['close'] = pd.to_numeric(df['close'])
    #我們分別計算7天,15天與30天的移動平均線
    df['MA_7'] = df['close'].rolling(7).mean()
    df['MA_15'] = df['close'].rolling(15).mean()
    df['MA_30'] = df['close'].rolling(30).mean()
    # com=1 代表權重為 1/(com+1) = 1/2
    df['EMA_12'] = df['close'].ewm(com=1, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(com=1, adjust=False).mean()
    df['EMA_12'] = df['EMA_12'].rolling(12).mean()
    df['EMA_26'] = df['EMA_26'].rolling(26).mean()
    # 差離值
    df['DIF'] = df['EMA_12'] - df['EMA_26']
    # 差離平均值
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    # 柱狀值
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    return df.loc[:, ['DIF','DEA','MACD']]

def __calculateRSI(stockInfo):
    '''計算RSI值
    
    RSI是計算過去一段時間的相對強弱, 這個"一段時間"是看個人選擇要多長的時間, 一般比較常見的是6日、12日、14日、24日。

    一樣預設使用EMA

    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    df['close'] = pd.to_numeric(df['close'])
    close_delta = df['close'].diff()

    high = close_delta.clip(lower=0)
    low = -1*close_delta.clip(upper=0)

    period = 14
    maHigh = high.ewm(com=period-1, adjust=True, min_periods=period).mean()
    maLow = low.ewm(com=period-1, adjust=True, min_periods=period).mean()

    df['RSI'] = maHigh/maLow
    df['RSI'] = 100-(100/(1+df['RSI']))
    return df.loc[:, ['RSI']]

def __calculateBIAS(stockInfo):
    '''計算乖離率(bias), 公式為: (目前價格 - MA) / MA, 乖離率所衡量的就是現行股價與均線的差異程度。
    
    乖離率為正, 意即股價>平均線；乖離率為負, 意即股價<平均線。
    因為乖離率的計算和MA有關, 因此乖離率也會因為使用的日均線天數而有所不同。

    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')

    df['MA_5'] = df['close'].rolling(5).mean()
    df['MA_10'] = df['close'].rolling(10).mean()
    df['MA_20'] = df['close'].rolling(20).mean()

    df['BIAS_5'] = 100*((df['close']-df['MA_5'])/df['MA_5'])
    df['BIAS_10'] = 100*((df['close']-df['MA_10'])/df['MA_10'])
    df['BIAS_20'] = 100*((df['close']-df['MA_20'])/df['MA_20'])
    return df.loc[:, ['BIAS_5','BIAS_10','BIAS_20']]

def __calculateWR(stockInfo):
    '''計算威廉指標
    
    以14天為計算週期

    原本的威廉指標，值越小時（收盤價越接近最高價），代表市場越處於超買中，因此乘上(-1)使得該指標符合"指標值越大代表超買、越小則代表超賣的統一認知"。
    
    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    high = df['high'].rolling(14).max()
    low = df['low'].rolling(14).min()
    close = df['close']
    df['WR'] = -100 * ((high - close) / (high - low))
    return df.loc[:, ['WR']]

def __calculateBBI(stockInfo):
    '''計算多空指標(BBI), Bull and Bear Index, 將不同日數移動平均線加權平均之後的綜合指標, 屬於均線型指標。

    一般將3日、6日、12日和24日的四種sma(或ema)作為計算的參數。

    計算公式: BBI=(3日均價+6日均價+12日均價+24日均價)÷4

    '''
    
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    df['close'] = pd.to_numeric(df['close'])
    # 分別計算3天, 6天, 12天和24天的移動平均線
    df['MA_3'] = df['close'].rolling(3).mean()
    df['MA_6'] = df['close'].rolling(6).mean()
    df['MA_12'] = df['close'].rolling(12).mean()
    df['MA_24'] = df['close'].rolling(24).mean()
    df['BBI'] = (df['MA_3']+df['MA_6']+df['MA_12']+df['MA_24'])/4

    return df.loc[:, ['BBI']]

def __calculateCDP(stockInfo):
    '''計算CDP, Contrarian Operation 
    
    計算公式: CDP = (H+L+C*2)÷4 , H: 前一日最高價, L: 前一日最低價, C: 前一日收盤價

    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])

    df['CDP'] = (df['high']+df['low']+df['close']*2)/4
    df['AN'] = df['CDP'] + (df['high'] - df['low'])
    df['NH'] = df['CDP']*2 - df['low']
    df['AL'] = df['CDP'] - (df['high'] - df['low'])
    df['NL'] = df['CDP']*2 - df['high']

    return df.loc[:, ['CDP']]

def __calculateDMI(stockInfo):
    '''計算DMI, Directional Movement Index, 這個指標是由四個指標組合而成, 分別是ADX,ADXR,PDI,MDI。
    
    '''
    df = json_normalize(stockInfo)
    df = df.sort_values(by=['date'], ascending=True)
    df.index = pd.to_datetime(df['date'], unit='s')
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])

    df['TR'] = (np.maximum(np.maximum(df['high']-df['low'], np.abs(df['high']-pd.Series(df['close']).shift(1).values)), np.abs(df['low']-pd.Series(df['close']).shift(1).values)))
    df['TR'] = df['TR'].rolling(14).sum()
    df['HD'] = df['high'] - REF(df['high'], 1)
    df['LD'] = REF(df['low'], 1) - df['low'] 
    df['DMP'] = IF((df['HD'] > 0) & (df['HD'] > df['LD']), df['HD'], 0)
    df['DMP'] = df['DMP'].rolling(14).mean()
    df['DMM'] = IF((df['LD'] > 0) & (df['LD'] > df['HD']), df['LD'], 0)
    df['DMM'] = df['DMM'].rolling(14).mean()
    df['PDI'] = df['DMP'] * 100 / df['TR'];         
    df['MDI'] = df['DMM'] * 100 / df['TR']
    df['ADX'] = pd.Series(np.abs(df['MDI'] - df['PDI']) / (df['PDI'] + df['MDI']) * 100)
    df['ADX'] = df['ADX'].rolling(14).mean()
    df['ADXR'] = (df['ADX'] + REF(df['ADX'], 14)) / 2
    # print(df)
    return df.loc[:, ['PDI','MDI','ADX','ADXR']]

def getStock(stockNo:int, start_date:str=None, end_date:str=None):
    '''
    Parameters
    ----------
    stockNo   : int (required) 
        個股代號
    start     : str (optional) 
        查詢區間的起始時間, 預設為90天前(一個季), 必須是YYYYMMDD格式
    end       : str (optional) 
        查詢區間的結束時間, 預設為當天日期, 必須是YYYYMMDD格式
    '''
    if start_date == None:
        start_date = (datetime.today() - timedelta(days=90)).strftime("%Y%m%d")
    if end_date == None:
        end_date = datetime.today().strftime("%Y%m%d")

    response = dict()
    response['stockNo'] = stockNo

    data = dict()
    stockInfo = getStockInformations(stockNo, start_date, end_date)
    
    ma = __calculateMA(stockInfo)
    ma['date'] = ma.index
    ma['date'] = ma['date'].dt.strftime('%Y-%m-%d')
    ma = json.loads(ma.to_json(orient='records'))
    data['ma'] = ma

    kd = __calculateKD(stockInfo)
    kd['date'] = kd.index
    kd['date'] = kd['date'].dt.strftime('%Y-%m-%d')
    kd = json.loads(kd.to_json(orient='records'))
    data['kd'] = kd

    macd = __calculateMACD(stockInfo)
    macd['date'] = macd.index
    macd['date'] = macd['date'].dt.strftime('%Y-%m-%d')
    macd = json.loads(macd.to_json(orient='records'))
    data['macd'] = macd

    rsi = __calculateRSI(stockInfo)
    rsi['date'] = rsi.index
    rsi['date'] = rsi['date'].dt.strftime('%Y-%m-%d')
    rsi = json.loads(rsi.to_json(orient='records'))
    data['rsi'] = rsi

    bias = __calculateBIAS(stockInfo)
    bias['date'] = bias.index
    bias['date'] = bias['date'].dt.strftime('%Y-%m-%d')
    bias = json.loads(bias.to_json(orient='records'))
    data['bias'] = bias
    
    wr = __calculateWR(stockInfo)
    wr['date'] = wr.index
    wr['date'] = wr['date'].dt.strftime('%Y-%m-%d')
    wr = json.loads(wr.to_json(orient='records'))
    data['wr'] = wr

    bbi = __calculateBBI(stockInfo)
    bbi['date'] = bbi.index
    bbi['date'] = bbi['date'].dt.strftime('%Y-%m-%d')
    bbi = json.loads(bbi.to_json(orient='records'))
    data['bbi'] = bbi

    cdp = __calculateCDP(stockInfo)
    cdp['date'] = cdp.index
    cdp['date'] = cdp['date'].dt.strftime('%Y-%m-%d')
    cdp = json.loads(cdp.to_json(orient='records'))
    data['cdp'] = cdp

    
    dmi = __calculateDMI(stockInfo)
    dmi['date'] = dmi.index
    dmi['date'] = dmi['date'].dt.strftime('%Y-%m-%d')
    dmi = json.loads(dmi.to_json(orient='records'))
    data['dmi'] = dmi
    # print(data['dmi'])
    print(json.dumps(data, indent=4, sort_keys=True))
