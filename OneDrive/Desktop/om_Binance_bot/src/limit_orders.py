import argparse

from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger


def place_limit_order(symbol: str, side: str, quantity, price, dry_run: bool = False):
    symbol, quantity, price = validate_inputs(symbol, quantity, price)

    side_up = side.upper()
    if side_up not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")

    if dry_run:
        logger.info(f"[DRY-RUN] Would place Futures LIMIT {side_up} {quantity} {symbol} @ {price}")
        print(f"[DRY-RUN] Futures Limit order validated: {side_up} {quantity} {symbol} @ {price}")
        return

    client = get_client()
    try:
        logger.info(f"Placing Futures LIMIT {side_up} {quantity} {symbol} @ {price}")

        order = client.futures_create_order(
            symbol=symbol,
            side=side_up,
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=str(price)
        )

        logger.info(f"Limit order response: {order}")
        print("[OK] Futures Limit order placed (or attempted).")
        print(order)

    except BinanceAPIException as e:
        logger.error(f"Binance API error (limit): {e}")
        print("[ERROR] Binance API error:", e)

    except Exception as e:
        logger.error(f"General error (limit): {e}")
        print("[ERROR] Error:", e)


def main():
    parser = argparse.ArgumentParser(description="Binance Futures Limit Order CLI Bot")
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("quantity", nargs="?", help="Order quantity, e.g., 0.001")
    parser.add_argument("price", nargs="?", help="Limit price, e.g., 50000")

    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Order quantity")
    parser.add_argument("-p", "--price", dest="price_flag", help="Limit price")
    parser.add_argument("--dry-run", action="store_true", help="Validate without placing order")

    args = parser.parse_args()

    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.quantity
    price = args.price_flag or args.price

    if not all([symbol, side, quantity, price]):
        parser.error("Symbol, side, quantity, and price are required.")

    place_limit_order(symbol, side, quantity, price, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
