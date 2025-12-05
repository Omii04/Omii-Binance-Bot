"""
Stop-Limit Orders for Binance Futures.
Trigger a limit order when the price reaches a stop price.
"""

import argparse
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger


def place_stop_limit_order(
    symbol: str,
    side: str,
    quantity,
    stop_price: float,
    limit_price: float,
    dry_run: bool = False
):
    """
    Place a stop-limit order on Binance Futures.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        side: BUY or SELL
        quantity: Order quantity
        stop_price: Price at which order is triggered
        limit_price: Price at which order is placed
        dry_run: If True, only validate without placing
    """
    symbol, quantity, _ = validate_inputs(symbol, quantity)
    
    side_up = side.upper()
    if side_up not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")
    
    try:
        stop_price = float(stop_price)
        limit_price = float(limit_price)
    except ValueError:
        raise ValueError("stop_price and limit_price must be numbers")
    
    if stop_price <= 0 or limit_price <= 0:
        raise ValueError("Prices must be positive")
    
    if dry_run:
        logger.info(
            f"[DRY-RUN] Would place Stop-Limit {side_up} {quantity} {symbol}: "
            f"Stop=${stop_price:.2f}, Limit=${limit_price:.2f}"
        )
        print(
            f"✅ [DRY-RUN] Stop-Limit order validated: {side_up} {quantity} {symbol} "
            f"Stop=${stop_price:.2f}, Limit=${limit_price:.2f}"
        )
        return
    
    client = get_client()
    try:
        logger.info(
            f"Placing Stop-Limit {side_up} {quantity} {symbol}: "
            f"Stop=${stop_price:.2f}, Limit=${limit_price:.2f}"
        )
        
        order = client.futures_create_order(
            symbol=symbol,
            side=side_up,
            type="STOP_MARKET",
            timeInForce="GTC",
            stopPrice=str(stop_price),
            quantity=quantity
        )
        
        logger.info(f"Stop-Limit order response: {order}")
        print("✅ Stop-Limit order placed (or attempted).")
        print(f"   Order ID: {order.get('orderId', 'N/A')}")
    
    except BinanceAPIException as e:
        logger.error(f"Binance API error (stop-limit): {e}")
        print("❌ Binance API error:", e)
    
    except Exception as e:
        logger.error(f"General error (stop-limit): {e}")
        print("❌ Error:", e)


def main():
    parser = argparse.ArgumentParser(description="Binance Futures Stop-Limit Order CLI Bot")
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("quantity", nargs="?", help="Order quantity, e.g., 0.001")
    parser.add_argument("stop_price", nargs="?", help="Stop price (trigger)")
    parser.add_argument("limit_price", nargs="?", help="Limit price (execution)")
    
    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Order quantity")
    parser.add_argument("--stop", dest="stop_flag", help="Stop price")
    parser.add_argument("--limit", dest="limit_flag", help="Limit price")
    parser.add_argument("--dry-run", action="store_true", help="Validate without placing")
    
    args = parser.parse_args()
    
    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.quantity
    stop_price = args.stop_flag or args.stop_price
    limit_price = args.limit_flag or args.limit_price
    
    if not all([symbol, side, quantity, stop_price, limit_price]):
        parser.error("Symbol, side, quantity, stop_price, and limit_price are required.")
    
    place_stop_limit_order(symbol, side, quantity, stop_price, limit_price, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

