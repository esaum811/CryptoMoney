import requests
import pandas as pd


def safe_request(url, params=None, headers=None, timeout=15):
    """Wrapper for HTTP GET requests with error handling."""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"Bybit API request failed for {url}: {exc}")
        return None


def get_symbols():
    """Fetch all spot trading pairs from Bybit v5 API."""
    url = 'https://api.bybit.com/v5/market/symbols'
    params = {'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            return result.get('list', []) or []
        return data.get('list', []) or []
    return [
        {'name': 'BTCUSDT'},
        {'name': 'ETHUSDT'},
        {'name': 'BNBUSDT'},
        {'name': 'SOLUSDT'},
        {'name': 'ADAUSDT'},
    ]


def get_symbol_info(symbol):
    """Get real-time ticker info for a specific symbol."""
    url = 'https://api.bybit.com/v5/market/tickers'
    params = {'symbol': symbol, 'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            return result.get('list', []) or []
    return []


def get_candlestick_data(symbol, interval, limit):
    """Fetch OHLC candlestick data and return as DataFrame."""
    url = 'https://api.bybit.com/v5/market/kline'
    params = {
        'symbol': symbol,
        'interval': interval,
        'category': 'spot',
        'limit': limit,
    }
    data = safe_request(url, params=params)
    empty = pd.DataFrame(columns=['times', 'open', 'high', 'low', 'close'])
    if not isinstance(data, dict):
        return empty
    result = data.get('result')
    if not isinstance(result, dict) or 'list' not in result:
        return empty
    df = pd.DataFrame(result)
    if 'list' not in df.columns:
        return empty
    df['times'] = pd.to_datetime(df['list'].apply(lambda x: int(x[0]) / 1000), unit='s')
    df['open'] = df['list'].apply(lambda x: x[1])
    df['high'] = df['list'].apply(lambda x: x[2])
    df['low'] = df['list'].apply(lambda x: x[3])
    df['close'] = df['list'].apply(lambda x: x[4])
    df = df.drop(['category', 'symbol', 'list'], axis=1, errors='ignore')
    df = df.sort_values(by='times')
    return df
