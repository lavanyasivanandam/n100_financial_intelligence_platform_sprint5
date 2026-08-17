from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

# Ensure the project root is importable when Streamlit executes this file
# directly (Streamlit does not treat src/dashboard/app.py as a package module).
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard import screens

st.set_page_config(page_title='Nifty 100 Insights',page_icon='📊',layout='wide',initial_sidebar_state='expanded')
st.set_option('client.showSidebarNavigation', False)

PAGES={
 '01 — Home':screens.home,
 '02 — Company Profile':screens.profile,
 '03 — Screener':screens.screener,
 '04 — Peers':screens.peers,
 '05 — Trends':screens.trends,
 '06 — Sectors':screens.sectors,
 '07 — Capital Allocation':screens.capital_allocation,
 '08 — Reports & Valuation':screens.reports,
}
# Valuation is embedded as a tab in screen 08, keeping the dashboard at exactly 8 screens.
choice=st.sidebar.radio('Navigate',list(PAGES),index=0)
PAGES[choice]()
