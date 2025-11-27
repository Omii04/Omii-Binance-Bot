import os
import time
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from binance.client import Client

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
ENV_PATH = BASE_DIR / ".env"
LOG_FILE_PATH = BASE_DIR / "bot.log"

# Load environment variables from .env
load_dotenv(ENV_PATH)

# ---------- Logging ----------
logging.basicConfig(
    filename=str(LOG_FILE_PATH),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ---------- Input Validation ----------
def validate_inputs(symbol: str, quantity, price: Optional[float] = None):
    if not isinstance(symbol, str) or len(symbol) < 3:
        raise ValueError("Invalid symbol")

    try:
        quantity = float(quantity)
    except ValueError:
        raise ValueError("Quantity must be a number")

    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    if price is not None:
        try:
            price = float(price)
        except ValueError:
            raise ValueError("Price must be a number")

        if price <= 0:
            raise ValueError("Price must be positive")

    return symbol.upper(), quantity, price


# ---------- Binance Client (SPOT) ----------
def get_client() -> Client:
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        raise RuntimeError("API_KEY or API_SECRET not set in .env")

    client = Client(api_key, api_secret)

    # Sync timestamp with Binance server to avoid -1021 errors
    try:
        server_time = client.get_server_time()
        server_ts = server_time["serverTime"]        # ms
        local_ts = int(time.time() * 1000)           # ms
        client._timestamp_offset = server_ts - local_ts
    except Exception as e:
        logger.warning(f"Failed to sync server time: {e}")

    return client
