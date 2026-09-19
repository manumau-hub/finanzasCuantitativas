#!/usr/bin/env python3
"""
EarningsWhispers Client — Earnings Transcripts API (Cobertura Global).

Accede a transcripts completos de earnings calls via la API publica de
earningswhispers.com SIN autenticacion ni anti-bot. Cobertura global:
US, Europa, Asia, LatAm, Canada. +60 tickers testeados (AAPL, MSFT,
GOOG, GGAL, YPF, SHEL, TM, VALE...).

API endpoint: GET https://www.earningswhispers.com/api/conferencecalls?t={TICKER}

Dependencias: curl_cffi
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from curl_cffi import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://www.earningswhispers.com"
API_URL = f"{BASE_URL}/api/conferencecalls"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Referer": "https://www.earningswhispers.com/",
    "X-Requested-With": "XMLHttpRequest",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ew")


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class Speaker:
    """Participante del earnings call."""
    id: str
    name: str
    title: str = ""
    text: str = ""


@dataclass
class Transcript:
    """Earnings transcript completo."""
    ticker: str
    company: str
    ccid: int
    date: str
    year: int
    quarter: int
    speakers: List[Speaker]
    summary: Optional[str] = None
    ai_summary: Optional[str] = None
    status: str = ""

    @property
    def quarter_label(self) -> str:
        return f"Q{self.quarter}"

    @property
    def date_parsed(self) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(self.date.replace("Z", ""))
        except (ValueError, AttributeError):
            return None

    @property
    def full_text(self) -> str:
        """Texto completo con identificacion de speakers."""
        parts = []
        for s in self.speakers:
            tag = f"[{s.name}]" if s.name != "Operator" else "[Operator]"
            parts.append(f"{tag} {s.text}")
        return "\n\n".join(parts)

    def _find_qa_start(self, text: str) -> Optional[int]:
        """
        Encuentra donde empieza el Q&A.

        Busca la ULTIMA ocurrencia de los marcadores tipicos de inicio
        de Q&A. El operador suele mencionarlo al principio ("after the
        presentation we'll have Q&A") y al final ("we will now begin Q&A").
        La ultima ocurrencia es la correcta.
        """
        markers = [
            # Pattern: "We're going to start the question and answer session"
            r"(?:we.s?re|we will|we shall|i will)\s*(?:now\s+)?(?:going to\s+|proceed to\s+|)\s*(?:start|begin|open)\s+(?:the\s+)?(?:question.?.?and.?.?answer|q.?.?a)\s+(?:session|period|portion|segment)?",
            # Pattern: "The floor is now open for questions"
            r"(?:the\s+)?floor\s+is\s+(?:now\s+)?open\s+for\s+questions",
            # Pattern: "We will now open the call/line for questions"
            r"(?:we\s+)?will\s+now\s+open\s+(?:the\s+)?(?:call|line)\s+for\s+questions",
            # Pattern: "We will now take questions"
            r"(?:we\s+)?will\s+now\s+take\s+(?:your\s+)?questions",
            # Pattern: "So now we are open to questions" 
            r"(?:so\s+)?now\s+(?:we\s+)?(?:are|will\s+be)\s+open\s+(?:to|for)\s+questions",
            # Pattern: "Now we will begin Q&A"
            r"now\s+(?:we\s+)?(?:will|shall|are\s+going\s+to)\s+(?:begin|start)\s+(?:the\s+)?q.?a",
            # Fallback pattern: "Question and Answer" as a section header
            r"^\s*question\s*(?:and|&|/)\s*answer\s*:?\s*$",
        ]

        last_pos = None
        for marker in markers:
            for m in re.finditer(marker, text, re.I):
                last_pos = m.start()

        if last_pos is not None:
            return last_pos

        # Fallback: ultimo "Question and Answer" generico
        for marker in [
            r"Question\s*and\s*Answer",
            r"Questions?\s*&\s*Answers?",
        ]:
            for m in re.finditer(marker, text, re.I):
                last_pos = m.start()

        return last_pos

    @property
    def prepared_remarks(self) -> str:
        """Texto de la presentacion del management (antes del Q&A)."""
        text = self.full_text
        qa_start = self._find_qa_start(text)

        if qa_start is not None:
            return text[:qa_start].strip()

        # Fallback: buscar primer speaker que sea Analyst
        for i, s in enumerate(self.speakers):
            if "analyst" in s.title.lower() and i > 1:
                parts = []
                for sp in self.speakers[:i]:
                    tag = f"[{sp.name}]" if sp.name != "Operator" else "[Operator]"
                    parts.append(f"{tag} {sp.text}")
                return "\n\n".join(parts).strip()

        # Fallback extremo: primeros 60%
        lines = text.split("\n\n")
        return "\n\n".join(lines[:int(len(lines) * 0.6)]).strip()

    @property
    def qa_section(self) -> str:
        """Seccion de preguntas y respuestas."""
        text = self.full_text
        qa_start = self._find_qa_start(text)

        if qa_start is not None:
            return text[qa_start:].strip()

        # Fallback: primer Analyst
        for i, s in enumerate(self.speakers):
            if "analyst" in s.title.lower() and i > 1:
                parts = []
                for sp in self.speakers[i:]:
                    tag = f"[{sp.name}]" if sp.name != "Operator" else "[Operator]"
                    parts.append(f"{tag} {sp.text}")
                return "\n\n".join(parts).strip()

        lines = text.split("\n\n")
        return "\n\n".join(lines[int(len(lines) * 0.6):]).strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a dict para serializacion JSON."""
        # Participantes unicos (por nombre, sin operador)
        seen = set()
        participants = []
        for s in self.speakers:
            if s.name != "Operator" and s.name not in seen:
                seen.add(s.name)
                participants.append({"name": s.name, "title": s.title or ""})

        return {
            "ticker": self.ticker,
            "company": self.company,
            "ccid": self.ccid,
            "date": self.date,
            "year": self.year,
            "quarter": f"Q{self.quarter}",
            "status": self.status,
            "summary": self.summary,
            "ai_summary": self.ai_summary,
            "participants": participants,
            "prepared_remarks": self.prepared_remarks,
            "qa_section": self.qa_section,
        }


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class EarningsWhispersClient:
    """
    Cliente para la API de EarningsWhispers.

    Obtiene earnings transcripts completos SIN autenticacion.

    Args:
        min_delay: Segundos entre requests (default: 1.0)
        use_cache: Cachear localmente (default: True)

    Uso:
        >>> client = EarningsWhispersClient()
        >>> tr = client.get_transcript("GGAL")
        >>> print(tr.prepared_remarks[:500])
        >>> print(tr.qa_section[:500])
        >>> tr.to_dict()  # para JSON
    """

    def __init__(self, min_delay: float = 1.0, use_cache: bool = True):
        self.min_delay = min_delay
        self.use_cache = use_cache
        self._last_request = 0.0

        self._session = requests.Session(impersonate="chrome131")
        self._session.headers.update(BROWSER_HEADERS)

        if use_cache:
            _ensure_cache_dir()

    def _request(self, url: str) -> requests.Response:
        elapsed = time.time() - self._last_request
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self._last_request = time.time()
        log.debug(f"GET {url}")
        resp = self._session.get(url, timeout=30)
        if resp.status_code != 200:
            log.warning(f"  -> {resp.status_code} ({len(resp.text)} bytes)")
        return resp

    # ---- Transcript Fetching ----------------------------------------------

    def get_transcript(
        self,
        ticker: str,
        force_refresh: bool = False,
    ) -> Optional[Transcript]:
        """
        Obtiene el earnings transcript mas reciente para un ticker.

        Args:
            ticker: Simbolo bursatil (AAPL, MSFT, GOOG, GGAL, YPF, SHEL...)
            force_refresh: Ignorar cache local

        Returns:
            Transcript object o None si no hay datos
        """
        ticker = ticker.upper().strip()

        cache_key = f"transcript_{ticker}"
        if not force_refresh and self.use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                log.info(f"Cache HIT for {ticker}")
                return self._from_cache(cached)

        log.info(f"Fetching transcript for {ticker}...")
        url = f"{API_URL}?t={ticker}"
        resp = self._request(url)

        if resp.status_code != 200:
            log.error(f"API returned {resp.status_code} for {ticker}")
            return None

        try:
            data = resp.json()
        except json.JSONDecodeError:
            log.error(f"Invalid JSON response for {ticker}")
            return None

        if not isinstance(data, list) or len(data) == 0:
            log.warning(f"No transcript data for {ticker}")
            return None

        item = data[0]
        transcript = self._parse_item(item, ticker)

        if transcript and self.use_cache:
            self._save_cache(cache_key, item)

        return transcript

    def get_transcripts_batch(
        self,
        tickers: List[str],
        force_refresh: bool = False,
    ) -> Dict[str, Optional[Transcript]]:
        """Obtiene transcripts para multiples tickers."""
        results = {}
        for t in tickers:
            results[t] = self.get_transcript(t, force_refresh=force_refresh)
        return results

    # ---- Parsing -----------------------------------------------------------

    def _parse_item(self, item: Dict, ticker: str) -> Optional[Transcript]:
        """Convierte un item de la API en Transcript."""
        try:
            # Parsear speakers
            speakers_raw = item.get("speakers", "[]")
            if isinstance(speakers_raw, str):
                speakers_list = json.loads(speakers_raw) if speakers_raw else []
            else:
                speakers_list = speakers_raw

            # Parsear speakerMap
            sm_raw = item.get("speakerMap", "{}")
            if isinstance(sm_raw, str):
                speaker_map = json.loads(sm_raw) if sm_raw else {}
            else:
                speaker_map = sm_raw

            speakers = []
            for sp in speakers_list:
                sp_id = sp.get("speaker", "")
                sp_text = sp.get("text", "")
                sp_info = speaker_map.get(sp_id, {})
                sp_name = sp_info.get("name", sp_id)
                sp_title = sp_info.get("title", "")

                speakers.append(Speaker(
                    id=sp_id,
                    name=sp_name,
                    title=sp_title,
                    text=sp_text,
                ))

            return Transcript(
                ticker=ticker,
                company=item.get("company", ""),
                ccid=item.get("ccid", 0),
                date=item.get("ccDate", ""),
                year=item.get("ccYear", 0),
                quarter=item.get("ccQtr", 0),
                speakers=speakers,
                summary=item.get("summary"),
                ai_summary=item.get("aiSummary"),
                status=item.get("status", ""),
            )

        except Exception as e:
            log.error(f"Failed to parse transcript for {ticker}: {e}")
            return None

    # ---- Company Info ------------------------------------------------------

    def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Obtiene info basica de la empresa desde el transcript."""
        tr = self.get_transcript(ticker)
        if not tr:
            return {"ticker": ticker.upper(), "error": "No data available"}

        # Participantes unicos
        seen = set()
        participants = [s for s in tr.speakers if s.name != "Operator" and s.name not in seen and not seen.add(s.name)]

        return {
            "ticker": tr.ticker,
            "company": tr.company,
            "last_transcript_date": tr.date,
            "last_transcript_quarter": tr.quarter_label,
            "last_transcript_year": tr.year,
            "participants_count": len(participants),
        }

    # ---- Tickers de Referencia (solo como ejemplo) -----------------------

    SAMPLE_TICKERS_GLOBAL = [
        # US Large Cap
        "AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA",
        "JPM", "GS", "BAC", "V", "MA", "WMT", "DIS", "NKE",
        "XOM", "CVX", "UNH", "JNJ", "PFE", "KO", "PEP", "MCD",
        # Europe
        "SHEL", "BP", "TTE", "HSBC", "BBVA",
        # Asia
        "TM", "HMC", "BABA", "JD", "TCEHY", "INFY",
        # LatAm
        "ITUB", "BBD", "VALE", "AMX", "FMX", "SBS",
        # Argentina
        "GGAL", "YPF", "TGS", "PAM", "BMA", "CEPU",
        # Canada
        "CNQ", "SU", "RY", "TD",
    ]

    @classmethod
    def list_sample_tickers(cls) -> List[str]:
        """Lista de tickers de ejemplo (cobertura global)."""
        return cls.SAMPLE_TICKERS_GLOBAL.copy()

    # ---- Cache -------------------------------------------------------------

    def _cache_path(self, key: str) -> str:
        safe = re.sub(r'[^\w\-_]', '_', key)
        return os.path.join(CACHE_DIR, f"{safe}.json")

    def _load_cache(self, key: str) -> Optional[Any]:
        path = self._cache_path(key)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                age = time.time() - data.get("_cached_at", 0)
                if age < 86400:  # 24h
                    return data.get("data")
            except Exception:
                pass
        return None

    def _save_cache(self, key: str, data: Any):
        path = self._cache_path(key)
        try:
            path = self._cache_path(key)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({
                    "data": data,
                    "_cached_at": time.time(),
                    "_key": key,
                }, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            log.warning(f"Cache save failed: {e}")

    def _from_cache(self, data: Dict) -> Optional[Transcript]:
        return self._parse_item(data, data.get("ticker", ""))

    def clear_cache(self, ticker: Optional[str] = None):
        if not os.path.exists(CACHE_DIR):
            return
        for fname in os.listdir(CACHE_DIR):
            if ticker and ticker not in fname:
                continue
            try:
                os.remove(os.path.join(CACHE_DIR, fname))
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Quick functions
# ---------------------------------------------------------------------------

def get_transcript(ticker: str) -> Optional[Dict[str, Any]]:
    """Funcion rapida: obtiene transcript como dict."""
    client = EarningsWhispersClient()
    tr = client.get_transcript(ticker)
    return tr.to_dict() if tr else None


def get_transcripts_batch(tickers: List[str]) -> Dict[str, Any]:
    """Funcion rapida: obtiene multiples transcripts."""
    client = EarningsWhispersClient()
    results = client.get_transcripts_batch(tickers)
    return {t: tr.to_dict() if tr else None for t, tr in results.items()}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_transcript(tr: Transcript, show_full: bool = False):
    """Imprime transcript en formato legible."""
    print(f"\n{'='*70}")
    print(f"  {tr.company} ({tr.ticker})")
    print(f"  {tr.quarter_label} {tr.year} | {tr.date} | Status: {tr.status or 'OK'}")
    print(f"{'='*70}\n")

    # Participantes unicos
    seen = set()
    participants = [s for s in tr.speakers if s.name != "Operator" and s.name not in seen and not seen.add(s.name)]
    if participants:
        print(f"Participantes ({len(participants)}):")
        for s in participants:
            title = f" ({s.title})" if s.title else ""
            print(f"  - {s.name}{title}")
        print()

    # Summary
    if tr.summary:
        print(f"Summary:")
        print(f"  {tr.summary[:800]}{'...' if len(tr.summary) > 800 else ''}\n")

    if tr.ai_summary:
        print(f"AI Summary:")
        print(f"  {tr.ai_summary[:800]}{'...' if len(tr.ai_summary) > 800 else ''}\n")

    # Prepared Remarks
    pr = tr.prepared_remarks
    if pr:
        max_len = 3000 if show_full else 1500
        print(f"Prepared Remarks ({len(pr)} chars):")
        print(f"{'-'*50}")
        print(f"  {pr[:max_len]}{'...' if len(pr) > max_len else ''}")
        print()

    # Q&A
    qa = tr.qa_section
    if qa:
        max_len = 2000 if show_full else 1000
        print(f"Q&A Section ({len(qa)} chars):")
        print(f"{'-'*50}")
        print(f"  {qa[:max_len]}{'...' if len(qa) > max_len else ''}")
        print()

    print(f"{'='*70}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="EarningsWhispers — Earnings Transcripts API (Cobertura Global)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s get AAPL                        # Ultimo transcript de Apple
  %(prog)s get GOOG --json                  # Output JSON
  %(prog)s get SHEL --full                  # Texto completo
  %(prog)s batch MSFT,GOOG,AMZN --json      # Multiples tickers
  %(prog)s info GGAL                        # Info empresa
  %(prog)s list                             # Tickers de ejemplo (global)
        """
    )
    parser.add_argument("command", choices=["get", "batch", "info", "list"])
    parser.add_argument("ticker", nargs="?", help="Ticker (AAPL, GOOG, GGAL, YPF, SHEL... - cobertura global)")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")
    parser.add_argument("-f", "--full", action="store_true", help="Texto completo")
    parser.add_argument("--no-cache", action="store_true", help="Ignorar cache")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay entre requests")

    args = parser.parse_args()
    client = EarningsWhispersClient(min_delay=args.delay, use_cache=not args.no_cache)

    if args.command == "list":
        print("\nTickers de ejemplo (cobertura global):")
        for t in EarningsWhispersClient.list_sample_tickers():
            print(f"  - {t}")
        print("\nNo es una lista exhaustiva. Cualquier ticker de empresa publica")
        print("con earnings calls puede funcionar. Probar con --json para ver datos.")
        return

    if args.command == "info":
        if not args.ticker:
            print("Error: Se requiere un ticker")
            sys.exit(1)
        info = client.get_company_info(args.ticker)
        if args.json:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"\n=== {info['ticker']} ===\n")
            for k, v in info.items():
                print(f"  {k}: {v}")
            print()
        return

    if args.command == "batch":
        if not args.ticker:
            print("Error: tickers separados por coma (GGAL,YPF,TGS)")
            sys.exit(1)
        tickers = [t.strip().upper() for t in args.ticker.split(",")]
        results = client.get_transcripts_batch(tickers)

        if args.json:
            output = {t: tr.to_dict() if tr else None for t, tr in results.items()}
            print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
        else:
            for t, tr in results.items():
                if tr:
                    print_transcript(tr, args.full)
                else:
                    print(f"\n[ERROR] No transcript for {t}\n")
        return

    if args.command == "get":
        if not args.ticker:
            print("Error: Se requiere un ticker")
            sys.exit(1)
        tr = client.get_transcript(args.ticker, force_refresh=args.no_cache)

        if not tr:
            print(f"No se encontro transcript para {args.ticker.upper()}")
            sys.exit(1)

        if args.json:
            print(json.dumps(tr.to_dict(), indent=2, ensure_ascii=False, default=str))
        else:
            print_transcript(tr, args.full)


if __name__ == "__main__":
    main()
