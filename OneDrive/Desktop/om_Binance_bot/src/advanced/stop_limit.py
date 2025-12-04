import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

#!/usr/bin/env python3
"""
Stop-Limit watcher for Binance USDT-M Futures (polling-based).

Usage:
  python src/advanced/stop_limit.py --symbol BTCUSDT --side SELL --stop-price 60000 --limit-price 59900 --qty 0.001 --check-interval 5 --timeout 3600 --testnet --dry-run

Meaning:
 - If side=SELL and last_price <= stop_price then place LIMIT SELL at limit_price.
 - If side=BUY  and last_price >= stop_price then place LIMIT BUY at limit_price.

Notes:
 - This script polls the symbol ticker periodically (check-interval).
 - Use --dry-run to simulate without sending orders.
 - Use --testnet for futures testnet (make sure keys point to testnet).
"""
import argparse
import os
import sys
import time
import math
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Reuse your utils
from src.utils.logging_config import setup_logger
from src.utils.validator import validate_symbol, validate_quantity, validate_price
import src.config as config

logger = setup_logger()

def get_client(use_testnet: bool):
    api_key = os.getenv('BINANCE_API_KEY') or getattr(config, 'API_KEY', None)
    api_secret = os.getenv('BINANCE_API_SECRET') or getattr(config, 'API_SECRET', None)
    if not api_key or not api_secret:
        raise EnvironmentError("Set BINANCE_API_KEY and BINANCE_API_SECRET in env or src/config.py")
    client = Client(api_key, api_secret)
    if use_testnet:
        client.API_URL = 'https://testnet.binancefuture.com'
    return client

def get_last_price(client: Client, symbol: str) -> float:
    t = client.futures_symbol_ticker(symbol=symbol)
    return float(t['price'])

def fetch_symbol_filters(client: Client, symbol: str):
    info = client.futures_exchange_info().get('symbols', [])
    for s in info:
        if s.get('symbol') == symbol:
            return {f['filterType']: f for f in s.get('filters', [])}
    return {}

def round_qty(qty: float, step_size: Optional[str]) -> float:
    if not step_size:
        return qty
    step = float(step_size)
    if step <= 0:
        return qty
    prec = max(0, int(round(-math.log10(step))))
    floored = math.floor(qty/step) * step
    return round(floored, prec)

def round_price(price: float, tick_size: Optional[str]) -> float:
    if not tick_size:
        return price
    tick = float(tick_size)
    if tick <= 0:
        return price
    prec = max(0, int(round(-math.log10(tick))))
    floored = math.floor(price / tick) * tick
    return round(floored, prec)

def place_limit_order(client: Client, symbol: str, side: str, qty: float, price: float, dry_run: bool=False):
    logger.info(f"Placing LIMIT {side} {qty} {symbol} @ {price} (dry={dry_run})")
    if dry_run:
        return {"status":"DRY_RUN","symbol":symbol,"side":side,"qty":qty,"price":price,"time":int(time.time())}
    return client.futures_create_order(
        symbol=symbol,
        side=side,
        type='LIMIT',
        timeInForce='GTC',
        quantity=str(qty),
        price=str(price)
    )

def stop_limit_watch(client: Client, symbol: str, side: str, stop_price: float, limit_price: float,
                     qty: float, check_interval: int, timeout: int, dry_run: bool=False):
    start = time.time()
    logger.info(f"Starting stop-limit watch: {side} {qty} {symbol}, stop={stop_price}, limit={limit_price}, interval={check_interval}s, timeout={timeout}s")
    # get filters
    filters = fetch_symbol_filters(client, symbol)
    step_size = None
    tick_size = None
    if 'LOT_SIZE' in filters:
        step_size = filters['LOT_SIZE'].get('stepSize')
    if 'PRICE_FILTER' in filters:
        tick_size = filters['PRICE_FILTER'].get('tickSize')

    qty_adj = round_qty(qty, step_size)
    limit_price_adj = round_price(limit_price, tick_size)

    if qty_adj <= 0:
        raise ValueError("Adjusted quantity is 0. Check stepSize and input qty.")

    logger.info(f"Adjusted qty={qty_adj} (step={step_size}), limit_price={limit_price_adj} (tick={tick_size})")

    while True:
        now = time.time()
        if timeout and (now - start) > timeout:
            logger.info("Timeout reached without trigger. Exiting watch.")
            return {"status":"TIMEOUT"}
        try:
            last_price = get_last_price(client, symbol)
            logger.info(f"Market price for {symbol}: {last_price}")
            triggered = False
            if side.upper() == 'SELL':
                # Sell stop: trigger when price <= stop_price
                if last_price <= stop_price:
                    triggered = True
            else: # BUY
                # Buy stop: trigger when price >= stop_price
                if last_price >= stop_price:
                    triggered = True

            if triggered:
                logger.info(f"Stop price reached (last={last_price}). Placing limit order...")
                resp = place_limit_order(client, symbol, side, qty_adj, limit_price_adj, dry_run=dry_run)
                logger.info(f"Limit order response: {resp}")
                return {"status":"FILLED_OR_SENT","response":resp,"trigger_price":last_price}
            # else sleep and continue
            time.sleep(check_interval)
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.exception(f"Binance API error while watching price: {e}")
            time.sleep(check_interval)
        except Exception as e:
            logger.exception(f"Unexpected error in watch loop: {e}")
            time.sleep(check_interval)

def parse_args():
    p = argparse.ArgumentParser(description="Stop-Limit watcher (polling) for Binance Futures")
    p.add_argument('--symbol','-s', required=True, help='Symbol e.g. BTCUSDT')
    p.add_argument('--side','-S', required=True, choices=['BUY','SELL'], help='BUY or SELL for the LIMIT order to place when triggered')
    p.add_argument('--stop-price', required=True, type=float, help='Stop trigger price')
    p.add_argument('--limit-price', required=True, type=float, help='Limit price to place once triggered')
    p.add_argument('--qty','-q', required=True, help='Quantity to trade')
    p.add_argument('--check-interval', type=int, default=5, help='Seconds between price checks (default 5)')
    p.add_argument('--timeout', type=int, default=3600, help='Overall timeout in seconds (default 3600)')
    p.add_argument('--testnet', action='store_true', help='Use futures testnet')
    p.add_argument('--dry-run', action='store_true', help='Simulate without sending order')
    return p.parse_args()

def main():
    args = parse_args()
    symbol = args.symbol.upper()
    side = args.side.upper()
    try:
        if not validate_symbol(symbol):
            raise ValueError("Invalid symbol format")
        qty = validate_quantity(args.qty)
        stop_price = validate_price(args.stop_price)
        limit_price = validate_price(args.limit_price)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        print("Validation error:", e)
        sys.exit(1)

    client = get_client(args.testnet)
    result = stop_limit_watch(client, symbol, side, stop_price, limit_price, qty,
                              check_interval=args.check_interval, timeout=args.timeout,
                              dry_run=args.dry_run)
    print(result)

if __name__ == '__main__':
    main()
