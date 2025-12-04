# Omii Binance Bot

This repository provides small command-line utilities to place Binance SPOT orders (market and limit) and some advanced order strategies.

**Important:** These scripts can place real orders on Binance. Use testnet or a `--dry-run` flag (if added) during testing.

**API Setup**
- **Create a `.env` file** in the project root with your Binance API credentials:

```
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

- The project reads `.env` automatically (via `python-dotenv`) and logs to `bot.log` in the project root.

**How to run the bot**
- Using positional arguments (existing behavior):

```
cd src
python market_orders.py BTCUSDT BUY 0.01
```

- Using flags (supported now):

```
cd src
python market_orders.py -s BTCUSDT -S BUY -q 0.01
```

- Notes:
  - `symbol` is the trading pair (e.g., `BTCUSDT`).
  - `side` must be `BUY` or `SELL`.
  - `quantity` is the base asset amount (e.g., `0.01`).

**Safety recommendations**
- Fund a testnet account or reduce `quantity` when testing.
- Check `bot.log` after running for details and errors.

**Next improvements you may want**
- Add `--dry-run` to validate inputs without calling Binance API.
- Add explicit `--testnet` mode using Binance testnet endpoints.

If you want, I can add `--dry-run` and `--testnet` support now and update examples.
