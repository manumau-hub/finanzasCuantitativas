#!/usr/bin/env python3
"""
Envía una orden de prueba.

Uso:
    python place_order.py --symbol AAPL --qty 10 --side buy --type market
    python place_order.py --symbol AAPL --qty 10 --side buy --type limit --limit-price 150.00
    python place_order.py --symbol AAPL --qty 10 --side sell --type stop --stop-price 140.00
"""

import argparse
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def main():
    parser = argparse.ArgumentParser(description="Envía una orden a Alpaca")
    parser.add_argument("--symbol", required=True, help="Símbolo (ej: AAPL)")
    parser.add_argument("--qty", required=True, type=float, help="Cantidad")
    parser.add_argument("--side", required=True, choices=["buy", "sell"], help="Buy o Sell")
    parser.add_argument("--type", required=True, choices=["market", "limit", "stop", "stop_limit"],
                        help="Tipo de orden")
    parser.add_argument("--limit-price", type=float, help="Precio límite (para limit orders)")
    parser.add_argument("--stop-price", type=float, help="Precio stop (para stop orders)")
    parser.add_argument("--tif", default="day", choices=["day", "gtc", "opg", "cls", "ioc", "fok"],
                        help="Time in Force (default: day)")
    args = parser.parse_args()
    
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Error: Se requieren APCA_API_KEY_ID y APCA_API_SECRET_KEY")
        return
    
    client = TradingClient(api_key, secret_key, paper=True)
    
    # Mapear time in force
    tif_map = {
        "day": TimeInForce.DAY,
        "gtc": TimeInForce.GTC,
        "opg": TimeInForce.OPG,
        "cls": TimeInForce.CLS,
        "ioc": TimeInForce.IOC,
        "fok": TimeInForce.FOK,
    }
    time_in_force = tif_map[args.tif]
    
    # Crear orden según tipo
    try:
        if args.type == "market":
            order_request = MarketOrderRequest(
                symbol=args.symbol,
                qty=args.qty,
                side=OrderSide.BUY if args.side == "buy" else OrderSide.SELL,
                time_in_force=time_in_force
            )
        elif args.type == "limit":
            if not args.limit_price:
                print("❌ Error: --limit-price requerido para órdenes limit")
                return
            order_request = LimitOrderRequest(
                symbol=args.symbol,
                qty=args.qty,
                side=OrderSide.BUY if args.side == "buy" else OrderSide.SELL,
                limit_price=args.limit_price,
                time_in_force=time_in_force
            )
        elif args.type == "stop":
            if not args.stop_price:
                print("❌ Error: --stop-price requerido para órdenes stop")
                return
            order_request = StopOrderRequest(
                symbol=args.symbol,
                qty=args.qty,
                side=OrderSide.BUY if args.side == "buy" else OrderSide.SELL,
                stop_price=args.stop_price,
                time_in_force=time_in_force
            )
        elif args.type == "stop_limit":
            if not args.limit_price or not args.stop_price:
                print("❌ Error: --limit-price y --stop-price requeridos")
                return
            order_request = StopLimitOrderRequest(
                symbol=args.symbol,
                qty=args.qty,
                side=OrderSide.BUY if args.side == "buy" else OrderSide.SELL,
                stop_price=args.stop_price,
                limit_price=args.limit_price,
                time_in_force=time_in_force
            )
        
        print(f"\nEnviando orden...")
        print(f"  Symbol: {args.symbol}")
        print(f"  Qty: {args.qty}")
        print(f"  Side: {args.side}")
        print(f"  Type: {args.type}")
        if args.limit_price:
            print(f"  Limit Price: ${args.limit_price}")
        if args.stop_price:
            print(f"  Stop Price: ${args.stop_price}")
        print(f"  TIF: {args.tif}")
        print()
        
        order = client.submit_order(order_request)
        
        print(f"✅ Orden enviada exitosamente!")
        print(f"  Order ID: {order.id}")
        print(f"  Status: {order.status}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Qty: {order.qty}")
        
    except Exception as e:
        print(f"❌ Error al enviar orden: {e}")

if __name__ == "__main__":
    main()
