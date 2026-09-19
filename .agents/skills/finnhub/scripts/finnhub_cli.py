"""
Finnhub CLI — Interfaz de linea de comandos para consultas rapidas a Finnhub.

Uso:
    py finnhub_cli.py --api-key TU_API_KEY quote AAPL
    py finnhub_cli.py --api-key TU_API_KEY profile MSFT
    py finnhub_cli.py --api-key TU_API_KEY search apple
    py finnhub_cli.py --api-key TU_API_KEY news AAPL --days 7
    py finnhub_cli.py --api-key TU_API_KEY peers NVDA
    py finnhub_cli.py --api-key TU_API_KEY earnings TSLA
    py finnhub_cli.py --api-key TU_API_KEY status US
    py finnhub_cli.py --api-key TU_API_KEY forex
    py finnhub_cli.py --api-key TU_API_KEY quote AAPL,MSFT,GOOGL (multiples simbolos)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import requests

BASE_URL = "https://finnhub.io/api/v1"


def call_api(endpoint, params, api_key):
    """Llama a la API de Finnhub."""
    params["token"] = api_key
    r = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=60)
    r.raise_for_status()
    return r.json()


# ── Comandos ─────────────────────────────────────────────────────────────────


def cmd_quote(args):
    """Cotizacion en tiempo real."""
    symbols = [s.strip().upper() for s in args.symbol.split(",")]
    for sym in symbols:
        try:
            data = call_api("quote", {"symbol": sym}, args.api_key)
            if "c" in data and data["c"] is not None:
                dp = data.get("dp", 0) or 0
                sign = "+" if dp >= 0 else ""
                print(f"{sym:<6} ${data['c']:<8.2f} ({sign}{dp:.2f}%)  "
                      f"H:${data.get('h',0):.2f} L:${data.get('l',0):.2f} "
                      f"O:${data.get('o',0):.2f} PC:${data.get('pc',0):.2f}")
            else:
                print(f"{sym}: Sin datos")
        except Exception as e:
            print(f"{sym}: Error - {e}")


def cmd_profile(args):
    """Perfil de empresa."""
    data = call_api("stock/profile2", {"symbol": args.symbol.upper()}, args.api_key)
    if data and "name" in data:
        mc = data.get("marketCapitalization", 0)
        print(f"{data.get('name','N/A')} ({data.get('ticker','N/A')})")
        print(f"  Industria: {data.get('finnhubIndustry','N/A')}")
        print(f"  Exchange: {data.get('exchange','N/A')}")
        print(f"  Market Cap: ${mc/1000:.2f}B")
        print(f"  Shares: {data.get('shareOutstanding','N/A'):,}")
        print(f"  IPO: {data.get('ipo','N/A')}")
        print(f"  Web: {data.get('weburl','N/A')}")
        print(f"  Pais: {data.get('country','N/A')}")
    else:
        print(f"Sin datos para {args.symbol.upper()}")


def cmd_search(args):
    """Busqueda de simbolos."""
    data = call_api("search", {"q": args.query}, args.api_key)
    results = data.get("result", [])
    if results:
        print(f"Resultados para '{args.query}': {len(results)}")
        for r in results[:15]:
            print(f"  {r.get('symbol','N/A'):<20} {r.get('description',''):<45} {r.get('type','N/A')}")
    else:
        print(f"Sin resultados para '{args.query}'")


def cmd_news(args):
    """Noticias de empresa."""
    to_date = args.to or datetime.now().strftime("%Y-%m-%d")
    from_date = args.from_date or (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    data = call_api("company-news", {
        "symbol": args.symbol.upper(), "from": from_date, "to": to_date
    }, args.api_key)
    if data:
        print(f"Noticias de {args.symbol.upper()} ({from_date} -> {to_date}): {len(data)} articulos")
        for i, article in enumerate(data[:args.limit]):
            dt = datetime.fromtimestamp(article.get("datetime", 0)).strftime("%Y-%m-%d")
            print(f"\n  [{i+1}] {dt} - {article.get('source','N/A')}")
            print(f"       {article.get('headline','')[:120]}")
    else:
        print(f"Sin noticias para {args.symbol.upper()}")


def cmd_peers(args):
    """Empresas similares."""
    data = call_api("stock/peers", {"symbol": args.symbol.upper()}, args.api_key)
    if data and isinstance(data, list):
        print(f"Peers de {args.symbol.upper()}: {', '.join(data)}")
    else:
        print(f"Sin peers para {args.symbol.upper()}")


def cmd_earnings(args):
    """Earnings historicos."""
    data = call_api("stock/earnings", {"symbol": args.symbol.upper(), "limit": args.limit},
                    args.api_key)
    if data and isinstance(data, list):
        print(f"Earnings de {args.symbol.upper()}:")
        for e in data:
            eps_a = e.get("epsActual", "N/A")
            eps_e = e.get("epsEstimate", "N/A")
            rev_a = e.get("revenueActual", "N/A")
            surprise = e.get("surprisePercent", "")
            s_str = f" (surprise: {surprise}%)" if surprise else ""
            print(f"  {e.get('period','N/A')}: EPS={eps_a} (estimado={eps_e}) revenue={rev_a}{s_str}")
    else:
        print(f"Sin earnings para {args.symbol.upper()}")


def cmd_status(args):
    """Estado del mercado."""
    data = call_api("stock/market-status", {"exchange": args.exchange.upper()}, args.api_key)
    is_open = data.get("isOpen", False)
    session = data.get("session") or "closed"
    status = "ABIERTO" if is_open else "CERRADO"
    print(f"Mercado {args.exchange.upper()}: {status} (session: {session})")


def cmd_forex(args):
    """Tasas de cambio forex."""
    data = call_api("forex/rates", {"base": args.base.upper()}, args.api_key)
    quotes = data.get("quote", {})
    if quotes:
        print(f"Tasas de cambio (base: {args.base.upper()}):")
        for pair, rate in list(quotes.items())[:20]:
            print(f"  {args.base.upper()}/{pair}: {rate}")
    else:
        print(f"Sin datos forex")


def cmd_metric(args):
    """Metricas financieras."""
    data = call_api("stock/metric", {"symbol": args.symbol.upper(), "metric": "all"},
                    args.api_key)
    metric_data = data.get("metric", {})
    if metric_data:
        print(f"Metricas de {args.symbol.upper()}:")
        for k, v in list(metric_data.items())[:25]:
            print(f"  {k}: {v}")
    else:
        print(f"Sin metricas para {args.symbol.upper()}")


def cmd_recommendation(args):
    """Recomendaciones de analistas."""
    data = call_api("stock/recommendation", {"symbol": args.symbol.upper()}, args.api_key)
    if data and isinstance(data, list):
        print(f"Recomendaciones de {args.symbol.upper()}:")
        for r in data[:5]:
            print(f"  {r.get('period','N/A')}: "
                  f"SB={r.get('strongBuy',0)} B={r.get('buy',0)} "
                  f"H={r.get('hold',0)} S={r.get('sell',0)} SS={r.get('strongSell',0)}")
    else:
        print(f"Sin recomendaciones para {args.symbol.upper()}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Finnhub CLI — Consultas rapidas a Finnhub.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--api-key", default=os.getenv("FINNHUB_API_KEY", ""),
                        help="API key (o FINNHUB_API_KEY env var)")

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # quote
    p_quote = subparsers.add_parser("quote", help="Cotizacion en tiempo real")
    p_quote.add_argument("symbol", help="Simbolo (ej: AAPL o AAPL,MSFT,GOOGL)")

    # profile
    p_profile = subparsers.add_parser("profile", help="Perfil de empresa")
    p_profile.add_argument("symbol", help="Simbolo (ej: AAPL)")

    # search
    p_search = subparsers.add_parser("search", help="Buscar simbolos")
    p_search.add_argument("query", help="Texto de busqueda")

    # news
    p_news = subparsers.add_parser("news", help="Noticias de empresa")
    p_news.add_argument("symbol", help="Simbolo")
    p_news.add_argument("--days", type=int, default=7, help="Dias hacia atras (default: 7)")
    p_news.add_argument("--from-date", dest="from_date", help="Fecha desde (YYYY-MM-DD)")
    p_news.add_argument("--to", help="Fecha hasta (YYYY-MM-DD)")
    p_news.add_argument("--limit", type=int, default=5, help="Max articulos (default: 5)")

    # peers
    p_peers = subparsers.add_parser("peers", help="Empresas similares")
    p_peers.add_argument("symbol", help="Simbolo")

    # earnings
    p_earnings = subparsers.add_parser("earnings", help="Earnings historicos")
    p_earnings.add_argument("symbol", help="Simbolo")
    p_earnings.add_argument("--limit", type=int, default=8, help="Cuantos (default: 8)")

    # status
    p_status = subparsers.add_parser("status", help="Estado del mercado")
    p_status.add_argument("exchange", nargs="?", default="US", help="Exchange (default: US)")

    # forex
    p_forex = subparsers.add_parser("forex", help="Tasas de cambio")
    p_forex.add_argument("--base", default="USD", help="Moneda base (default: USD)")

    # metric
    p_metric = subparsers.add_parser("metric", help="Metricas financieras")
    p_metric.add_argument("symbol", help="Simbolo")

    # recommendation
    p_rec = subparsers.add_parser("recommendation", help="Recomendaciones de analistas")
    p_rec.add_argument("symbol", help="Simbolo")

    args = parser.parse_args()

    if not args.api_key:
        log.error("API Key no encontrada. Usa --api-key o setea FINNHUB_API_KEY.")
        sys.exit(1)

    # Routing
    commands = {
        "quote": cmd_quote,
        "profile": cmd_profile,
        "search": cmd_search,
        "news": cmd_news,
        "peers": cmd_peers,
        "earnings": cmd_earnings,
        "status": cmd_status,
        "forex": cmd_forex,
        "metric": cmd_metric,
        "recommendation": cmd_recommendation,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        print("\nComandos disponibles: quote, profile, search, news, peers, earnings, status, forex, metric, recommendation")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.ERROR)
    log = logging.getLogger("finnhub-cli")
    main()
