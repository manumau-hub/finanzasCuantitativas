#!/usr/bin/env python3
"""
MarketScreener CLI — Consultas rapidas de datos financieros gratuitos.

Uso:
    python marketscreener_cli.py quote AAPL
    python marketscreener_cli.py transcript GGAL
    python marketscreener_cli.py profile AAPL
    python marketscreener_cli.py search YPF
    python marketscreener_cli.py consensus AAPL --json

Comandos disponibles:
    search      Buscar empresa por ticker/nombre
    quote       Cotizacion actual y datos basicos
    profile     Perfil completo de la empresa
    transcript  Ultimo earnings transcript
    transcripts Lista de transcripts disponibles
    financials  Estados financieros (income, balance, cashflow, ratios)
    valuation   Ratios de valuacion (PE, EV/EBITDA, etc.)
    consensus   Consenso de analistas
    ratings     Ratings Surperformance (Trader, Investor, Global)
    news        Ultimas noticias
    calendar    Calendario corporativo
    insider     Transacciones de insiders
    shareholders Principales accionistas
    governance  Gobierno corporativo (board, management)
"""

import json
import sys

from marketscreener_client import MarketScreenerClient


def print_result(data):
    """Imprime resultado en formato legible."""
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                print(f"\n[{k}]")
                print_result(v)
            else:
                print(f"  {k}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                print(f"\n--- Item {i+1} ---")
                print_result(item)
            else:
                print(f"  [{i}] {item}")
    else:
        print(f"  {data}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    ticker = sys.argv[2].upper()

    # Parsear opciones adicionales
    kwargs = {}
    extra_args = sys.argv[3:]

    i = 0
    while i < len(extra_args):
        arg = extra_args[i]
        if arg in ("--json", "-j"):
            kwargs["json"] = True
        elif arg in ("--statement", "-s") and i + 1 < len(extra_args):
            kwargs["statement"] = extra_args[i + 1]
            i += 1
        elif arg in ("--quarter", "-q") and i + 1 < len(extra_args):
            kwargs["quarter"] = extra_args[i + 1]
            i += 1
        elif arg in ("--year", "-y") and i + 1 < len(extra_args):
            kwargs["year"] = extra_args[i + 1]
            i += 1
        elif arg in ("--max", "-m") and i + 1 < len(extra_args):
            kwargs["max"] = int(extra_args[i + 1])
            i += 1
        elif arg in ("--delay", "-d") and i + 1 < len(extra_args):
            kwargs["delay"] = float(extra_args[i + 1])
            i += 1
        i += 1

    output_json = kwargs.pop("json", False)

    client = MarketScreenerClient(min_delay=kwargs.get("delay", 1.5))

    try:
        if command == "search":
            data = client.search_company(ticker)
        elif command == "quote":
            data = client.get_quote(ticker)
        elif command == "profile":
            data = client.get_profile(ticker)
        elif command == "transcript":
            if "quarter" in kwargs and "year" in kwargs:
                data = client.get_transcript_by_quarter(
                    ticker, kwargs["quarter"], kwargs["year"]
                )
            else:
                data = client.get_transcript(ticker)
        elif command == "transcripts":
            data = client.get_transcripts_list(ticker, max_items=kwargs.get("max", 10))
        elif command == "financials":
            data = client.get_financials(
                ticker, statement=kwargs.get("statement", "income")
            )
        elif command == "valuation":
            data = client.get_valuation(ticker)
        elif command == "consensus":
            data = client.get_consensus(ticker)
        elif command == "ratings":
            data = client.get_ratings(ticker)
        elif command == "news":
            data = client.get_news(ticker, max_items=kwargs.get("max", 15))
        elif command == "calendar":
            data = client.get_calendar(ticker)
        elif command == "insider":
            data = client.get_insider_trading(ticker, max_items=kwargs.get("max", 15))
        elif command == "shareholders":
            data = client.get_shareholders(ticker, max_items=kwargs.get("max", 10))
        elif command == "governance":
            data = client.get_governance(ticker)
        else:
            print(f"Comando desconocido: {command}")
            print(__doc__)
            sys.exit(1)

        if output_json:
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"\n=== {command.upper()} | {ticker} ===\n")
            print_result(data)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
