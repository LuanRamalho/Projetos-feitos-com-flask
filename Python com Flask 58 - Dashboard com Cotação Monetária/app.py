from __future__ import annotations

import os
import platform
import threading
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

import psutil
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

API_BASE = os.getenv("FX_API_BASE", "https://api.frankfurter.dev/v2").rstrip("/")
BASE_CURRENCY = os.getenv("FX_BASE", "EUR").upper()
QUOTE_CURRENCIES = [
    code.strip().upper()
    for code in os.getenv("FX_QUOTES", "USD,BRL,GBP,JPY,CHF,CAD,AUD,ARS,MXN,CLP").split(",")
    if code.strip()
]
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "20"))

CURRENCY_NAMES = {
    "USD": "Dólar americano",
    "EUR": "Euro",
    "BRL": "Real brasileiro",
    "GBP": "Libra esterlina",
    "JPY": "Iene japonês",
    "CHF": "Franco suíço",
    "CAD": "Dólar canadense",
    "AUD": "Dólar australiano",
    "ARS": "Peso argentino",
    "MXN": "Peso mexicano",
    "CLP": "Peso chileno",
}

# Valores de fallback para o caso da API ficar fora do ar.
FALLBACK_RATES = {
    "USD": 1.08,
    "BRL": 6.15,
    "GBP": 0.86,
    "JPY": 163.20,
    "CHF": 0.94,
    "CAD": 1.47,
    "AUD": 1.65,
    "ARS": 1240.0,
    "MXN": 19.60,
    "CLP": 1090.0,
}

_cache_lock = threading.Lock()
_dashboard_cache: Dict[str, Any] = {"ts": 0.0, "data": None}


def _http_get(url: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    response = requests.get(
        url,
        params=params,
        timeout=12,
        headers={
            "User-Agent": "Mozilla/5.0 FinanceDashboard/1.0",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Resposta inválida da API")
    return data


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _human_delta(seconds: float) -> str:
    seconds = int(max(0, seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours:02d}h {minutes:02d}m"
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def _api_pair_rate(base: str, quote: str, day: date | None = None) -> float | None:
    url = f"{API_BASE}/rate/{base}/{quote}"
    params = {"date": day.isoformat()} if day else None
    try:
        payload = _http_get(url, params=params)
        if "rate" in payload:
            return _safe_float(payload.get("rate"))
        # Algumas respostas podem trazer conversão em campos alternativos.
        if "rates" in payload and isinstance(payload["rates"], dict):
            return _safe_float(payload["rates"].get(quote))
    except Exception:
        return None
    return None


def _fallback_snapshot() -> Dict[str, Any]:
    latest_day = date.today()
    quotes: List[Dict[str, Any]] = []
    for code in QUOTE_CURRENCIES:
        current = _safe_float(FALLBACK_RATES.get(code, 1.0))
        previous = current * 0.99
        change = current - previous
        change_pct = (change / previous) * 100 if previous else None
        quotes.append(
            {
                "code": code,
                "name": CURRENCY_NAMES.get(code, code),
                "rate": current,
                "previous_rate": previous,
                "change": change,
                "change_pct": change_pct,
                "trend": "up" if change > 0 else "down" if change < 0 else "flat",
            }
        )

    best_gainer = max(quotes, key=lambda q: q["change_pct"] or -10**9, default=None)
    worst_loser = min(quotes, key=lambda q: q["change_pct"] or 10**9, default=None)
    avg_change = sum((q["change_pct"] or 0) for q in quotes) / max(1, len(quotes))

    return {
        "base": BASE_CURRENCY,
        "base_name": CURRENCY_NAMES.get(BASE_CURRENCY, BASE_CURRENCY),
        "updated_at": latest_day.isoformat(),
        "source": "Fallback local",
        "source_detail": "API indisponível no momento",
        "quotes": quotes,
        "best_gainer": best_gainer,
        "worst_loser": worst_loser,
        "avg_change_pct": avg_change,
        "offline": True,
    }


def fetch_market_snapshot() -> Dict[str, Any]:
    params = {"base": BASE_CURRENCY, "quotes": ",".join(QUOTE_CURRENCIES)}
    try:
        payload = _http_get(f"{API_BASE}/rates", params=params)
        latest_date_raw = payload.get("date")
        latest_day = date.fromisoformat(latest_date_raw) if latest_date_raw else date.today()
        latest_rates = payload.get("rates", {})

        quotes: List[Dict[str, Any]] = []
        for code in QUOTE_CURRENCIES:
            current = _safe_float(latest_rates.get(code))
            previous = _api_pair_rate(BASE_CURRENCY, code, latest_day - timedelta(days=1))

            # tenta alguns dias anteriores caso o último dia útil não exista
            if previous is None:
                for offset in range(2, 11):
                    previous = _api_pair_rate(BASE_CURRENCY, code, latest_day - timedelta(days=offset))
                    if previous is not None:
                        break

            change = None if previous is None else current - previous
            change_pct = None if previous in (None, 0) else (change / previous) * 100

            quotes.append(
                {
                    "code": code,
                    "name": CURRENCY_NAMES.get(code, code),
                    "rate": current,
                    "previous_rate": previous,
                    "change": change,
                    "change_pct": change_pct,
                    "trend": "up" if (change or 0) > 0 else "down" if (change or 0) < 0 else "flat",
                }
            )

        gainers = sorted([q for q in quotes if q["change_pct"] is not None], key=lambda q: q["change_pct"], reverse=True)
        losers = sorted([q for q in quotes if q["change_pct"] is not None], key=lambda q: q["change_pct"])

        best_gainer = gainers[0] if gainers else None
        worst_loser = losers[0] if losers else None
        avg_change = sum((q["change_pct"] or 0) for q in quotes if q["change_pct"] is not None) / max(
            1, len([q for q in quotes if q["change_pct"] is not None])
        )

        return {
            "base": BASE_CURRENCY,
            "base_name": CURRENCY_NAMES.get(BASE_CURRENCY, BASE_CURRENCY),
            "updated_at": latest_day.isoformat(),
            "source": "Frankfurter",
            "source_detail": "Taxas diárias de referência",
            "quotes": quotes,
            "best_gainer": best_gainer,
            "worst_loser": worst_loser,
            "avg_change_pct": avg_change,
            "offline": False,
        }
    except Exception:
        return _fallback_snapshot()


def fetch_system_snapshot() -> Dict[str, Any]:
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))
    net = psutil.net_io_counters()
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = (datetime.now() - boot_time).total_seconds()

    return {
        "platform": platform.platform(),
        "boot_time": boot_time.isoformat(timespec="seconds"),
        "uptime": _human_delta(uptime_seconds),
        "cpu": {
            "percent": cpu,
            "cores_logical": psutil.cpu_count(logical=True),
            "cores_physical": psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True),
        },
        "memory": {
            "percent": memory.percent,
            "used_gb": round(memory.used / (1024 ** 3), 2),
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
        },
        "disk": {
            "percent": disk.percent,
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
        },
        "network": {
            "sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
            "recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        },
    }


def get_dashboard_data() -> Dict[str, Any]:
    now = datetime.now().timestamp()
    with _cache_lock:
        if _dashboard_cache["data"] is not None and (now - _dashboard_cache["ts"]) < CACHE_TTL_SECONDS:
            return _dashboard_cache["data"]

    market = fetch_market_snapshot()
    system = fetch_system_snapshot()
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "cache_ttl_seconds": CACHE_TTL_SECONDS,
        "market": market,
        "system": system,
    }

    with _cache_lock:
        _dashboard_cache["ts"] = now
        _dashboard_cache["data"] = payload

    return payload


@app.route("/")
def index():
    return render_template("index.html", base_currency=BASE_CURRENCY, quote_currencies=QUOTE_CURRENCIES)


@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(get_dashboard_data())


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat(timespec="seconds")})


if __name__ == "__main__":
    app.run(debug=True)
