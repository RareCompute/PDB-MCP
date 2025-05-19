# mcp_pdb/config.py
import os
from enum import Enum

# --- Core API Settings ---
PDB_API_BASE_URL: str = "https://data.rcsb.org"  # Official RCSB Data API

# --- Logging Configuration ---
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

LOG_LEVEL: LogLevel = LogLevel(os.getenv("LOG_LEVEL", "INFO").upper())

# --- Cache Settings (Optional - for future use) ---
CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "False").lower() == "true"
CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000")) # Max items in cache
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600")) # Time-to-live for cache entries

# --- Application Metadata (Optional - for __version__) ---
APP_VERSION: str = "0.1.0-alpha"

if __name__ == "__main__":
    # Example of how to access settings
    print(f"PDB API Base URL: {PDB_API_BASE_URL}")
    print(f"Default Log Level: {LOG_LEVEL.value}")
    print(f"Cache Enabled: {CACHE_ENABLED}")
    print(f"Cache Max Size: {CACHE_MAX_SIZE}")
    print(f"Cache TTL (seconds): {CACHE_TTL_SECONDS}")
    print(f"App Version: {APP_VERSION}")
