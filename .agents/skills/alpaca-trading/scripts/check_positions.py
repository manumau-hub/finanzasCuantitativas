#!/usr/bin/env python3
"""
Lista todas las posiciones abiertas.

Uso:
    python check_positions.py
"""

import os
from alpaca.trading.client import TradingClient

def main():
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Error: Se requieren APCA_API_KEY_ID y APCA_API_SECRET_KEY")
        return
    
    client = TradingClient(api_key, secret_key, paper=True)
    
    positions = client.get_all_positions()
    
    if not positions:
        print("No hay posiciones abiertas")
        return
    
    print(f"{'Symbol':<10} {'Qty':<8} {'Entry':<12} {'Current':<12} {'P/L $':<12} {'P/L %':<10}")
    print("-" * 70)
    
    total_pl = 0
    total_value = 0
    
    for pos in positions:
        entry = float(pos.avg_entry_price)
        current = float(pos.current_price)
        pl = float(pos.unrealized_pl)
        pl_pct = (pl / float(pos.cost_basis)) * 100 if float(pos.cost_basis) else 0
        value = float(pos.market_value)
        
        total_pl += pl
        total_value += value
        
        print(f"{pos.symbol:<10} {pos.qty:<8} ${entry:<11.2f} ${current:<11.2f} ${pl:>10.2f} {pl_pct:>9.2f}%")
    
    print("-" * 70)
    print(f"{'TOTAL':<10} {'':<8} {'':<12} {'':<12} ${total_pl:>10.2f}")
    print(f"\nValor total del portfolio: ${total_value:,.2f}")

if __name__ == "__main__":
    main()
