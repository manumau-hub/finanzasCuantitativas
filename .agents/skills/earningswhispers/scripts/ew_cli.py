#!/usr/bin/env python3
"""
EarningsWhispers CLI — Earnings Transcripts para ADRs Argentinos.

Uso:
    python ew_cli.py get GGAL              # Ultimo transcript
    python ew_cli.py get GGAL --json       # Output JSON
    python ew_cli.py get GGAL --full       # Texto completo
    python ew_cli.py batch GGAL,YPF,TGS    # Multiples tickers
    python ew_cli.py info GGAL             # Info empresa
    python ew_cli.py list                  # Tickers disponibles
"""

from ew_client import main

if __name__ == "__main__":
    main()
