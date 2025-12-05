"""
Grid Trading Strategy for Binance Futures.
Automatically place buy orders below current price and sell orders above.
Captures profit on price fluctuations within a defined range.
"""

import argparse
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger


def place_grid_orders(
    symbol: str,
    side: str,
    quantity,
    lower_price: float,
    upper_price: float,
    grid_levels: int = 5,
    dry_run: bool = False
):
    """
    Place a grid of orders for buy-low/sell-high strategy.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        side: BUY or SELL (direction of initial grid)
        quantity: Total quantity to divide among grid levels
        lower_price: Lower bound of grid range
        upper_price: Upper bound of grid range
        grid_levels: Number of grid levels (default: 5)
        dry_run: If True, only validate without placing
    """
    symbol, total_quantity, _ = validate_inputs(symbol, quantity)
    
    side_up = side.upper()
    if side_up not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")
    
    try:
        lower_price = float(lower_price)
        upper_price = float(upper_price)
        grid_levels = int(grid_levels)
    except ValueError:
        raise ValueError("lower_price, upper_price, and grid_levels must be numbers")
    
    if lower_price <= 0 or upper_price <= 0:
        raise ValueError("Prices must be positive")
    
    if lower_price >= upper_price:
        raise ValueError("lower_price must be less than upper_price")
    
    if grid_levels < 2:
        raise ValueError("grid_levels must be at least 2")
    
    # Calculate quantity per level
    qty_per_level = total_quantity / grid_levels
    
    # Generate grid prices
    price_step = (upper_price - lower_price) / (grid_levels - 1)
    grid_prices = [lower_price + i * price_step for i in range(grid_levels)]
    
    if dry_run:
        logger.info(
            f"[DRY-RUN] Would place {grid_levels}-level grid {side_up} strategy "
            f"for {symbol}: ${lower_price:.2f} - ${upper_price:.2f}"
        )
        print(f"✅ [DRY-RUN] Grid strategy validated: {side_up} {symbol}")
        print(f"   Levels: {grid_levels}, Qty/level: {qty_per_level:.8f}")
        for i, price in enumerate(grid_prices, 1):
            print(f"   Level {i}: ${price:.2f}")
        return
    
    client = get_client()
    order_ids = []
    
    try:
        logger.info(
            f"Placing {grid_levels}-level grid {side_up} strategy for {symbol}"
        )
        
        # For BUY grid: place buy orders at lower prices, sell orders at higher prices
        # For SELL grid: place sell orders at lower prices, buy orders at higher prices
        
        for i, price in enumerate(grid_prices, 1):
            # Lower half: place buy orders (if side=BUY) or sell orders (if side=SELL)
            if i <= grid_levels // 2:
                order_side = "BUY" if side_up == "BUY" else "SELL"
            else:
                order_side = "SELL" if side_up == "BUY" else "BUY"
            
            order = client.futures_create_order(
                symbol=symbol,
                side=order_side,
                type="LIMIT",
                timeInForce="GTC",
                quantity=qty_per_level,
                price=str(price)
            )
            order_ids.append(order['orderId'])
            logger.info(f"Grid level {i} ({order_side} @ ${price:.2f}): Order {order['orderId']}")
            
            # Small delay to avoid rate limits
            if i < grid_levels:
                time.sleep(0.1)
        
        print(f"✅ Grid strategy ({grid_levels} levels) placed for {symbol}.")
        print(f"   Order IDs: {order_ids}")
    
    except BinanceAPIException as e:
        logger.error(f"Binance API error (grid): {e}")
        print("❌ Binance API error:", e)
    
    except Exception as e:
        logger.error(f"General error (grid): {e}")
        print("❌ Error:", e)


def main():
    parser = argparse.ArgumentParser(description="Binance Futures Grid Trading CLI Bot")
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("quantity", nargs="?", help="Total order quantity")
    parser.add_argument("lower_price", nargs="?", help="Grid lower bound price")
    parser.add_argument("upper_price", nargs="?", help="Grid upper bound price")
    
    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Total quantity")
    parser.add_argument("--lower", dest="lower_flag", help="Grid lower price")
    parser.add_argument("--upper", dest="upper_flag", help="Grid upper price")
    parser.add_argument("--levels", type=int, default=5, help="Number of grid levels (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without placing")
    
    args = parser.parse_args()
    
    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.quantity
    lower_price = args.lower_flag or args.lower_price
    upper_price = args.upper_flag or args.upper_price
    
    if not all([symbol, side, quantity, lower_price, upper_price]):
        parser.error("Symbol, side, quantity, lower_price, and upper_price are required.")
    
    place_grid_orders(
        symbol, side, quantity, lower_price, upper_price,
        grid_levels=args.levels, dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
