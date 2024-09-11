from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep

session = HTTP(
    api_key=api,
    api_secret=secret
)

timeframe = 15

def get_balance():
    try:
        resp = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")['result']['list'][0]['coin'][0]['walletBalance']
        resp = float(resp)
        return resp
    except Exception as err:
        print(err)

print(f'Your Balance: {get_balance()} USDT')

def get_tickers():
    try:
        resp = session.get_tickers(category="linear")['result']['list']
        symbols = []
        for elem in resp:
            if 'USDT' in elem['symbol'] and not 'USDC' in elem['symbol']:
                symbols.append(elem['symbol'])
        return symbols
    except Exception as err:
        print(err)

def klines(symbol):
    try:
        resp = session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=500
        )['result']['list']
        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        resp = resp.set_index('Time')
        resp = resp.astype(float)
        resp = resp[::1]
        return resp

    except Exception as err:
        print(err)

def get_positions():
    try:
        resp = session.get_positions(
            category='linear',
            settleCoin='USDT'
        )['result']['list']

        pos = []
        for elem in resp:
            pos.append(elem['symbol'])

        return pos
    except Exception as err:
        print(err)

def rsi_signal(symbol):
    kl = klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'up'
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'down'
    else:
        return 'none'

max_pos = 50
symbols = get_tickers()

while True:
    balance = get_balance()
    if balance is None:
        print('API not connected')
    if balance is not None:
        print(f'Balance: {balance}')
        pos = get_positions()
        print(f'You have {len(pos)} positions: {pos}')

        if len(pos) <= max_pos:
            for elem in symbols:
                pos = get_positions()
                if len(pos) > max_pos:
                    break
                signal = rsi_signal(elem)
                if signal == 'up' and elem not in pos:
                    print(f'Found RSI BUY signal for {elem}')
                    sleep(2)
                if signal == 'down' and elem not in pos:
                    print(f'Found RSI SELL signal for {elem}')
                    sleep(2)
    print('Waiting 2 mins')
    sleep(120)
