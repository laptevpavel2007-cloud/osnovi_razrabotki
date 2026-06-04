import sys
import os

DB_PATH = os.environ.get('DB_PATH', 'store.db')
DATA_DIR = os.environ.get('DATA_DIR', 'data')
DEFAULT_CASHIER_ID = int(os.environ.get('CASHIER_ID', '1'))

WINDOW_TITLE = "Магазин техники"
WINDOW_GEOMETRY = "970x400"
BG_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#2c6e9e"
TEXT_COLOR = "#333333"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"