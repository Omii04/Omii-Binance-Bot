import argparse

from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC
from binance.exceptions import BinanceAPIException

from helpers import validate_inputs, get_client, logger


def place_limit_order(symbol: str, side: str, quantity, price):
    client = get_client()

    symbol, quantity, price = validate_inputs(symbol, quantity, price)

    side_up = side.upper()
    if side_up == "BUY":
        side_enum = SIDE_BUY
    elif side_up == "SELL":
        side_enum = SIDE_SELL
    else:
        raise ValueError("side must be BUY or SELL")

    try:
        logger.info(f"Placing SPOT LIMIT {side_up} {quantity} {symbol} @ {price}")

        order = client.create_order(
            symbol=symbol,
            side=side_enum,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=str(price)
        )

        logger.info(f"Limit order response: {order}")
        print("✅ SPOT Limit order placed (or attempted).")
        print(order)

    except BinanceAPIException as e:
        logger.error(f"Binance API error (limit): {e}")
        print("❌ Binance API error:", e)

    except Exception as e:
        logger.error(f"General error (limit): {e}")
        print("❌ Error:", e)


def main():
    parser = argparse.ArgumentParser(description="Binance SPOT Limit Order CLI Bot")
    parser.add_argument("symbol", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", help="BUY or SELL")
    parser.add_argument("quantity", help="Order quantity, e.g., 0.001")
    parser.add_argument("price", help="Limit price, e.g., 50000")

    args = parser.parse_args()

    place_limit_order(
        symbol=args.symbol,
        side=args.side,
        quantity=args.quantity,
        price=args.price,
    )


if __name__ == "__main__":
    main()
