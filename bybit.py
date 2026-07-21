import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'


def safe_request(url, params=None, headers=None, timeout=15):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"Bybit API request failed for {url}: {exc}")
        try:
            print("Bybit response:", response.text[:400])
        except Exception:
            pass
        return None


def get_symbols():
    url = 'https://api.bybit.com/v5/market/symbols'
    params = {'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            return result.get('list', []) or []
        return data.get('list', []) or []

    # Fallback symbols when API is unavailable
    return [
        {'name': 'BTCUSDT'},
        {'name': 'ETHUSDT'},
        {'name': 'BNBUSDT'},
        {'name': 'SOLUSDT'},
        {'name': 'ADAUSDT'},
    ]


def get_symbol_info(symbol):
    url = 'https://api.bybit.com/v5/market/tickers'
    params = {
        'symbol': symbol,
        'category': 'spot',
    }
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            return result.get('list', []) or []
    return []


def get_candlestick_data(symbol, interval, limit):
    print(symbol, interval)
    url = 'https://api.bybit.com/v5/market/kline'
    params = {
        'symbol': symbol,
        'interval': interval,
        'category': 'spot',
        'limit': limit,
    }
    data = safe_request(url, params=params)
    if not isinstance(data, dict):
        return pd.DataFrame(columns=['times', 'open', 'high', 'low', 'close'])

    result = data.get('result')
    if not isinstance(result, dict) or 'list' not in result:
        return pd.DataFrame(columns=['times', 'open', 'high', 'low', 'close'])

    df = pd.DataFrame(result)
    if 'list' not in df.columns:
        return pd.DataFrame(columns=['times', 'open', 'high', 'low', 'close'])

    df['times'] = pd.to_datetime(df['list'].apply(lambda x: int(x[0]) / 1000), unit='s')
    df['open'] = df['list'].apply(lambda x: x[1])
    df['high'] = df['list'].apply(lambda x: x[2])
    df['low'] = df['list'].apply(lambda x: x[3])
    df['close'] = df['list'].apply(lambda x: x[4])
    df = df.drop(['category', 'symbol', 'list'], axis=1, errors='ignore')
    df = df.sort_values(by='times')
    print(df)
    return df