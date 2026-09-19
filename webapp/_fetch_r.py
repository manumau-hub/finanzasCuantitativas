"""Script auxiliar para obtener r (^IRX) via subprocess."""
import sys
from pathlib import Path

root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, root)
from Codigo.data.market_data import get_risk_free_rate_with_source

v, s = get_risk_free_rate_with_source()
print(f"{v}|{s}")
