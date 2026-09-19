#!/usr/bin/env python3
"""
Verifica el estado de la cuenta de Alpaca.

Uso:
    python check_account.py
"""

import os
from alpaca.trading.client import TradingClient

def main():
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Error: Se requieren APCA_API_KEY_ID y APCA_API_SECRET_KEY")
        return
    
    # Paper trading
    client = TradingClient(api_key, secret_key, paper=True)
    
    print("=== ALPACA ACCOUNT ===\n")
    
    # Account info
    account = client.get_account()
    
    print(f"Account ID: {account.id}")
    print(f"Status: {account.status}")
    print(f"Currency: {account.currency}")
    print()
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Day Trade Count: {account.day_trade_count}")
    print()
    print(f"Pattern Day Trader: {account.pattern_day_trader}")
    print(f"Shorting Enabled: {account.shorting_enabled}")
    print()
    
    # Clock
    clock = client.get_clock()
    print(f"Market Open: {clock.is_open}")
    print(f"Next Open: {clock.next_open}")
    print(f"Next Close: {clock.next_close}")
    print()
    
    # Positions
    positions = client.get_all_positions()
    print(f"Posiciones abiertas: {len(positions)}")
    
    if positions:
        print("\n--- POSICIONES ---")
        for pos in positions:
            pl_pct = (float(pos.unrealized_pl) / float(pos.cost_basis)) * 100 if float(pos.cost_basis) else 0
            print(f"\n{pos.symbol}:")
            print(f"  Cantidad: {pos.qty}")
            print(f"  Entry: ${float(pos.avg_entry_price):.2f}")
            print(f"  Current: ${float(pos.current_price):.2f}")
            print(f"  P/L: ${float(pos.unrealized_pl):.2f} ({pl_pct:.2f}%)")
    
    # Orders abiertos
    orders = client.get_orders(status="open")
    print(f"\nÓrdenes abiertas: {len(orders)}")
    
    if orders:
        print("\n--- ÓRDENES ABIERTAS ---")
        for order in orders:
            print(f"\n{order.symbol}: {order.side} {order.qty} @ ${order.limit_price or 'MARKET'}")
            print(f"  Status: {order.status}")
            print(f"  Filled: {order.filled_qty}/{order.qty}")

if __name__ == "__main__":
    main()
