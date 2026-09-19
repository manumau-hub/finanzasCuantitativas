"""
Script auxiliar: genera superficie de volatilidad en subproceso aislado.
NO importa pandas. Lee chain desde CSV (escrito por el proceso principal).
Escribe raw.csv y surf.csv en el mismo directorio que el CSV de chain.
Uso: python _fetch_vol_surface.py CHAIN_CSV SPOT R DIV
Salida: RUTA_DIR|spot|r|div (4 líneas)
"""
import csv
import os
import sys
from pathlib import Path

root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, root)


def _write_dict_arrays_to_csv(path: str, d: dict) -> None:
    """Escribe dict de arrays a CSV sin pandas."""
    if not d:
        return
    keys = list(d.keys())
    n = len(d[keys[0]])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for i in range(n):
            row = {}
            for k in keys:
                v = d[k][i]
                if hasattr(v, "item"):
                    v = v.item()
                if isinstance(v, float) and v != v:  # NaN
                    v = ""
                row[k] = v
            w.writerow(row)


def main():
    if len(sys.argv) < 5:
        print("ERROR|Uso: _fetch_vol_surface.py CHAIN_CSV SPOT R DIV", file=sys.stderr)
        sys.exit(1)

    chain_csv = sys.argv[1]
    spot = float(sys.argv[2])
    r = float(sys.argv[3])
    div = float(sys.argv[4])

    if not os.path.isfile(chain_csv):
        print(f"ERROR|No existe: {chain_csv}", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(chain_csv))

    try:
        # Leer chain desde CSV (sin pandas)
        chain_rows = []
        with open(chain_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                chain_rows.append(dict(row))

        if not chain_rows:
            print("ERROR|Chain CSV vacío", file=sys.stderr)
            sys.exit(1)

        from Codigo.analytics.vol_surface import chain_to_raw_iv_data, gaussian_smooth

        raw = chain_to_raw_iv_data(chain_rows, spot, r, div)
        vs = gaussian_smooth()
        surf = vs.generate_volatility_surface(raw)

        raw_path = os.path.join(out_dir, "raw.csv")
        surf_path = os.path.join(out_dir, "surf.csv")
        _write_dict_arrays_to_csv(raw_path, raw)
        _write_dict_arrays_to_csv(surf_path, surf)

        print(out_dir)
        print(spot)
        print(r)
        print(div)
    except Exception as e:
        print(f"ERROR|{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
