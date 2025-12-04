import argparse

from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger



def place_market_order(symbol: str, side: str, quantity):
    client = get_client()

    symbol, quantity, _ = validate_inputs(symbol, quantity)

    side_up = side.upper()
    if side_up == "BUY":
        side_enum = SIDE_BUY
    elif side_up == "SELL":
        side_enum = SIDE_SELL
    else:
        raise ValueError("side must be BUY or SELL")

    try:
        logger.info(f"Placing SPOT MARKET {side_up} {quantity} {symbol}")

        order = client.create_order(
            symbol=symbol,
            side=side_enum,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        logger.info(f"Market order response: {order}")
        print("✅ SPOT Market order placed (or attempted).")
        print(order)

    except BinanceAPIException as e:
        logger.error(f"Binance API error (market): {e}")
        print("❌ Binance API error:", e)

    except Exception as e:
        logger.error(f"General error (market): {e}")
        print("❌ Error:", e)


def main():
    parser = argparse.ArgumentParser(description="Binance SPOT Market Order CLI Bot")
    # Positional (kept for backwards compatibility) — make them optional
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("quantity", nargs="?", help="Order quantity, e.g., 0.001")

    # Optional flags (preferred by some users)
    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Order quantity, e.g., 0.001")

    args = parser.parse_args()

    # Prefer flags if provided, otherwise fall back to positional args
    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.quantity

    if not (symbol and side and quantity):
        parser.error("Symbol, side and quantity are required (provide as positional args or with -s/-S/-q flags).")

    place_market_order(symbol, side, quantity)


if __name__ == "__main__":
    main()
