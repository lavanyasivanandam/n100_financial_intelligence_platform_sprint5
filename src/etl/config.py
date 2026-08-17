
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT/"data/raw"
SUPPORTING = ROOT/"data/supporting"
DB_PATH = ROOT/os.environ.get("DB_PATH","db/nifty100.db")
OUTPUT = ROOT/"output"
REPORTS = ROOT/"reports"
DB_PATH.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)
CORE_FILES = ["companies.xlsx","profitandloss.xlsx","balancesheet.xlsx","cashflow.xlsx","analysis.xlsx","documents.xlsx","prosandcons.xlsx"]
SUPPORT_FILES = ["sectors.xlsx","stock_prices.xlsx","market_cap.xlsx","financial_ratios.xlsx","peer_groups.xlsx"]
