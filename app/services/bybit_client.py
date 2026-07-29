"""Cliente para la API v5 de Bybit y fallbacks a Binance (datos de mercado y gráficos candlestick)."""

import requests
import pandas as pd

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}


def safe_request(url, params=None, headers=None, timeout=15):
    """Encapsula solicitudes HTTP GET hacia APIs de criptomonedas con manejo de errores, User-Agent y timeouts."""
    req_headers = DEFAULT_HEADERS.copy()
    if headers:
        req_headers.update(headers)
    try:
        response = requests.get(url, params=params, headers=req_headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"API request failed for {url}: {exc}")
        return None


def get_symbols():
    """Obtiene la lista de pares de mercado Spot disponibles en Bybit o Binance."""
    url = 'https://api.bybit.com/v5/market/instruments-info'
    params = {'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            symbols_raw = result.get('list', []) or []
            if symbols_raw:
                symbols = []
                for s in symbols_raw:
                    if isinstance(s, dict):
                        name = s.get('symbol') or s.get('name')
                        if name and name.endswith('USDT'):
                            symbols.append({'name': name, 'symbol': name})
                if symbols:
                    return symbols
        elif 'list' in data and data['list']:
            return [{'name': s.get('symbol', s.get('name')), 'symbol': s.get('symbol', s.get('name'))}
                    for s in data['list'] if isinstance(s, dict)]

    # Fallback 1: Binance exchangeInfo
    b_data = safe_request('https://api.binance.com/api/v3/exchangeInfo')
    if isinstance(b_data, dict) and 'symbols' in b_data:
        symbols = [
            {'name': s['symbol'], 'symbol': s['symbol']}
            for s in b_data['symbols']
            if isinstance(s, dict) and s.get('status') == 'TRADING' and s.get('symbol', '').endswith('USDT')
        ]
        if symbols:
            return symbols

    # Fallback 2: Lista estática predeterminada
    return [
        {'name': 'BTCUSDT', 'symbol': 'BTCUSDT'},
        {'name': 'ETHUSDT', 'symbol': 'ETHUSDT'},
        {'name': 'BNBUSDT', 'symbol': 'BNBUSDT'},
        {'name': 'SOLUSDT', 'symbol': 'SOLUSDT'},
        {'name': 'ADAUSDT', 'symbol': 'ADAUSDT'},
        {'name': 'XRPUSDT', 'symbol': 'XRPUSDT'},
        {'name': 'DOGEUSDT', 'symbol': 'DOGEUSDT'},
    ]


def get_symbol_info(symbol):
    """Obtiene la información y precio actual en tiempo real de un símbolo (Bybit con fallback a Binance y Coinbase)."""
    symbol = (symbol or 'BTCUSDT').upper().strip()
    url = 'https://api.bybit.com/v5/market/tickers'
    params = {'symbol': symbol, 'category': 'spot'}
    data = safe_request(url, params=params)
    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict):
            ticker_list = result.get('list', []) or []
            if ticker_list and isinstance(ticker_list[0], dict) and float(ticker_list[0].get('lastPrice', 0)) > 0:
                return ticker_list

    # Fallback 1: Binance Global API
    b_data = safe_request('https://api.binance.com/api/v3/ticker/24hr', params={'symbol': symbol})
    if not (isinstance(b_data, dict) and 'lastPrice' in b_data):
        # Fallback 2: Binance US API
        b_data = safe_request('https://api.binance.us/api/v3/ticker/24hr', params={'symbol': symbol})

    if isinstance(b_data, dict) and 'lastPrice' in b_data:
        try:
            pct = float(b_data.get('priceChangePercent', 0)) / 100.0
        except (ValueError, TypeError):
            pct = 0.0
        return [{
            'symbol': b_data.get('symbol', symbol),
            'lastPrice': str(b_data.get('lastPrice', '0')),
            'highPrice24h': str(b_data.get('highPrice', b_data.get('lastPrice', '0'))),
            'lowPrice24h': str(b_data.get('lowPrice', b_data.get('lastPrice', '0'))),
            'price24hPcnt': str(pct),
            'volume24h': str(b_data.get('volume', '0'))
        }]

    # Fallback 3: Coinbase API (para cuando Bybit y Binance presenten bloqueos de IP/WAF)
    base_currency = symbol.replace('USDT', '').replace('USD', '')
    cb_spot = safe_request(f'https://api.coinbase.com/v2/prices/{base_currency}-USD/spot')
    if isinstance(cb_spot, dict) and 'data' in cb_spot and 'amount' in cb_spot['data']:
        price = cb_spot['data']['amount']
        cb_stats = safe_request(f'https://api.exchange.coinbase.com/products/{base_currency}-USD/stats')
        high = price
        low = price
        pct = '0'
        vol = '0'
        if isinstance(cb_stats, dict):
            high = cb_stats.get('high', price)
            low = cb_stats.get('low', price)
            vol = cb_stats.get('volume', '0')
            open_p = float(cb_stats.get('open', price))
            last_p = float(price)
            if open_p > 0:
                pct = str((last_p - open_p) / open_p)

        return [{
            'symbol': symbol,
            'lastPrice': str(price),
            'highPrice24h': str(high),
            'lowPrice24h': str(low),
            'price24hPcnt': pct,
            'volume24h': str(vol)
        }]

    return []


def get_candlestick_data(symbol, interval, limit):
    """Obtiene datos de kline/candlestick (OHLC) de Bybit (con fallback a Binance y Coinbase)."""
    symbol = (symbol or 'BTCUSDT').upper().strip()
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

    if isinstance(data, dict):
        result = data.get('result')
        if isinstance(result, dict) and 'list' in result and result['list']:
            raw_list = result['list']
            records = []
            for row in raw_list:
                try:
                    records.append({
                        'times': pd.to_datetime(int(row[0]) / 1000, unit='s'),
                        'open': float(row[1]),
                        'high': float(row[2]),
                        'low': float(row[3]),
                        'close': float(row[4])
                    })
                except (IndexError, ValueError, TypeError):
                    continue
            if records:
                df = pd.DataFrame(records)
                df = df.sort_values(by='times').reset_index(drop=True)
                return df

    # Fallback 1: Binance klines
    binance_interval_map = {
        '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
        '1h': '1h', '4h': '4h', '12h': '12h', '1d': '1d', 'd': '1d',
        '1w': '1w', 'w': '1w', '1m': '1M', 'm': '1M'
    }
    b_interval = binance_interval_map.get(str(interval).lower(), '15m')
    b_data = safe_request('https://api.binance.com/api/v3/klines', params={
        'symbol': symbol,
        'interval': b_interval,
        'limit': limit
    })
    if not (isinstance(b_data, list) and len(b_data) > 0):
        b_data = safe_request('https://api.binance.us/api/v3/klines', params={
            'symbol': symbol,
            'interval': b_interval,
            'limit': limit
        })

    if isinstance(b_data, list) and len(b_data) > 0:
        try:
            records = []
            for row in b_data:
                records.append({
                    'times': pd.to_datetime(int(row[0]) / 1000, unit='s'),
                    'open': float(row[1]),
                    'high': float(row[2]),
                    'low': float(row[3]),
                    'close': float(row[4])
                })
            df = pd.DataFrame(records)
            df = df.sort_values(by='times').reset_index(drop=True)
            return df
        except Exception as exc:
            print(f"Error parsing Binance klines: {exc}")

    # Fallback 2: Coinbase candles
    base_currency = symbol.replace('USDT', '').replace('USD', '')
    cb_candles = safe_request(f'https://api.exchange.coinbase.com/products/{base_currency}-USD/candles', params={'granularity': 900})
    if isinstance(cb_candles, list) and len(cb_candles) > 0:
        try:
            records = []
            for row in cb_candles[:limit]:
                records.append({
                    'times': pd.to_datetime(int(row[0]), unit='s'),
                    'open': float(row[3]),
                    'high': float(row[2]),
                    'low': float(row[1]),
                    'close': float(row[4])
                })
            df = pd.DataFrame(records)
            df = df.sort_values(by='times').reset_index(drop=True)
            return df
        except Exception as exc:
            print(f"Error parsing Coinbase candles: {exc}")

    return empty

