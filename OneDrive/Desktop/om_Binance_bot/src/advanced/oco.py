"""
OCO (One-Cancels-the-Other) Orders for Binance Futures.
Simultaneously place a take-profit limit order and a stop-loss limit order.
If one fills, the other is automatically cancelled.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger


def place_oco_order(
    symbol: str,
    side: str,
    quantity,
    tp_price: float,
    sl_price: float,
    dry_run: bool = False
):
    """
    Place an OCO order on Binance Futures.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        side: BUY or SELL
        quantity: Order quantity
        tp_price: Take-profit price (opposite side limit)
        sl_price: Stop-loss price (opposite side market)
        dry_run: If True, only validate without placing
    """
    symbol, quantity, _ = validate_inputs(symbol, quantity)
    
    side_up = side.upper()
    if side_up not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")
    
    # For BUY order: TP is SELL limit, SL is SELL market (stop-loss)
    # For SELL order: TP is BUY limit, SL is BUY market (stop-loss)
    opposite_side = "SELL" if side_up == "BUY" else "BUY"
    
    # Validate prices
    try:
        tp_price = float(tp_price)
        sl_price = float(sl_price)
    except ValueError:
        raise ValueError("tp_price and sl_price must be numbers")
    
    if tp_price <= 0 or sl_price <= 0:
        raise ValueError("Prices must be positive")
    
    if dry_run:
        logger.info(
            f"[DRY-RUN] Would place OCO {side_up} {quantity} {symbol}: "
            f"TP={tp_price}, SL={sl_price}"
        )
        print(
            f"✅ [DRY-RUN] OCO order validated: {side_up} {quantity} {symbol} "
            f"with TP={tp_price}, SL={sl_price}"
        )
        return
    
    client = get_client()
    try:
        logger.info(
            f"Placing OCO {side_up} {quantity} {symbol}: TP={tp_price}, SL={sl_price}"
        )
        
        # Place entry order (BUY or SELL at market)
        entry_order = client.futures_create_order(
            symbol=symbol,
            side=side_up,
            type="MARKET",
            quantity=quantity
        )
        logger.info(f"Entry order placed: {entry_order}")
        
        # Place take-profit (limit order at TP price)
        tp_order = client.futures_create_order(
            symbol=symbol,
            side=opposite_side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=str(tp_price)
        )
        logger.info(f"Take-profit order placed: {tp_order}")
        
        # Place stop-loss (stop-market order at SL price)
        sl_order = client.futures_create_order(
            symbol=symbol,
            side=opposite_side,
            type="STOP_MARKET",
            stopPrice=str(sl_price),
            quantity=quantity
        )
        logger.info(f"Stop-loss order placed: {sl_order}")
        
        print("✅ OCO orders placed (entry + TP + SL).")
        print(f"Entry: {entry_order['orderId']}")
        print(f"Take-Profit: {tp_order['orderId']}")
        print(f"Stop-Loss: {sl_order['orderId']}")
    
    except BinanceAPIException as e:
        logger.error(f"Binance API error (OCO): {e}")
        print("❌ Binance API error:", e)
    
    except Exception as e:
        logger.error(f"General error (OCO): {e}")
        print("❌ Error:", e)


def main():
    parser = argparse.ArgumentParser(description="Binance Futures OCO Order CLI Bot")
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("quantity", nargs="?", help="Order quantity, e.g., 0.001")
    parser.add_argument("tp_price", nargs="?", help="Take-profit price")
    parser.add_argument("sl_price", nargs="?", help="Stop-loss price")
    
    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Order quantity")
    parser.add_argument("--tp", dest="tp_flag", help="Take-profit price")
    parser.add_argument("--sl", dest="sl_flag", help="Stop-loss price")
    parser.add_argument("--dry-run", action="store_true", help="Validate without placing")
    
    args = parser.parse_args()
    
    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.quantity
    tp_price = args.tp_flag or args.tp_price
    sl_price = args.sl_flag or args.sl_price
    
    if not all([symbol, side, quantity, tp_price, sl_price]):
        parser.error("Symbol, side, quantity, tp_price, and sl_price are required.")
    
    place_oco_order(symbol, side, quantity, tp_price, sl_price, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
