"""
TWAP (Time-Weighted Average Price) strategy for Binance Futures.
Split a large order into smaller chunks over time.
"""

import argparse
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger


def run_twap(
    symbol: str,
    side: str,
    total_quantity,
    parts: int = 5,
    delay_seconds: float = 10.0,
    dry_run: bool = False
):
    """
    TWAP (Time-Weighted Average Price) strategy.
    Split a large order into smaller chunks over time.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        side: BUY or SELL
        total_quantity: Total quantity to execute
        parts: Number of chunks (default: 5)
        delay_seconds: Delay between chunks in seconds (default: 10)
        dry_run: If True, only validate without placing
    """
    symbol, total_quantity, _ = validate_inputs(symbol, total_quantity)
    
    try:
        parts = int(parts)
        delay_seconds = float(delay_seconds)
    except ValueError:
        raise ValueError("parts must be an integer, delay_seconds must be a number")

    if parts <= 0:
        raise ValueError("parts must be positive")
    
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be non-negative")

    qty_per_order = total_quantity / parts

    side_up = side.upper()
    if side_up not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")

    if dry_run:
        logger.info(
            f"[DRY-RUN] TWAP: {total_quantity} {symbol} in {parts} parts, "
            f"~{qty_per_order:.8f} per order, every {delay_seconds}s"
        )
        print(
            f"✅ [DRY-RUN] TWAP strategy validated: {side_up} {total_quantity} {symbol}"
        )
        print(f"   Chunks: {parts}, Qty/chunk: {qty_per_order:.8f}, Interval: {delay_seconds}s")
        return

    client = get_client()
    print(
        f"Running TWAP: {total_quantity} {symbol} in {parts} parts, "
        f"~{qty_per_order:.8f} per order, every {delay_seconds}s"
    )

    for i in range(parts):
        try:
            logger.info(
                f"TWAP chunk {i+1}/{parts}: Futures MARKET {side_up} "
                f"{qty_per_order} {symbol}"
            )

            order = client.futures_create_order(
                symbol=symbol,
                side=side_up,
                type="MARKET",
                quantity=qty_per_order
            )

            logger.info(f"TWAP order response (chunk {i+1}): {order}")
            print(f"✅ Chunk {i+1}/{parts} placed (or attempted).")
            print(f"   Order ID: {order.get('orderId', 'N/A')}")

        except BinanceAPIException as e:
            logger.error(f"Binance API error (TWAP, chunk {i+1}): {e}")
            print("❌ Binance API error during TWAP:", e)
            break

        except Exception as e:
            logger.error(f"General error (TWAP, chunk {i+1}): {e}")
            print("❌ Error during TWAP:", e)
            break

        if i != parts - 1:
            time.sleep(delay_seconds)


def main():
    parser = argparse.ArgumentParser(description="Binance Futures TWAP Order CLI")
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("total_quantity", nargs="?", help="Total quantity, e.g., 0.01")
    parser.add_argument("parts", nargs="?", help="Number of chunks, e.g., 5")
    parser.add_argument("delay_seconds", nargs="?", help="Delay between chunks (sec)")
    
    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Total quantity")
    parser.add_argument("--parts", type=int, dest="parts_flag", help="Number of chunks")
    parser.add_argument("--delay", type=float, dest="delay_flag", help="Delay (seconds)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without placing")

    args = parser.parse_args()

    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.total_quantity
    parts = args.parts_flag or (int(args.parts) if args.parts else 5)
    delay = args.delay_flag or (float(args.delay_seconds) if args.delay_seconds else 10.0)

    if not all([symbol, side, quantity]):
        parser.error("Symbol, side, and total_quantity are required.")

    run_twap(symbol, side, quantity, parts=parts, delay_seconds=delay, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
