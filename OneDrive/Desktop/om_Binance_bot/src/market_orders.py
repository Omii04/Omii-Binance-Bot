import argparse

from binance.exceptions import BinanceAPIException

from utils import validate_inputs, get_client, logger



def place_market_order(symbol: str, side: str, quantity, dry_run: bool = False):
    symbol, quantity, _ = validate_inputs(symbol, quantity)

    side_up = side.upper()
    if side_up not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")

    if dry_run:
        logger.info(f"[DRY-RUN] Would place Futures MARKET {side_up} {quantity} {symbol}")
        print(f"[DRY-RUN] Futures Market order validated: {side_up} {quantity} {symbol}")
        return

    client = get_client()
    try:
        logger.info(f"Placing Futures MARKET {side_up} {quantity} {symbol}")

        order = client.futures_create_order(
            symbol=symbol,
            side=side_up,
            type="MARKET",
            quantity=quantity
        )

        logger.info(f"Market order response: {order}")
        print("[OK] Futures Market order placed (or attempted).")
        print(order)

    except BinanceAPIException as e:
        logger.error(f"Binance API error (market): {e}")
        print("[ERROR] Binance API error:", e)

    except Exception as e:
        logger.error(f"General error (market): {e}")
        print("[ERROR] Error:", e)



def main():
    parser = argparse.ArgumentParser(description="Binance Futures Market Order CLI Bot")
    # Positional (kept for backwards compatibility) — make them optional
    parser.add_argument("symbol", nargs="?", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("side", nargs="?", help="BUY or SELL")
    parser.add_argument("quantity", nargs="?", help="Order quantity, e.g., 0.001")

    # Optional flags (preferred by some users)
    parser.add_argument("-s", "--symbol", dest="symbol_flag", help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("-S", "--side", dest="side_flag", help="BUY or SELL")
    parser.add_argument("-q", "--quantity", dest="quantity_flag", help="Order quantity, e.g., 0.001")
    parser.add_argument("--dry-run", action="store_true", help="Validate without placing order")

    args = parser.parse_args()

    # Prefer flags if provided, otherwise fall back to positional args
    symbol = args.symbol_flag or args.symbol
    side = args.side_flag or args.side
    quantity = args.quantity_flag or args.quantity

    if not (symbol and side and quantity):
        parser.error("Symbol, side and quantity are required (provide as positional args or with -s/-S/-q flags).")

    place_market_order(symbol, side, quantity, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
