import argparse
import time
import sys
import os

# Make sure we can import utils from ../
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger


def run_twap(symbol: str, side: str, total_quantity, parts, delay_seconds):
    client = get_client()

    symbol, total_quantity, _ = validate_inputs(symbol, total_quantity)
    parts = int(parts)
    delay_seconds = float(delay_seconds)

    if parts <= 0:
        raise ValueError("parts must be positive")

    qty_per_order = total_quantity / parts

    side_up = side.upper()
    if side_up == "BUY":
        side_enum = SIDE_BUY
    elif side_up == "SELL":
        side_enum = SIDE_SELL
    else:
        raise ValueError("side must be BUY or SELL")

    print(
        f"Running TWAP: {total_quantity} {symbol} in {parts} parts, "
        f"~{qty_per_order:.8f} per order, every {delay_seconds}s"
    )

    for i in range(parts):
        try:
            logger.info(
                f"TWAP chunk {i+1}/{parts}: SPOT MARKET {side_up} "
                f"{qty_per_order} {symbol}"
            )

            order = client.create_order(
                symbol=symbol,
                side=side_enum,
                type=ORDER_TYPE_MARKET,
                quantity=qty_per_order
            )

            logger.info(f"TWAP order response (chunk {i+1}): {order}")
            print(f"✅ Chunk {i+1}/{parts} placed (or attempted).")
            print(order)

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
    parser = argparse.ArgumentParser(description="Binance SPOT TWAP Order CLI")
    parser.add_argument("symbol", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", help="BUY or SELL")
    parser.add_argument("total_quantity", help="Total quantity, e.g., 0.01")
    parser.add_argument("parts", help="Number of chunks, e.g., 5")
    parser.add_argument("delay_seconds", help="Delay between chunks, e.g., 10")

    args = parser.parse_args()

    run_twap(
        symbol=args.symbol,
        side=args.side,
        total_quantity=args.total_quantity,
        parts=args.parts,
        delay_seconds=args.delay_seconds,
    )


if __name__ == "__main__":
    main()
