"""Cliente para la API v5 de Bybit (datos de mercado y gráficos candlestick)."""

import requests
import pandas as pd


def safe_request(url, params=None, headers=None, timeout=15):
    """Encapsula solicitudes HTTP GET hacia Bybit con manejo de errores y timeouts."""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"Bybit API request failed for {url}: {exc}")
        return None


def get_symbols():
    """Obtiene la lista de pares de mercado Spot disponibles en Bybit."""
    url = 'https://api.bybit.com/v5/market/symbols'
    params = {'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            return result.get('list', []) or []
        return data.get('list', []) or []
    # Fallback si falla la API
    return [
        {'name': 'BTCUSDT'},
        {'name': 'ETHUSDT'},
        {'name': 'BNBUSDT'},
        {'name': 'SOLUSDT'},
        {'name': 'ADAUSDT'},
    ]


def get_symbol_info(symbol):
    """Obtiene la información y precio actual en tiempo real de un símbolo específico."""
    url = 'https://api.bybit.com/v5/market/tickers'
    params = {'symbol': symbol, 'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            return result.get('list', []) or []
    return []


def get_candlestick_data(symbol, interval, limit):
    """Obtiene datos de kline/candlestick (OHLC) de Bybit y devuelve un DataFrame procesado."""
    url = 'https://api.bybit.com/v5/market/kline'

    # Mapeo de intervalos amigables al formato exigido por Bybit v5
    interval_map = {
        '1m': '1', '5m': '5', '15m': '15', '30m': '30',
        '1h': '60', '4h': '240', '12h': '720', '1d': 'D', 'd': 'D',
        '1w': 'W', 'w': 'W', '1m': 'M', 'm': 'M'
    }
    bybit_interval = interval_map.get(str(interval).lower(), str(interval))

    params = {
        'symbol': symbol,
        'interval': bybit_interval,
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

    # Transformación de timestamps y columnas OHLC
    df['times'] = pd.to_datetime(df['list'].apply(lambda x: int(x[0]) / 1000), unit='s')
    df['open'] = df['list'].apply(lambda x: x[1])
    df['high'] = df['list'].apply(lambda x: x[2])
    df['low'] = df['list'].apply(lambda x: x[3])
    df['close'] = df['list'].apply(lambda x: x[4])
    df = df.drop(['category', 'symbol', 'list'], axis=1, errors='ignore')
    df = df.sort_values(by='times')
    return df

