#!/usr/bin/env python3
"""
XDGe — Enterprise-Grade Web Directory Scanner & Dorking Engine
Author  : AhmedAbdelaziz.Reda
Version : 2.0.0
License : All Rights Reserved

Usage (interactive):
    python XDGe.py

Usage (CLI):
    python XDGe.py -t https://target.com -T 100 -f all -m HEAD
    python XDGe.py -t https://target.com -d GODORKS.txt -e bing
    python XDGe.py -t https://target.com -w my_list.txt -p proxies.txt
"""

# ─────────────────────────────────────────────────────────────────────────────
# § 1  IMPORTS & DEPENDENCY CHECK
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os
import re
import json
import csv
import time
import random
import asyncio
import argparse
import pathlib
from datetime import datetime
from urllib.parse import quote_plus

# Graceful dependency check — friendly message before crashing
_MISSING: list[str] = []

try:
    import aiohttp
except ImportError:
    _MISSING.append("aiohttp>=3.9.0")

try:
    from rich.console import Console
    # pyrefly: ignore [missing-import]
    from rich.table import Table
    # pyrefly: ignore [missing-import]
    from rich.progress import (
        Progress, SpinnerColumn, BarColumn,
        TextColumn, TimeElapsedColumn, MofNCompleteColumn,
    )
    # pyrefly: ignore [missing-import]
    from rich.panel import Panel
    # pyrefly: ignore [missing-import]
    from rich.prompt import Prompt, Confirm
    # pyrefly: ignore [missing-import]
    from rich import box
except ImportError:
    _MISSING.append("rich>=13.7.0")

if _MISSING:
    print("\n[XDGe] Missing required packages. Install them with:")
    print(f"  pip install {' '.join(_MISSING)}\n")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# § 2  CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

VERSION     = "2.0.0"
SCRIPT_DIR  = pathlib.Path(__file__).parent.resolve()
WORDLIST_DIR = SCRIPT_DIR / "xarWORD"

# ── Realistic browser User-Agent pool (20 entries) ────────────────────────────
USER_AGENTS: list[str] = [
    # Chrome / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Edge / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    # Chrome / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Safari / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    # Firefox / Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    # Firefox / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Firefox / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Safari / iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    # Chrome / iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.6367.88 Mobile/15E148 Safari/604.1",
    # Chrome / Android
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    # Safari / iPadOS
    "Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    # Opera / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
    # Opera / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
    # Vivaldi
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Vivaldi/6.7.3329.21",
    # ChromeOS
    "Mozilla/5.0 (X11; CrOS x86_64 15633.69.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.212 Safari/537.36",
    # Googlebot (blends with crawlers)
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    # Bingbot
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

# ── HTTP status → rich style mapping ─────────────────────────────────────────
STATUS_STYLES: dict[int, str] = {
    200: "bold green",    201: "green",         204: "green",
    206: "green",         301: "bold cyan",      302: "cyan",
    307: "cyan",          308: "cyan",           400: "yellow",
    401: "bold yellow",   403: "bold yellow",    405: "yellow",
    408: "dim yellow",    429: "bold red",        500: "bold red",
    502: "red",           503: "red",             504: "dim red",
}

# ── Search engine URL templates ───────────────────────────────────────────────
DORK_ENGINES: dict[str, str] = {
    "google": "https://www.google.com/search?q={query}&num=100&hl=en",
    "bing":   "https://www.bing.com/search?q={query}&count=50",
    "ddg":    "https://html.duckduckgo.com/html/?q={query}",
}

# ── URL extraction regex per engine ───────────────────────────────────────────
DORK_REGEX: dict[str, str] = {
    "google": r'<a href="/url\?q=(https?://[^&"]+)',
    "bing":   r'<cite[^>]*>(https?://[^<\s]+)',
    "ddg":    r'result__url[^>]*>\s*(https?://[^\s<]+)',
}

# ── Domains to filter from dork results ──────────────────────────────────────
DORK_FILTER: dict[str, list[str]] = {
    "google": ["support.google.com", "accounts.google.com", "policies.google.com"],
    "bing":   ["microsoft.com/en-us/servicesagreement", "go.microsoft.com"],
    "ddg":    ["duckduckgo.com"],
}

# ── Vulnerability wordlists ────────────────────────────────────────────────────
VULN_WORDLISTS: list[str] = [
    "apache.txt", "cgis.txt", "coldfusion.txt", "domino.txt",
    "fatwire.txt", "fatwire_pagenames.txt", "frontpage.txt",
    "iis.txt", "iplanet.txt", "jrun.txt", "netware.txt",
    "oas.txt", "sharepoint.txt", "sunas.txt", "tests.txt",
    "tomcat.txt", "vignette.txt", "weblogic.txt", "websphere.txt",
]

# ── General directory wordlists ────────────────────────────────────────────────
#    All paths are relative to WORDLIST_DIR.
#    Bug fix: was using raw integer index `z` instead of NOR[z].
#    Bug fix: "others\\common_pass" → "others/common_pass.txt" (added .txt).
NORMAL_WORDLISTS: list[str] = [
    "big.txt",
    "catala.txt",
    "euskera.txt",
    "extensions_common.txt",
    "indexes.txt",
    "common.txt",
    "mutations_common.txt",
    "small.txt",
    "spanish.txt",
    os.path.join("stress", "alphanum_case.txt"),
    os.path.join("stress", "alphanum_case_extra.txt"),
    os.path.join("stress", "char.txt"),
    os.path.join("stress", "doble_uri_hex.txt"),
    os.path.join("stress", "test_ext.txt"),
    os.path.join("stress", "unicode.txt"),
    os.path.join("stress", "uri_hex.txt"),
    os.path.join("others", "names.txt"),
    os.path.join("others", "common_pass.txt"),  # Bug fix: was "others\\common_pass"
]


# ─────────────────────────────────────────────────────────────────────────────
# § 3  RICH CONSOLE & I/O HELPERS
# ─────────────────────────────────────────────────────────────────────────────

console = Console()

# Thread-safe global result accumulator & live statistics
found_results: list[dict] = []
_stats: dict[str, float | int] = {
    "requests": 0,
    "found":    0,
    "errors":   0,
    "start_time": 0.0,
}


def _banner() -> None:
    """Render the XDGe ASCII art banner via rich."""
    now = datetime.now().strftime("%I:%M:%S %p")
    art = (
        "[bold cyan]██╗  ██╗██████╗  ██████╗ [/]\n"
        "[bold cyan]╚██╗██╔╝██╔══██╗██╔════╝ [/]\n"
        "[bold cyan] ╚███╔╝ ██║  ██║██║  ███╗[/]\n"
        "[bold cyan] ██╔██╗ ██║  ██║██║   ██║[/]\n"
        "[bold cyan]██╔╝ ██╗██████╔╝╚██████╔╝[/]\n"
        "[bold cyan]╚═╝  ╚═╝╚═════╝  ╚═════╝ [/]\n\n"
        "[bold magenta]██╗  ██╗ █████╗ ██████╗ [/]\n"
        "[bold magenta]╚██╗██╔╝██╔══██╗██╔══██╗[/]\n"
        "[bold magenta] ╚███╔╝ ███████║██████╔╝[/]\n"
        "[bold magenta] ██╔██╗ ██╔══██║██╔══██╗[/]\n"
        "[bold magenta]██╔╝ ██╗██║  ██║██║  ██║[/]\n"
        "[bold magenta]╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝[/]"
    )
    console.print(Panel.fit(
        art,
        subtitle=f"[dim]v{VERSION}  ·  AhmedAbdelaziz.Reda  ·  {now}[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))


def _save_data(data: str, filepath: pathlib.Path) -> None:
    """Append a discovered URL to a plain-text output file."""
    with open(filepath, "a", encoding="utf-8") as fh:
        fh.write(data + "\n")


def _count_lines(filepath: pathlib.Path) -> int:
    """Return the number of lines in a file — used for progress bar totals."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
            return sum(1 for _ in fh)
    except (OSError, IOError):
        return 0


def _load_proxies(proxy_file: str | None) -> list[str]:
    """
    Load an HTTP/SOCKS proxy list from a file.
    Format: one proxy per line, http:// or socks5:// prefix (auto-added if missing).
    """
    if not proxy_file:
        return []
    path = pathlib.Path(proxy_file)
    if not path.exists():
        console.print(f"[yellow]⚠ Proxy file not found: {proxy_file} — running without proxies[/yellow]")
        return []
    proxies: list[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            proxy = line.strip()
            if not proxy or proxy.startswith("#"):
                continue
            if not proxy.startswith(("http://", "https://", "socks4://", "socks5://")):
                proxy = "http://" + proxy
            proxies.append(proxy)
    console.print(f"[green]✔ Loaded {len(proxies)} proxies from {proxy_file}[/green]")
    return proxies


# ─────────────────────────────────────────────────────────────────────────────
# § 4  ASYNC HTTP CORE  (replaces synchronous UScanner)
# ─────────────────────────────────────────────────────────────────────────────

async def _scan_single(
    session:     "aiohttp.ClientSession",
    url:         str,
    semaphore:   asyncio.Semaphore,
    progress:    "Progress",
    task_id:     int,
    method:      str = "GET",
    proxy:       str | None = None,
    output_path: pathlib.Path | None = None,
) -> dict | None:
    """
    Fire one HTTP request against a single URL.

    Design:
    - Semaphore-constrained for concurrency control.
    - Random UA per request (stealth).
    - Optional per-request proxy rotation (stealth).
    - All exceptions silently consumed — scan must never halt on a single error.

    Bug fixes implemented here vs original UScanner():
    - REQ.getcode() used correctly (was `x.getcode()` — NameError).
    """
    async with semaphore:
        ua = random.choice(USER_AGENTS)
        headers = {
            "User-Agent":      ua,
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection":      "keep-alive",
        }
        result: dict | None = None
        try:
            _stats["requests"] += 1
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.request(
                method, url,
                headers=headers,
                proxy=proxy,
                timeout=timeout,
                allow_redirects=True,
                ssl=False,
            ) as resp:
                status  = resp.status           # Bug fix: was x.getcode() → NameError
                style   = STATUS_STYLES.get(status, "white")
                elapsed = time.monotonic() - _stats["start_time"]
                rps     = _stats["requests"] / elapsed if elapsed > 0 else 0.0

                if status == 404:
                    console.print(f"  [dim][404] {url}[/dim]")
                else:
                    console.print(
                        f"  [{style}][{status}][/{style}] {url}"
                        f"  [dim]{method} · {rps:.1f} req/s[/dim]"
                    )
                    result = {
                        "url":       url,
                        "status":    status,
                        "method":    method,
                        "ua":        ua,
                        "timestamp": datetime.now().isoformat(),
                    }
                    found_results.append(result)
                    _stats["found"] += 1
                    if output_path:
                        _save_data(url, output_path)

        except asyncio.TimeoutError:
            _stats["errors"] += 1
        except Exception:
            # Swallow all other connection errors (SSL, DNS, reset, etc.)
            _stats["errors"] += 1
        finally:
            progress.advance(task_id)

        return result


async def _run_wordlist(
    target:      str,
    wl_path:     pathlib.Path,
    label:       str,
    semaphore:   asyncio.Semaphore,
    proxies:     list[str],
    method:      str,
    progress:    "Progress",
    output_path: pathlib.Path | None,
) -> None:
    """
    Process one wordlist file against the target.

    Bug fixes vs original NormalScan / vulnScan / UserScan:
    - File opened by NOR[z] (correct filename), not by raw int `z`.
    - Single `for line in file` iterator — no inner readline() call that
      caused every other line to be skipped.
    - File handle always open when we read from it (was closed in UserScan).
    """
    total   = _count_lines(wl_path)
    task_id = progress.add_task(f"[cyan]{label}[/cyan]", total=total)

    connector = aiohttp.TCPConnector(limit=0, ssl=False, enable_cleanup_closed=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        batch: list = []
        try:
            with open(wl_path, "r", encoding="utf-8", errors="ignore") as wf:
                for line in wf:                          # ← Fix: single iterator
                    word = line.strip()
                    if not word or word.startswith("#"):
                        continue
                    url   = f"{target.rstrip('/')}/{word.lstrip('/')}"
                    proxy = random.choice(proxies) if proxies else None
                    batch.append(
                        _scan_single(session, url, semaphore, progress,
                                     task_id, method, proxy, output_path)
                    )
                    # Dispatch in batches of 500 to cap memory usage on huge lists
                    if len(batch) >= 500:
                        await asyncio.gather(*batch, return_exceptions=True)
                        batch.clear()
            if batch:
                await asyncio.gather(*batch, return_exceptions=True)

        except (OSError, IOError) as exc:
            console.print(f"[red]✗ Cannot open wordlist: {wl_path} — {exc}[/red]")
            progress.advance(task_id, total)


# ─────────────────────────────────────────────────────────────────────────────
# § 5  ASYNC SCAN ENGINES
# ─────────────────────────────────────────────────────────────────────────────

async def vuln_scan(
    target:      str,
    semaphore:   asyncio.Semaphore,
    proxies:     list[str],
    method:      str,
    progress:    "Progress",
    output_path: pathlib.Path | None,
) -> None:
    """Scan target against every vulnerability-specific wordlist."""
    console.print(Panel("[bold red]⚔  VULNERABILITY SCAN[/bold red]", border_style="red"))
    for wl_name in VULN_WORDLISTS:
        wl_path = WORDLIST_DIR / "vulns" / wl_name
        if not wl_path.exists():
            console.print(f"  [dim]⤷ Skipping (not found): {wl_name}[/dim]")
            continue
        await _run_wordlist(
            target, wl_path, wl_name,
            semaphore, proxies, method, progress, output_path,
        )


async def normal_scan(
    target:      str,
    semaphore:   asyncio.Semaphore,
    proxies:     list[str],
    method:      str,
    progress:    "Progress",
    output_path: pathlib.Path | None,
) -> None:
    """
    Scan target using the bundled general-purpose wordlists.
    Bug fix: paths now use NORMAL_WORDLISTS[i] not the raw int index i.
    """
    console.print(Panel("[bold blue]📂  DIRECTORY SCAN[/bold blue]", border_style="blue"))
    for wl_rel in NORMAL_WORDLISTS:
        wl_path = WORDLIST_DIR / wl_rel          # ← Fix: NOR[z] not z
        if not wl_path.exists():
            console.print(f"  [dim]⤷ Skipping (not found): {wl_rel}[/dim]")
            continue
        label = pathlib.Path(wl_rel).name
        await _run_wordlist(
            target, wl_path, label,
            semaphore, proxies, method, progress, output_path,
        )


async def user_scan(
    target:       str,
    wordlist_file: str,
    semaphore:    asyncio.Semaphore,
    proxies:      list[str],
    method:       str,
    progress:     "Progress",
    output_path:  pathlib.Path | None,
) -> None:
    """
    Scan using a user-supplied custom wordlist.
    Bug fix: was reading from USEFILE after the `with` block closed it.
    Now passes the open file handle path to _run_wordlist which opens it itself.
    """
    wl_path = pathlib.Path(wordlist_file)
    if not wl_path.exists():
        console.print(f"[red]✗ Custom wordlist not found: {wordlist_file}[/red]")
        return
    console.print(Panel(
        f"[bold green]📋  CUSTOM WORDLIST SCAN[/bold green]\n[dim]{wordlist_file}[/dim]",
        border_style="green",
    ))
    await _run_wordlist(
        target, wl_path, wl_path.name,
        semaphore, proxies, method, progress, output_path,
    )


# ─────────────────────────────────────────────────────────────────────────────
# § 6  DORK ENGINE  (multi-engine + jitter + CAPTCHA auto-fallback)
# ─────────────────────────────────────────────────────────────────────────────

def _is_captcha(html: str) -> bool:
    """Detect common CAPTCHA / rate-limit indicators in a search response."""
    signals = [
        "unusual traffic", "captcha", "recaptcha",
        "i'm not a robot", "please complete the security check",
        "automated queries", "sorrypage", "verify you are human",
    ]
    lower = html.lower()
    return any(s in lower for s in signals)


async def _fetch_dork_page(
    session: "aiohttp.ClientSession",
    url:     str,
    engine:  str,
) -> str:
    """Fetch one search-engine results page with a rotating UA."""
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent":      ua,
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer":         "https://www.google.com/" if engine == "google" else "",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get(url, headers=headers, timeout=timeout, ssl=False) as resp:
            if resp.status in (429, 503):
                return "__RATELIMIT__"
            return await resp.text(errors="ignore")
    except Exception:
        return ""


async def go_scan(
    target:      str,
    dork_file:   str,
    engine:      str = "google",
    output_path: pathlib.Path | None = None,
) -> None:
    """
    Dork scan with:
      - Multi-engine support (Google → Bing → DuckDuckGo)
      - Jittered sleep between requests (1.5 – 4.5 s)
      - Automatic engine rotation on CAPTCHA / rate-limit detection
    """
    dork_path = pathlib.Path(dork_file)
    if not dork_path.exists():
        console.print(f"[red]✗ Dork file not found: {dork_file}[/red]")
        return

    # Load dork entries
    dorks: list[str] = []
    with open(dork_path, "r", encoding="utf-8", errors="ignore") as df:
        for line in df:
            d = line.strip()
            if d and not d.startswith("#"):
                dorks.append(d)

    # Build ordered, deduplicated engine rotation sequence
    engine_order = [engine] + [e for e in ("google", "bing", "ddg") if e != engine]
    engine_idx   = 0
    active_engine = engine_order[engine_idx]

    console.print(Panel(
        f"[bold yellow]🔍  DORK SCAN[/bold yellow]\n"
        f"[dim]Target: {target}  |  "
        f"Engine: {active_engine.upper()}  |  "
        f"Dorks: {len(dorks)}[/dim]",
        border_style="yellow",
    ))

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        for idx, dork in enumerate(dorks, 1):
            query = quote_plus(f"site:{target} {dork}")
            url   = DORK_ENGINES[active_engine].format(query=query)

            console.print(
                f"  [yellow][{idx}/{len(dorks)}][/yellow]"
                f" [dim]{active_engine.upper()}:[/dim] {dork}"
            )
            html = await _fetch_dork_page(session, url, active_engine)

            # Switch engine on rate-limit / CAPTCHA
            if html == "__RATELIMIT__" or _is_captcha(html):
                engine_idx    = (engine_idx + 1) % len(engine_order)
                active_engine = engine_order[engine_idx]
                console.print(
                    f"  [red]⚠ Rate-limited! Switching → {active_engine.upper()}[/red]"
                )
                url  = DORK_ENGINES[active_engine].format(query=query)
                html = await _fetch_dork_page(session, url, active_engine)

            if html and html not in ("__RATELIMIT__", ""):
                pattern   = DORK_REGEX.get(active_engine, DORK_REGEX["google"])
                hits      = re.findall(pattern, html)
                blocklist = DORK_FILTER.get(active_engine, [])
                for hit in hits:
                    if any(b in hit for b in blocklist):
                        continue
                    console.print(f"    [bold green]✔[/bold green] {hit}")
                    result = {
                        "url":       hit,
                        "status":    "dork",
                        "method":    "DORK",
                        "ua":        "N/A",
                        "timestamp": datetime.now().isoformat(),
                    }
                    found_results.append(result)
                    if output_path:
                        go_out = output_path.parent / "GODATA_XAR.txt"
                        _save_data(hit, go_out)

            # Jittered sleep — prevents search engine rate limiting
            jitter = random.uniform(1.5, 4.5)
            await asyncio.sleep(jitter)


# ─────────────────────────────────────────────────────────────────────────────
# § 7  REPORT EXPORTER  (JSON / CSV / HTML)
# ─────────────────────────────────────────────────────────────────────────────

def _export_json(results: list[dict], base: str) -> None:
    path = pathlib.Path(base + ".json")
    payload = {
        "meta": {
            "tool":          "XDGe",
            "version":       VERSION,
            "generated":     datetime.now().isoformat(),
            "total_found":   len(results),
        },
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    console.print(f"  [green]✔ JSON  → {path}[/green]")


def _export_csv(results: list[dict], base: str) -> None:
    if not results:
        return
    path   = pathlib.Path(base + ".csv")
    fields = list(results[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    console.print(f"  [green]✔ CSV   → {path}[/green]")


# Self-contained dark-themed HTML report — zero external dependencies
_HTML_TMPL = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>XDGe Report — {target}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0d1117;color:#e6edf3;font-family:'Inter',sans-serif;min-height:100vh}}
  .hero{{background:linear-gradient(135deg,#0d1117 0%,#161b22 60%,#0d1117 100%);
         border-bottom:1px solid #30363d;padding:48px 40px 32px}}
  .hero h1{{font-size:1.9rem;font-weight:700;color:#58a6ff;letter-spacing:-.02em}}
  .hero p{{color:#8b949e;margin-top:8px;font-size:.88rem}}
  .stats{{display:flex;gap:20px;margin-top:24px;flex-wrap:wrap}}
  .stat{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px 24px}}
  .stat .n{{font-size:1.8rem;font-weight:700;color:#58a6ff}}
  .stat .l{{font-size:.78rem;color:#8b949e;margin-top:4px;text-transform:uppercase;letter-spacing:.06em}}
  main{{padding:32px 40px}}
  .toolbar{{display:flex;gap:12px;align-items:center;margin-bottom:20px;flex-wrap:wrap}}
  input#search{{background:#161b22;border:1px solid #30363d;border-radius:8px;
                padding:8px 14px;color:#e6edf3;font-size:.88rem;width:320px;outline:none;
                transition:border .15s ease}}
  input#search:focus{{border-color:#58a6ff}}
  .filters{{display:flex;gap:8px;flex-wrap:wrap}}
  .filter-btn{{background:#161b22;border:1px solid #30363d;border-radius:8px;
               padding:5px 14px;cursor:pointer;color:#8b949e;font-size:.82rem;
               transition:all .15s ease;font-family:'Inter',sans-serif}}
  .filter-btn:hover,.filter-btn.active{{border-color:#58a6ff;color:#58a6ff;background:#1c2333}}
  table{{width:100%;border-collapse:separate;border-spacing:0;
         background:#161b22;border:1px solid #30363d;border-radius:12px;overflow:hidden}}
  thead tr{{background:#21262d}}
  th{{padding:12px 16px;text-align:left;font-size:.75rem;font-weight:600;
      color:#8b949e;text-transform:uppercase;letter-spacing:.06em}}
  td{{padding:11px 16px;border-top:1px solid #21262d;font-size:.83rem}}
  td.url-cell{{font-family:'JetBrains Mono',monospace}}
  td.url-cell a{{color:#58a6ff;text-decoration:none}}
  td.url-cell a:hover{{text-decoration:underline}}
  tr:hover td{{background:rgba(88,166,255,.04)}}
  .badge{{display:inline-flex;align-items:center;border-radius:5px;
           padding:2px 9px;font-size:.76rem;font-weight:600;
           font-family:'Inter',sans-serif;letter-spacing:.02em}}
  .s200,.s201,.s204,.s206{{background:#132d1e;color:#3fb950}}
  .s301,.s302,.s307,.s308{{background:#0d2340;color:#58a6ff}}
  .s400,.s401,.s403,.s405{{background:#2e2006;color:#d29922}}
  .s500,.s502,.s503,.s504{{background:#2d0f0f;color:#f85149}}
  .sdork{{background:#1e0f2d;color:#bc8cff}}
  .method-badge{{background:#21262d;border-radius:4px;padding:1px 8px;
                  font-family:'JetBrains Mono',monospace;font-size:.76rem;color:#8b949e}}
  footer{{text-align:center;padding:32px;color:#484f58;font-size:.78rem;
           border-top:1px solid #21262d;margin-top:32px}}
</style>
</head>
<body>
<div class="hero">
  <h1>⚔ XDGe Scan Report</h1>
  <p>Target: <strong style="color:#e6edf3">{target}</strong> &nbsp;·&nbsp; Generated: {generated} &nbsp;·&nbsp; XDGe v{version}</p>
  <div class="stats">
    <div class="stat"><div class="n">{total}</div><div class="l">Total Found</div></div>
    <div class="stat"><div class="n">{ok200}</div><div class="l">200 OK</div></div>
    <div class="stat"><div class="n">{redirects}</div><div class="l">Redirects</div></div>
    <div class="stat"><div class="n">{forbidden}</div><div class="l">Forbidden</div></div>
    <div class="stat"><div class="n">{errors5xx}</div><div class="l">Server Errors</div></div>
    <div class="stat"><div class="n">{dorks}</div><div class="l">Dork Hits</div></div>
  </div>
</div>
<main>
  <div class="toolbar">
    <input id="search" placeholder="🔍  Filter by URL…" oninput="doFilter()">
    <div class="filters">
      <button class="filter-btn active" onclick="setFilter('all',this)">All</button>
      <button class="filter-btn" onclick="setFilter('2',this)">2xx</button>
      <button class="filter-btn" onclick="setFilter('3',this)">3xx</button>
      <button class="filter-btn" onclick="setFilter('4',this)">4xx</button>
      <button class="filter-btn" onclick="setFilter('5',this)">5xx</button>
      <button class="filter-btn" onclick="setFilter('dork',this)">Dork</button>
    </div>
  </div>
  <table id="rt">
    <thead>
      <tr><th>#</th><th>URL</th><th>Status</th><th>Method</th><th>Timestamp</th></tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
</main>
<footer>XDGe v{version} &nbsp;·&nbsp; {generated} &nbsp;·&nbsp; For authorised security testing only.</footer>
<script>
let _f='all';
function setFilter(f,btn){{
  _f=f;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  doFilter();
}}
function doFilter(){{
  const q=document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('#rt tbody tr').forEach(r=>{{
    const url=r.cells[1].innerText.toLowerCase();
    const st=r.dataset.status;
    const mQ=url.includes(q);
    const mF=_f==='all'||(_f==='dork'?st==='dork':st.startsWith(_f));
    r.style.display=(mQ&&mF)?'':'none';
  }});
}}
</script>
</body>
</html>"""


def _export_html(results: list[dict], base: str, target: str) -> None:
    path  = pathlib.Path(base + ".html")
    rows: list[str] = []
    for i, r in enumerate(results, 1):
        status = str(r.get("status", ""))
        cls    = f"s{status}" if status not in ("", "dork") else "sdork"
        url    = r.get("url", "")
        method = r.get("method", "GET")
        ts     = r.get("timestamp", "")[:19].replace("T", " ")
        rows.append(
            f'      <tr data-status="{status}">'
            f'<td>{i}</td>'
            f'<td class="url-cell"><a href="{url}" target="_blank" rel="noopener">{url}</a></td>'
            f'<td><span class="badge {cls}">{status}</span></td>'
            f'<td><span class="method-badge">{method}</span></td>'
            f'<td>{ts}</td>'
            f'</tr>'
        )
    counts = {
        "total":    len(results),
        "ok200":    sum(1 for r in results if str(r.get("status","")).startswith("2")),
        "redirects":sum(1 for r in results if str(r.get("status","")).startswith("3")),
        "forbidden":sum(1 for r in results if str(r.get("status","")) in ("401","403")),
        "errors5xx":sum(1 for r in results if str(r.get("status","")).startswith("5")),
        "dorks":    sum(1 for r in results if r.get("method") == "DORK"),
    }
    html = _HTML_TMPL.format(
        target=target,
        generated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        version=VERSION,
        rows="\n".join(rows),
        **counts,
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    console.print(f"  [green]✔ HTML  → {path}[/green]")


def export_reports(
    results:  list[dict],
    fmt:      str,
    base:     str,
    target:   str,
) -> None:
    """Dispatch export to requested format(s)."""
    if not results:
        console.print("[yellow]⚠ No results to export.[/yellow]")
        return
    console.print(Panel("[bold]📊  EXPORTING REPORTS[/bold]", border_style="cyan"))
    if fmt in ("json", "all"):
        _export_json(results, base)
    if fmt in ("csv", "all"):
        _export_csv(results, base)
    if fmt in ("html", "all"):
        _export_html(results, base, target)


# ─────────────────────────────────────────────────────────────────────────────
# § 8  RICH SUMMARY TABLE
# ─────────────────────────────────────────────────────────────────────────────

def _print_summary(results: list[dict]) -> None:
    """Print a rich-formatted results table after the scan completes."""
    if not results:
        console.print("[yellow]No resources discovered.[/yellow]")
        return

    table = Table(
        title="[bold cyan]⚔  XDGe — Discovered Resources[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=False,
        header_style="bold cyan",
        expand=True,
    )
    table.add_column("#",        style="dim",   width=5,  justify="right")
    table.add_column("Status",                  width=8,  justify="center")
    table.add_column("Method",                  width=7,  justify="center")
    table.add_column("URL",      style="cyan",  ratio=1,  no_wrap=False)
    table.add_column("Time",     style="dim",   width=20)

    for i, r in enumerate(results, 1):
        status = r.get("status", "?")
        style  = STATUS_STYLES.get(status, "white") if isinstance(status, int) else "magenta"
        table.add_row(
            str(i),
            f"[{style}]{status}[/{style}]",
            r.get("method", "GET"),
            r.get("url", ""),
            r.get("timestamp", "")[:19].replace("T", " "),
        )
    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# § 9  CLI ARGUMENT PARSER & ASYNC MAIN
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="XDGe",
        description=f"XDGe v{VERSION} — Enterprise Web Directory Scanner & Dorking Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python XDGe.py                                          # Interactive wizard
  python XDGe.py -t https://target.com                   # Quick async scan
  python XDGe.py -t https://target.com -T 100 -m HEAD   # 100-thread HEAD scan
  python XDGe.py -t https://target.com -f all            # JSON + CSV + HTML output
  python XDGe.py -t https://target.com -d GODORKS.txt -e bing
  python XDGe.py -t https://target.com -w wordlist.txt -p proxies.txt
        """,
    )
    p.add_argument("--target",   "-t",
                   help="Target URL (e.g. https://example.com)")
    p.add_argument("--threads",  "-T", type=int, default=50,
                   help="Max concurrent requests  [default: 50]")
    p.add_argument("--wordlist", "-w",
                   help="Custom wordlist path (skips built-in lists)")
    p.add_argument("--proxies",  "-p",
                   help="Proxy list file (one per line, http:// or socks5://)")
    p.add_argument("--output",   "-o",
                   help="Output base path (auto-named with timestamp if omitted)")
    p.add_argument("--format",   "-f",
                   choices=["json", "csv", "html", "all"], default="json",
                   help="Export format  [default: json]")
    p.add_argument("--method",   "-m",
                   choices=["GET", "HEAD", "POST"], default="GET",
                   help="HTTP method  [default: GET]")
    p.add_argument("--engine",   "-e",
                   choices=["google", "bing", "ddg"], default="google",
                   help="Dork search engine  [default: google]")
    p.add_argument("--dorks",    "-d",
                   help="Dork list file path")
    p.add_argument("--no-vuln",  action="store_true",
                   help="Skip vulnerability wordlist scan")
    p.add_argument("--no-scan",  action="store_true",
                   help="Skip directory wordlist scan")
    return p


async def _async_main(
    target:      str,
    threads:     int,
    wordlist:    str | None,
    proxies:     list[str],
    output_base: str,
    fmt:         str,
    method:      str,
    engine:      str,
    dorks_file:  str | None,
    run_vuln:    bool,
    run_scan:    bool,
) -> None:
    """Top-level async orchestrator — runs all scan modules in sequence."""
    _stats["start_time"] = time.monotonic()
    output_path = pathlib.Path(output_base + ".txt")
    semaphore   = asyncio.Semaphore(threads)

    console.print(Panel(
        f"[bold]Target :[/bold] [cyan]{target}[/cyan]\n"
        f"[bold]Threads:[/bold] [cyan]{threads}[/cyan]  ·  "
        f"[bold]Method :[/bold] [cyan]{method}[/cyan]  ·  "
        f"[bold]Proxies:[/bold] [cyan]{len(proxies)}[/cyan]  ·  "
        f"[bold]Export :[/bold] [cyan]{fmt.upper()}[/cyan]  ·  "
        f"[bold]Output :[/bold] [cyan]{output_base}.*[/cyan]",
        title="[bold cyan]⚔  XDGe — Configuration[/bold cyan]",
        border_style="cyan",
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=28),
        MofNCompleteColumn(),
        TextColumn("[cyan]{task.speed:.0f}[/cyan] [dim]r/s[/dim]"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:

        if wordlist:
            # User-supplied wordlist overrides built-in lists
            await user_scan(target, wordlist, semaphore, proxies,
                            method, progress, output_path)
        else:
            if run_vuln:
                await vuln_scan(target, semaphore, proxies,
                                method, progress, output_path)
            if run_scan:
                await normal_scan(target, semaphore, proxies,
                                  method, progress, output_path)

        if dorks_file:
            await go_scan(target, dorks_file, engine, output_path)

    # ── Final statistics banner ──────────────────────────────────────────
    elapsed = time.monotonic() - _stats["start_time"]
    rps     = _stats["requests"] / elapsed if elapsed > 0 else 0.0
    console.print(Panel(
        f"[bold green]✔ Scan complete[/bold green]\n"
        f"Requests : [cyan]{_stats['requests']}[/cyan]  |  "
        f"Found : [green]{_stats['found']}[/green]  |  "
        f"Errors : [red]{_stats['errors']}[/red]  |  "
        f"Speed : [cyan]{rps:.1f} req/s[/cyan]  |  "
        f"Elapsed : [dim]{elapsed:.1f}s[/dim]",
        border_style="green",
    ))

    _print_summary(found_results)
    export_reports(found_results, fmt, output_base, target)


def main() -> None:
    """Entry point — parse CLI args or launch interactive wizard."""
    _banner()
    parser = _build_parser()
    args   = parser.parse_args()

    # ── Resolve target ────────────────────────────────────────────────────
    target: str = args.target or ""
    if not target:
        target = Prompt.ask(
            "\n[cyan]»[/cyan] [bold]Target URL[/bold] "
            "[dim](e.g. https://example.com)[/dim]"
        )
    target = target.strip().rstrip("/")
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    # ── Resolve proxies ───────────────────────────────────────────────────
    proxies = _load_proxies(args.proxies)

    # ── Resolve output base path ──────────────────────────────────────────
    if args.output:
        output_base = args.output
    else:
        domain  = re.sub(r"https?://", "", target).split("/")[0].replace(":", "_")
        ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base = str(SCRIPT_DIR / f"xdge_{domain}_{ts}")

    # ── Resolve scan options (wizard when no --target flag) ───────────────
    wordlist:   str | None = args.wordlist
    run_vuln:   bool = not args.no_vuln
    run_scan:   bool = not args.no_scan
    dorks_file: str | None = args.dorks
    method:     str = args.method
    fmt:        str = args.format
    engine:     str = args.engine
    threads:    int = args.threads

    if not args.target:
        # Interactive wizard — only shown in zero-argument mode
        console.print()
        use_builtin = Confirm.ask(
            "[cyan]»[/cyan] Use built-in wordlists?", default=True
        )
        if not use_builtin:
            wordlist = Prompt.ask("[cyan]»[/cyan] Path to your custom wordlist")
            run_vuln = False
            run_scan = False

        use_dorks = Confirm.ask(
            "[cyan]»[/cyan] Run Google Dork scan?", default=False
        )
        if use_dorks:
            dorks_file = Prompt.ask(
                "[cyan]»[/cyan] Path to dork list",
                default=str(SCRIPT_DIR / "GODORKS.txt"),
            )
            engine = Prompt.ask(
                "[cyan]»[/cyan] Search engine",
                choices=["google", "bing", "ddg"],
                default="google",
            )

        method = Prompt.ask(
            "[cyan]»[/cyan] HTTP method",
            choices=["GET", "HEAD", "POST"],
            default="GET",
        )
        fmt = Prompt.ask(
            "[cyan]»[/cyan] Export format",
            choices=["json", "csv", "html", "all"],
            default="all",
        )
        threads_str = Prompt.ask(
            "[cyan]»[/cyan] Concurrent threads", default="50"
        )
        threads = int(threads_str) if threads_str.isdigit() else 50

        proxy_file = Prompt.ask(
            "[cyan]»[/cyan] Proxy list file [dim](Enter to skip)[/dim]",
            default="",
        )
        if proxy_file.strip():
            proxies = _load_proxies(proxy_file.strip())

    # ── Execute ───────────────────────────────────────────────────────────
    asyncio.run(_async_main(
        target=target,
        threads=threads,
        wordlist=wordlist,
        proxies=proxies,
        output_base=output_base,
        fmt=fmt,
        method=method,
        engine=engine,
        dorks_file=dorks_file,
        run_vuln=run_vuln,
        run_scan=run_scan,
    ))


if __name__ == "__main__":
    main()
