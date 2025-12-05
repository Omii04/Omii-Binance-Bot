# Omii Binance Futures Bot

A professional CLI-based trading bot for **Binance USDT-M Futures** supporting multiple order types with robust logging, validation, and comprehensive error handling.

## Features

### Core Orders (Mandatory)
- **Market Orders**: Instantly buy/sell at current market price
- **Limit Orders**: Buy/sell at a specified price when available

### Advanced Orders (Bonus)
- **Stop-Limit Orders**: Trigger limit orders when price reaches stop price
- **OCO (One-Cancels-the-Other)**: Simultaneously place take-profit and stop-loss orders
- **TWAP (Time-Weighted Average Price)**: Split large orders into smaller chunks over time
- **Grid Orders**: Automated buy-low/sell-high strategy within a price range

## API Setup

### Prerequisites
- Python 3.7+
- Binance account with API keys enabled
- `python-dotenv` and `binance-connector` packages

### Create `.env` File

Create a `.env` file in the project root:

```
API_KEY=your_binance_api_key_here
API_SECRET=your_binance_api_secret_here
```

**Security Note:** Never commit `.env` to version control.

### Install Dependencies

```bash
pip install python-dotenv binance-connector
```

## Project Structure

```
om_Binance_bot/
├── src/
│   ├── helpers.py              # Shared utilities (validation, client, logging)
│   ├── market_orders.py        # Market order implementation
│   ├── limit_orders.py         # Limit order implementation
│   ├── utils/
│   │   └── __init__.py         # Re-exports from helpers
│   └── advanced/
│       ├── stop_limit.py       # Stop-Limit orders
│       ├── twap.py             # TWAP strategy
│       ├── oco.py              # OCO orders
│       └── grid.py             # Grid trading
├── .env                         # API credentials (not in repo)
├── bot.log                      # Execution logs
└── README.md                    # This file
```

## How to Run the Bot

### Market Orders

**Using flags (recommended):**
```bash
cd src
python market_orders.py -s BTCUSDT -S BUY -q 0.001
```

**Using positional arguments:**
```bash
cd src
python market_orders.py BTCUSDT BUY 0.001
```

**Dry-run (validate without placing):**
```bash
python market_orders.py -s BTCUSDT -S BUY -q 0.001 --dry-run
```

### Limit Orders

```bash
cd src
python limit_orders.py -s BTCUSDT -S BUY -q 0.001 -p 50000
```

### Stop-Limit Orders

```bash
cd src
python advanced/stop_limit.py -s BTCUSDT -S SELL -q 0.001 --stop 60000 --limit 59900
```

**Parameters:**
- `--stop`: Price at which the order is triggered
- `--limit`: Price at which the order executes

### OCO (One-Cancels-the-Other) Orders

```bash
cd src
python advanced/oco.py -s BTCUSDT -S BUY -q 0.001 --tp 51000 --sl 49000
```

**Parameters:**
- `--tp`: Take-profit price (sell at this level if BUY)
- `--sl`: Stop-loss price (sell at this level if BUY)

### TWAP (Time-Weighted Average Price)

```bash
cd src
python advanced/twap.py -s BTCUSDT -S BUY -q 0.01 --parts 5 --delay 10
```

**Parameters:**
- `--parts`: Number of chunks to split the order (default: 5)
- `--delay`: Seconds between chunks (default: 10)

### Grid Orders

```bash
cd src
python advanced/grid.py -s BTCUSDT -S BUY -q 0.01 --lower 49000 --upper 51000 --levels 5
```

**Parameters:**
- `--lower`: Lower bound of grid range
- `--upper`: Upper bound of grid range
- `--levels`: Number of grid levels (default: 5)

## Common Arguments

All scripts support:
- `-s, --symbol`: Trading pair (e.g., BTCUSDT)
- `-S, --side`: BUY or SELL
- `-q, --quantity`: Order quantity
- `--dry-run`: Validate inputs without calling Binance API

## Logging

All actions are logged to `bot.log` in the project root with timestamps and severity levels:

```
2024-12-05 10:30:45,123 - INFO - Placing Futures MARKET BUY 0.001 BTCUSDT
2024-12-05 10:30:46,456 - INFO - Market order response: {'orderId': 123456789, ...}
2024-12-05 10:30:50,789 - ERROR - Binance API error: Account has insufficient balance for requested action.
```

## Safety Recommendations

1. **Use `--dry-run`** to validate orders before execution:
   ```bash
   python market_orders.py -s BTCUSDT -S BUY -q 0.001 --dry-run
   ```

2. **Start with small quantities** (e.g., 0.001 BTC) to test connectivity

3. **Check `bot.log`** after each run for details and errors

4. **Fund testnet account** or use testnet API keys for learning

5. **Monitor Binance account** during automated trades

## Validation

All inputs are validated before API calls:
- **Symbol**: Must be >= 3 characters
- **Quantity**: Must be positive number
- **Price**: Must be positive number (for limit orders)

## Error Handling

Common errors and solutions:

| Error | Solution |
|-------|----------|
| `APIError(code=-2010)` (insufficient balance) | Fund account or reduce quantity |
| `ModuleNotFoundError: binance` | Run `pip install binance-connector` |
| `RuntimeError: API_KEY or API_SECRET not set` | Create `.env` with credentials |

## Next Steps / Improvements

- Add Binance testnet mode (`--testnet` flag)
- WebSocket-based price monitoring for stop-limit
- Trade history and profitability analysis
- Discord/Telegram notifications on order fills
- Position sizing based on risk percentage

## Disclaimer

**This bot is for educational purposes.** Use at your own risk. Always test with small amounts or testnet before live trading. The authors are not responsible for any losses incurred.

## License

MIT License

