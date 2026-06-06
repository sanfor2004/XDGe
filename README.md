<p align="center">
  <img src="images/banner.png" width="100%" alt="XDGe Banner" />
</p>

# XDGe

An enterprise-grade, asynchronous web directory scanner and search engine dorking utility. Engineered with Python's `asyncio` framework for high-throughput concurrency, `aiohttp` for non-blocking network requests, and `rich` for an interactive CLI experience.

---

## How It Works

XDGe operates on two primary modes of discovery: **Asynchronous Directory Bruteforcing** and **Multi-Engine Search Dorking**.

### 1. Asynchronous Directory Bruteforcing
Instead of classic sequential scanning, XDGe utilizes `asyncio.Semaphore` to manage a configurable pool of concurrent HTTP/S connections.
* **Smart Concurrency:** Capable of executing hundreds of requests per second without depleting system sockets.
* **Evasion & Stealth:** Automatically rotates through a pool of realistic browser User-Agents and routes traffic via user-provided proxy lists (rotating proxies per request).
* **Robust Error Handling:** Connection timeouts, SSL handshake failures, and DNS resets are gracefully isolated so that a single network drop does not interrupt the scanner.

### 2. Multi-Engine Search Dorking
Retrieves public links matching custom queries using major search providers (Google, Bing, DuckDuckGo).
* **Automatic CAPTCHA / Rate-Limit Evasion:** Recognizes search-engine blockpages and automatically rotates to a secondary search provider.
* **Jittered Scheduling:** Employs a random delay (1.5s – 4.5s) between queries to blend with normal browser behavior.
* **Result Sanitization:** Dynamically parses search engine outputs, excludes platform-specific helper links, and extracts clean target URLs.

### 3. Interactive Wizard & CLI Mode
* Run it with zero arguments to launch an interactive setup wizard that guides you through wordlist choices, thread pools, and output locations.
* Pass CLI flags to instantly skip prompts and run automated scans in headless environments.

---

## Features

- **High-Performance Asynchronous I/O:** Powered by `asyncio` and `aiohttp`.
- **Stealth & Evasion:** Random User-Agent selection and proxy rotation.
- **Vulnerability-Specific Checks:** Built-in wordlists tailored for specific enterprise server tech (Apache, IIS, Tomcat, WebLogic, WebSphere, SharePoint).
- **Google, Bing, & DuckDuckGo Dorking:** Automated queries with self-healing rotation on rate limits.
- **Bespoke Multi-Format Reports:** Generates structured raw text lists, JSON payloads, CSV data sheets, and self-contained interactive Dark-Mode HTML reports.

---

## How to Setup

### Prerequisites
Make sure you have **Python 3.8 or higher** installed on your system.

### 1. Clone or Download the Repository
Extract the files into a directory of your choice.

### 2. Install Dependencies
Run the following command to install the required external libraries:
```bash
pip install -r requirements.txt
```
This will install:
* `aiohttp` (for non-blocking asynchronous HTTP operations)
* `rich` (for rendering beautiful terminal UI tables, progress bars, and prompt wizard panels)

---

## Usage

### Interactive Wizard
Simply execute the script with no options to initiate the configuration wizard:
```bash
python XDGe.py
```

### Command Line Interface (CLI)

Run a fast asynchronous directory scan with 100 concurrent workers using `HEAD` requests:
```bash
python XDGe.py -t https://target.com -T 100 -m HEAD
```

Run a custom wordlist scan using proxy rotation:
```bash
python XDGe.py -t https://target.com -w my_list.txt -p proxies.txt
```

Run a search dorking scan:
```bash
python XDGe.py -t https://target.com -d GODORKS.txt -e google
```

Export results in all available formats (JSON + CSV + HTML):
```bash
python XDGe.py -t https://target.com -f all
```

---

> **Disclaimer:** This tool is intended only for authorized security audits and educational research. Always obtain explicit permission before scanning target infrastructure.
