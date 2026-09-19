"""
Finnhub API Client — Cliente completo para todos los endpoints GRATUITOS de Finnhub.

Uso:
    py finnhub_client.py --api-key TU_API_KEY --quote AAPL
    py finnhub_client.py --api-key TU_API_KEY --candle AAPL --resolution D --days 30
    py finnhub_client.py --api-key TU_API_KEY --profile AAPL
    py finnhub_client.py --api-key TU_API_KEY --peers AAPL
    py finnhub_client.py --api-key TU_API_KEY --financials AAPL --statement ic --freq annual
    py finnhub_client.py --api-key TU_API_KEY --earnings AAPL
    py finnhub_client.py --api-key TU_API_KEY --recommendation AAPL
    py finnhub_client.py --api-key TU_API_KEY --price-target AAPL
    py finnhub_client.py --api-key TU_API_KEY --news AAPL --from 2025-01-01 --to 2025-01-15
    py finnhub_client.py --api-key TU_API_KEY --market-news general
    py finnhub_client.py --api-key TU_API_KEY --forex-rates
    py finnhub_client.py --api-key TU_API_KEY --forex-candle OANDA:EUR_USD --resolution D --days 30
    py finnhub_client.py --api-key TU_API_KEY --crypto-candle BINANCE:BTCUSDT --resolution D --days 30
    py finnhub_client.py --api-key TU_API_KEY --search apple
    py finnhub_client.py --api-key TU_API_KEY --market-status US
    py finnhub_client.py --api-key TU_API_KEY --dividends AAPL --from 2024-01-01 --to 2025-01-01
    py finnhub_client.py --api-key TU_API_KEY --splits AAPL --from 2020-01-01 --to 2025-01-01
    py finnhub_client.py --api-key TU_API_KEY --economic-code
    py finnhub_client.py --api-key TU_API_KEY --economic GDP
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import requests

# ── Config ──────────────────────────────────────────────────────────────────

BASE_URL = "https://finnhub.io/api/v1"
REQUEST_DELAY = 1.0  # segundos entre requests (60 calls/min => 1 call/s)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("finnhub")


# ── Finnhub Client ──────────────────────────────────────────────────────────


class FinnhubClient:
    """Cliente para la API de Finnhub (endpoints gratuitos)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self._last_request = 0.0

    def _rate_limit(self):
        """Rate limiting: asegura pausa entre requests."""
        elapsed = time.time() - self._last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request = time.time()

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Request GET a la API de Finnhub."""
        self._rate_limit()
        url = f"{BASE_URL}/{endpoint}"
        if params is None:
            params = {}
        params["token"] = self.api_key
        try:
            r = self.session.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            status = r.status_code
            if status == 429:
                log.error("Rate limit excedido (429). Espera 1-2s y reintenta.")
            elif status == 403:
                log.error("Acceso denegado (403). Este endpoint requiere plan pago.")
                try:
                    err = r.json()
                    log.error(f"  Mensaje: {err.get('error', 'Sin detalles')}")
                except Exception:
                    log.error(f"  Respuesta: {r.text[:200]}")
            elif status == 401:
                log.error("API Key invalida (401). Revisa tu API key.")
            elif status == 404:
                log.error(f"Recurso no encontrado (404): {endpoint}")
            else:
                log.error(f"HTTP {status}: {e}")
                try:
                    log.error(f"  Respuesta: {r.text[:200]}")
                except Exception:
                    pass
            raise

    # ── Stock Market Data ────────────────────────────────────────────────

    def quote(self, symbol: str) -> dict:
        """Cotizacion en tiempo real."""
        return self._get("quote", {"symbol": symbol.upper()})

    def candle(
        self,
        symbol: str,
        resolution: str = "D",
        days: int = 30,
        from_ts: int = None,
        to_ts: int = None,
    ) -> dict:
        """Velas OHLCV historicas.

        Args:
            symbol: Simbolo (ej: AAPL)
            resolution: 1, 5, 15, 30, 60, D, W, M
            days: Dias hacia atras (usado si no se especifican from_ts/to_ts)
            from_ts: Timestamp UNIX inicio (opcional)
            to_ts: Timestamp UNIX fin (opcional)
        """
        if from_ts is None or to_ts is None:
            to_ts = int(time.time())
            from_ts = to_ts - (days * 86400)
        return self._get("stock/candle", {
            "symbol": symbol.upper(),
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts,
        })

    def profile2(self, symbol: str) -> dict:
        """Perfil de empresa v2 (GRATUITO)."""
        return self._get("stock/profile2", {"symbol": symbol.upper()})

    def peers(self, symbol: str) -> list:
        """Empresas similares."""
        return self._get("stock/peers", {"symbol": symbol.upper()})

    def market_status(self, exchange: str = "US") -> dict:
        """Estado del mercado (abierto/cerrado)."""
        return self._get("stock/market-status", {"exchange": exchange})

    def market_holiday(self, exchange: str = "US") -> dict:
        """Feriados del mercado."""
        return self._get("stock/market-holiday", {"exchange": exchange})

    def stock_symbols(self, exchange: str = "US", mic: str = None) -> list:
        """Lista de simbolos de un exchange."""
        params = {"exchange": exchange}
        if mic:
            params["mic"] = mic
        return self._get("stock/symbol", params)

    # ── Fundamentales ────────────────────────────────────────────────────

    def metric(self, symbol: str, metric_type: str = "all") -> dict:
        """Metricas financieras clave.

        Args:
            symbol: Simbolo
            metric_type: 'all', 'price', 'valuation', 'margin', 'profitability'
        """
        return self._get("stock/metric", {
            "symbol": symbol.upper(),
            "metric": metric_type,
        })

    def financials(self, symbol: str, statement: str = "ic", freq: str = "annual") -> dict:
        """Estados financieros.

        Args:
            symbol: Simbolo
            statement: 'ic' (income), 'bs' (balance), 'cf' (cash flow)
            freq: 'annual' o 'quarterly'
        """
        return self._get("stock/financials", {
            "symbol": symbol.upper(),
            "statement": statement,
            "freq": freq,
        })

    def financials_reported(self, symbol: str, freq: str = "quarterly") -> dict:
        """SEC Financials As Reported."""
        return self._get("stock/financials-reported", {
            "symbol": symbol.upper(),
            "freq": freq,
        })

    def earnings(self, symbol: str, limit: int = 5) -> list:
        """Historial de earnings."""
        return self._get("stock/earnings", {
            "symbol": symbol.upper(),
            "limit": limit,
        })

    def recommendation(self, symbol: str) -> list:
        """Recomendaciones de analistas."""
        return self._get("stock/recommendation", {"symbol": symbol.upper()})

    def price_target(self, symbol: str) -> dict:
        """Price targets de analistas."""
        return self._get("stock/price-target", {"symbol": symbol.upper()})

    def earnings_calendar(self, from_date: str = None, to_date: str = None, symbol: str = None) -> dict:
        """Calendario de earnings (free: 1 mes, solo US)."""
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if symbol:
            params["symbol"] = symbol.upper()
        return self._get("calendar/earnings", params)

    def ipo_calendar(self, from_date: str, to_date: str) -> dict:
        """Calendario de IPO."""
        return self._get("calendar/ipo", {
            "from": from_date,
            "to": to_date,
        })

    def dividends(self, symbol: str, from_date: str, to_date: str) -> list:
        """Historial de dividendos."""
        return self._get("stock/dividend", {
            "symbol": symbol.upper(),
            "from": from_date,
            "to": to_date,
        })

    def splits(self, symbol: str, from_date: str, to_date: str) -> list:
        """Historial de splits."""
        return self._get("stock/split", {
            "symbol": symbol.upper(),
            "from": from_date,
            "to": to_date,
        })

    # ── Noticias ─────────────────────────────────────────────────────────

    def company_news(self, symbol: str, from_date: str, to_date: str) -> list:
        """Noticias de una empresa (free: 1 ano)."""
        return self._get("company-news", {
            "symbol": symbol.upper(),
            "from": from_date,
            "to": to_date,
        })

    def market_news(self, category: str = "general") -> list:
        """Noticias del mercado.

        Args:
            category: 'general', 'forex', 'crypto', 'merger'
        """
        return self._get("news", {"category": category})

    # ── Forex ────────────────────────────────────────────────────────────

    def forex_rates(self, base: str = "USD") -> dict:
        """Tasas de cambio forex."""
        return self._get("forex/rates", {"base": base})

    def forex_candle(self, symbol: str, resolution: str = "D", days: int = 30,
                     from_ts: int = None, to_ts: int = None) -> dict:
        """Velas forex."""
        if from_ts is None or to_ts is None:
            to_ts = int(time.time())
            from_ts = to_ts - (days * 86400)
        return self._get("forex/candle", {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts,
        })

    def forex_exchanges(self) -> list:
        """Brokers forex disponibles."""
        return self._get("forex/exchange")

    def forex_symbols(self, exchange: str) -> list:
        """Pares forex de un broker."""
        return self._get("forex/symbol", {"exchange": exchange})

    # ── Crypto ───────────────────────────────────────────────────────────

    def crypto_candle(self, symbol: str, resolution: str = "D", days: int = 30,
                      from_ts: int = None, to_ts: int = None) -> dict:
        """Velas crypto."""
        if from_ts is None or to_ts is None:
            to_ts = int(time.time())
            from_ts = to_ts - (days * 86400)
        return self._get("crypto/candle", {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts,
        })

    def crypto_exchanges(self) -> list:
        """Exchanges crypto disponibles."""
        return self._get("crypto/exchange")

    def crypto_symbols(self, exchange: str) -> list:
        """Simbolos crypto de un exchange."""
        return self._get("crypto/symbol", {"exchange": exchange})

    # ── Datos Economicos ─────────────────────────────────────────────────

    def economic_codes(self) -> list:
        """Codigos de indicadores economicos."""
        return self._get("economic/code")

    def economic_data(self, code: str) -> list:
        """Datos economicos historicos."""
        return self._get("economic", {"code": code})

    def country_list(self) -> list:
        """Metadatos de paises."""
        return self._get("country")

    # ── Busqueda ─────────────────────────────────────────────────────────

    def search(self, query: str, exchange: str = None) -> dict:
        """Busqueda de simbolos."""
        params = {"q": query}
        if exchange:
            params["exchange"] = exchange
        return self._get("search", params)


# ── Output helpers ──────────────────────────────────────────────────────────


def print_section(title: str):
    """Imprime separador de seccion."""
    print(f"\n=== {title} ===")


def print_json(data):
    """Imprime datos como JSON formateado."""
    print(json.dumps(data, indent=2, default=str))


def print_quote(quote: dict, symbol: str):
    """Formatea cotizacion."""
    if not quote or "c" not in quote:
        print(f"  No se pudo obtener cotizacion para {symbol}")
        return
    c, d, dp = quote.get("c"), quote.get("d"), quote.get("dp")
    arrow = "+" if d is not None and d >= 0 else ""
    print(f"  {symbol}: ${c} ({arrow}{dp}%)")
    print(f"  Apertura: ${quote.get('o','N/A')} | Max: ${quote.get('h','N/A')} | Min: ${quote.get('l','N/A')}")
    print(f"  Cierre ant: ${quote.get('pc','N/A')}")


def print_profile(profile: dict):
    """Formatea perfil de empresa."""
    if not profile or "name" not in profile:
        print("  No se pudo obtener el perfil")
        return
    print(f"  {profile.get('name','N/A')} ({profile.get('ticker','N/A')})")
    print(f"  Industria: {profile.get('finnhubIndustry','N/A')}")
    print(f"  Exchange: {profile.get('exchange','N/A')}")
    mc = profile.get("marketCapitalization", 0)
    if mc:
        print(f"  Market Cap: ${mc/1000:.2f}B")
    print(f"  IPO: {profile.get('ipo','N/A')}")
    print(f"  Web: {profile.get('weburl','N/A')}")


def print_news(news: list, limit: int = 5):
    """Formatea noticias."""
    if not news:
        print("  Sin noticias")
        return
    for i, article in enumerate(news[:limit]):
        dt = datetime.fromtimestamp(article.get("datetime", 0)).strftime("%Y-%m-%d")
        print(f"  [{dt}] {article.get('headline','')[:90]}")
        print(f"         {article.get('source','')} | {article.get('url','')}")


def print_recommendation(recs: list):
    """Formatea recomendaciones de analistas."""
    if not recs:
        print("  Sin datos de recomendaciones")
        return
    for r in recs[:5]:
        print(f"  Periodo: {r.get('period','N/A')}")
        print(f"    Strong Buy: {r.get('strongBuy',0)} | Buy: {r.get('buy',0)} | Hold: {r.get('hold',0)} | Sell: {r.get('sell',0)} | Strong Sell: {r.get('strongSell',0)}")


def print_earnings(earnings: list):
    """Formatea earnings."""
    if not earnings:
        print("  Sin datos de earnings")
        return
    for e in earnings[:8]:
        print(f"  {e.get('period','N/A')}: EPS actual={e.get('epsActual','N/A')} estimado={e.get('epsEstimate','N/A')} revenue={e.get('revenueActual','N/A')}")


def print_candle(candle: dict, symbol: str):
    """Formatea velas OHLCV."""
    status = candle.get("s", "no_data")
    if status == "ok":
        count = len(candle.get("c", []))
        dates = [datetime.fromtimestamp(t).strftime("%Y-%m-%d") for t in candle.get("t", [])]
        print(f"  {symbol}: {count} velas")
        print(f"  Periodo: {dates[0] if dates else 'N/A'} -> {dates[-1] if dates else 'N/A'}")
        print(f"  Precio rango: ${min(candle.get('l',[0])):.2f} - ${max(candle.get('h',[0])):.2f}")
        if count <= 10:
            for i in range(count):
                print(f"    {dates[i]}: O={candle['o'][i]} H={candle['h'][i]} L={candle['l'][i]} C={candle['c'][i]} V={candle['v'][i]}")
    else:
        print(f"  {symbol}: Sin datos (status={status})")


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Finnhub API Client — Accede a todos los endpoints gratuitos de Finnhub.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--api-key",
        default=os.getenv("FINNHUB_API_KEY", ""),
        help="Finnhub API key (o FINNHUB_API_KEY env var)",
    )

    # Acciones
    parser.add_argument("--quote", help="Cotizacion en tiempo real (ej: AAPL)")
    parser.add_argument("--candle", help="Velas OHLCV (ej: AAPL)")
    parser.add_argument("--resolution", default="D", choices=["1","5","15","30","60","D","W","M"],
                        help="Resolucion de velas (default: D)")
    parser.add_argument("--days", type=int, default=30, help="Dias hacia atras (default: 30)")
    parser.add_argument("--profile", help="Perfil de empresa v2 (ej: AAPL)")
    parser.add_argument("--peers", help="Empresas similares (ej: AAPL)")
    parser.add_argument("--metric", help="Metricas financieras (ej: AAPL)")
    parser.add_argument("--metric-type", default="all",
                        choices=["all","price","valuation","margin","profitability"],
                        help="Tipo de metrica (default: all)")
    parser.add_argument("--financials", help="Estados financieros (ej: AAPL)")
    parser.add_argument("--statement", default="ic", choices=["ic","bs","cf"],
                        help="Tipo de estado (ic=income, bs=balance, cf=cashflow)")
    parser.add_argument("--freq", default="annual", choices=["annual","quarterly"],
                        help="Frecuencia")
    parser.add_argument("--earnings", help="Earnings historicos (ej: AAPL)")
    parser.add_argument("--recommendation", help="Recomendaciones de analistas (ej: AAPL)")
    parser.add_argument("--price-target", dest="price_target", help="Price targets (ej: AAPL)")
    parser.add_argument("--news", help="Noticias de empresa (ej: AAPL)")
    parser.add_argument("--from", dest="from_date", help="Fecha desde (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="Fecha hasta (YYYY-MM-DD)")
    parser.add_argument("--market-news", dest="market_news",
                        choices=["general","forex","crypto","merger"],
                        help="Noticias del mercado por categoria")
    parser.add_argument("--forex-rates", dest="forex_rates", action="store_true",
                        help="Tasas de cambio forex")
    parser.add_argument("--forex-base", default="USD", help="Moneda base forex (default: USD)")
    parser.add_argument("--forex-candle", dest="forex_candle",
                        help="Velas forex (ej: OANDA:EUR_USD)")
    parser.add_argument("--crypto-candle", dest="crypto_candle",
                        help="Velas crypto (ej: BINANCE:BTCUSDT)")
    parser.add_argument("--search", help="Buscar simbolos (ej: apple)")
    parser.add_argument("--market-status", dest="market_status",
                        help="Estado del mercado (ej: US)")
    parser.add_argument("--dividends", help="Historial de dividendos (ej: AAPL)")
    parser.add_argument("--splits", help="Historial de splits (ej: AAPL)")
    parser.add_argument("--economic-code", dest="economic_code", action="store_true",
                        help="Listar codigos economicos")
    parser.add_argument("--economic", help="Datos economicos por codigo (ej: GDP)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    api_key = args.api_key
    if not api_key:
        log.error(
            "API Key no encontrada. Usa --api-key o setea FINNHUB_API_KEY env var.\n"
            "  Obtener gratis: https://finnhub.io/register"
        )
        sys.exit(1)

    client = FinnhubClient(api_key)
    use_json = args.json

    # ── Quote ────────────────────────────────────────────────────────────
    if args.quote:
        data = client.quote(args.quote)
        if use_json:
            print_json(data)
        else:
            print_section(f"Quote: {args.quote.upper()}")
            print_quote(data, args.quote.upper())

    # ── Candle ─────────────────────────────────────────────────────────
    elif args.candle:
        data = client.candle(args.candle, args.resolution, args.days)
        if use_json:
            print_json(data)
        else:
            print_section(f"Candle: {args.candle.upper()} ({args.resolution})")
            print_candle(data, args.candle.upper())

    # ── Profile ─────────────────────────────────────────────────────────
    elif args.profile:
        data = client.profile2(args.profile)
        if use_json:
            print_json(data)
        else:
            print_section(f"Profile: {args.profile.upper()}")
            print_profile(data)

    # ── Peers ───────────────────────────────────────────────────────────
    elif args.peers:
        data = client.peers(args.peers)
        if use_json:
            print_json(data)
        else:
            print_section(f"Peers: {args.peers.upper()}")
            if data:
                print(f"  {', '.join(data)}")
            else:
                print("  Sin datos")

    # ── Metric ──────────────────────────────────────────────────────────
    elif args.metric:
        data = client.metric(args.metric, args.metric_type)
        if use_json:
            print_json(data)
        else:
            print_section(f"Metric: {args.metric.upper()} ({args.metric_type})")
            metric_data = data.get("metric", {})
            if metric_data:
                for k, v in list(metric_data.items())[:20]:
                    print(f"  {k}: {v}")
            else:
                print("  Sin datos de metricas")

    # ── Financials ─────────────────────────────────────────────────────
    elif args.financials:
        data = client.financials(args.financials, args.statement, args.freq)
        if use_json:
            print_json(data)
        else:
            stmt_names = {"ic": "Income Statement", "bs": "Balance Sheet", "cf": "Cash Flow"}
            print_section(f"Financials: {args.financials.upper()} ({stmt_names.get(args.statement, args.statement)})")
            fin_list = data.get("financials", [])
            if fin_list:
                for fin in fin_list[:3]:
                    print(f"  Periodo: {fin.get('period','N/A')}")
                    for k, v in list(fin.items())[:10]:
                        if k != "period":
                            print(f"    {k}: {v}")
            else:
                print("  Sin datos financieros")

    # ── Earnings ───────────────────────────────────────────────────────
    elif args.earnings:
        data = client.earnings(args.earnings)
        if use_json:
            print_json(data)
        else:
            print_section(f"Earnings: {args.earnings.upper()}")
            print_earnings(data)

    # ── Recommendation ─────────────────────────────────────────────────
    elif args.recommendation:
        data = client.recommendation(args.recommendation)
        if use_json:
            print_json(data)
        else:
            print_section(f"Recommendation: {args.recommendation.upper()}")
            print_recommendation(data)

    # ── Price Target ──────────────────────────────────────────────────
    elif args.price_target:
        data = client.price_target(args.price_target)
        if use_json:
            print_json(data)
        else:
            print_section(f"Price Target: {args.price_target.upper()}")
            if data:
                print(f"  Target High: ${data.get('targetHigh','N/A')}")
                print(f"  Target Low: ${data.get('targetLow','N/A')}")
                print(f"  Target Mean: ${data.get('targetMean','N/A')}")
                print(f"  Target Median: ${data.get('targetMedian','N/A')}")
                print(f"  Last Updated: {data.get('lastUpdated','N/A')}")

    # ── News ───────────────────────────────────────────────────────────
    elif args.news:
        to_date = args.to_date or datetime.now().strftime("%Y-%m-%d")
        from_date = args.from_date or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        data = client.company_news(args.news, from_date, to_date)
        if use_json:
            print_json(data)
        else:
            print_section(f"News: {args.news.upper()} ({from_date} -> {to_date})")
            print_news(data, limit=10)

    # ── Market News ──────────────────────────────────────────────────
    elif args.market_news:
        data = client.market_news(args.market_news)
        if use_json:
            print_json(data)
        else:
            print_section(f"Market News: {args.market_news}")
            print_news(data, limit=10)

    # ── Forex Rates ──────────────────────────────────────────────────
    elif args.forex_rates:
        data = client.forex_rates(args.forex_base)
        if use_json:
            print_json(data)
        else:
            print_section(f"Forex Rates (base: {args.forex_base})")
            quotes = data.get("quote", {})
            for pair, rate in list(quotes.items())[:15]:
                print(f"  {args.forex_base}/{pair}: {rate}")

    # ── Forex Candle ────────────────────────────────────────────────
    elif args.forex_candle:
        data = client.forex_candle(args.forex_candle, args.resolution, args.days)
        if use_json:
            print_json(data)
        else:
            print_section(f"Forex Candle: {args.forex_candle}")
            print_candle(data, args.forex_candle)

    # ── Crypto Candle ───────────────────────────────────────────────
    elif args.crypto_candle:
        data = client.crypto_candle(args.crypto_candle, args.resolution, args.days)
        if use_json:
            print_json(data)
        else:
            print_section(f"Crypto Candle: {args.crypto_candle}")
            print_candle(data, args.crypto_candle)

    # ── Search ──────────────────────────────────────────────────────
    elif args.search:
        data = client.search(args.search)
        if use_json:
            print_json(data)
        else:
            print_section(f"Search: '{args.search}'")
            results = data.get("result", [])
            if results:
                for r in results[:10]:
                    print(f"  {r.get('symbol','N/A'):<15} {r.get('description',''):<40} {r.get('type','N/A')}")
            else:
                print("  Sin resultados")

    # ── Market Status ───────────────────────────────────────────────
    elif args.market_status:
        data = client.market_status(args.market_status)
        if use_json:
            print_json(data)
        else:
            exch = data.get("exchange", args.market_status)
            is_open = data.get("isOpen", False)
            session = data.get("session") or "closed"
            status_str = "ABIERTO" if is_open else "CERRADO"
            print(f"  Mercado {exch}: {status_str} (session: {session})")

    # ── Dividends ──────────────────────────────────────────────────
    elif args.dividends:
        to_date = args.to_date or datetime.now().strftime("%Y-%m-%d")
        from_date = args.from_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        data = client.dividends(args.dividends, from_date, to_date)
        if use_json:
            print_json(data)
        else:
            print_section(f"Dividends: {args.dividends.upper()} ({from_date} -> {to_date})")
            if data:
                for d in data[:10]:
                    print(f"  {d.get('date','N/A')}: ${d.get('amount','N/A')} (pay: {d.get('payDate','N/A')})")
            else:
                print("  Sin dividendos en el periodo")

    # ── Splits ─────────────────────────────────────────────────────
    elif args.splits:
        to_date = args.to_date or datetime.now().strftime("%Y-%m-%d")
        from_date = args.from_date or "2020-01-01"
        data = client.splits(args.splits, from_date, to_date)
        if use_json:
            print_json(data)
        else:
            print_section(f"Splits: {args.splits.upper()} ({from_date} -> {to_date})")
            if data:
                for d in data[:10]:
                    print(f"  {d.get('date','N/A')}: {d.get('fromFactor','?')}:{d.get('toFactor','?')}")
            else:
                print("  Sin splits en el periodo")

    # ── Economic Code ──────────────────────────────────────────────
    elif args.economic_code:
        data = client.economic_codes()
        if use_json:
            print_json(data)
        else:
            print_section("Economic Codes")
            if data:
                for c in data[:20]:
                    print(f"  {c.get('code','N/A'):<15} {c.get('name',''):<50} {c.get('country','N/A')}")
                if len(data) > 20:
                    print(f"  ... y {len(data)-20} mas")
            else:
                print("  Sin datos")

    # ── Economic Data ──────────────────────────────────────────────
    elif args.economic:
        data = client.economic_data(args.economic)
        if use_json:
            print_json(data)
        else:
            print_section(f"Economic Data: {args.economic}")
            if data:
                for d in data[:10]:
                    print(f"  {d.get('date','N/A')}: {d.get('value','N/A')}")
            else:
                print("  Sin datos economicos")

    else:
        parser.print_help()
        print("\nUsa --quote, --candle, --profile, --peers, --metric, --financials,")
        print("--earnings, --recommendation, --price-target, --news, --market-news,")
        print("--forex-rates, --forex-candle, --crypto-candle, --search, --market-status,")
        print("--dividends, --splits, --economic-code o --economic")


if __name__ == "__main__":
    main()
