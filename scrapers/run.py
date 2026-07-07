#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          ██╗     ███████╗██╗  ██╗███████╗██████╗  ██████╗ ██████╗  ║
║          ██║     ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██╔═══██╗╚════██╗ ║
║          ██║     █████╗   ╚███╔╝ ███████╗██████╔╝██║   ██║ █████╔╝ ║
║          ██║     ██╔══╝   ██╔██╗ ╚════██║██╔═══╝ ██║   ██║ ╚═══██╗ ║
║          ███████╗███████╗██╔╝ ██╗███████║██║     ╚██████╔╝██████╔╝ ║
║          ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═════╝  ║
║                                                                      ║
║            AI Sports Law Platform — Data Layer v1.0                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

QUICK START:
    python run.py setup        # Install dependencies
    python run.py scrape       # Scrape CAS + Regulations
    python run.py serve        # Start RAG API server
    python run.py search "FIFA Art 17"  # Test a search
    python run.py stats        # Show database stats

FULL PIPELINE:
    python run.py all          # Setup + Scrape + Serve

CONNECT TO LEXSPORT APP:
    Once running on port 8000, update your LexSport React app
    to call http://localhost:8000/search?q=YOUR_QUERY
    instead of the Anthropic API directly for research queries.
"""

import sys
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
SCRAPERS_DIR = BASE_DIR / "scrapers"
PROCESSORS_DIR = BASE_DIR / "processors"

sys.path.insert(0, str(SCRAPERS_DIR))
sys.path.insert(0, str(PROCESSORS_DIR))


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║              LEXSPORT DATA LAYER — Command Center           ║
╚══════════════════════════════════════════════════════════════╝
""")


def cmd_setup():
    """Install all required packages."""
    print("Installing dependencies...")
    packages = [
        "requests",
        "beautifulsoup4",
        "pypdf",
        "lxml",
    ]
    for pkg in packages:
        result = subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages", "-q"],
                              capture_output=True)
        status = "✓" if result.returncode == 0 else "✗"
        print(f"  {status} {pkg}")
    print("\n✓ Setup complete!")


def cmd_scrape(max_awards=200, start_year=2018, end_year=2025):
    """Run all scrapers."""
    print("\n▶ Starting CAS Award Scraper...")
    from cas_scraper import run_scraper
    result = run_scraper(max_awards=max_awards, start_year=start_year, end_year=end_year)

    print("\n▶ Starting Regulations Scraper...")
    from regulations_scraper import run_regulations_scraper
    run_regulations_scraper()

    print("\n✓ All scraping complete!")
    return result


def cmd_serve(port=8000):
    """Start the RAG API server."""
    print(f"\n▶ Starting LexSport RAG Server on port {port}...")
    from rag_engine import run_api_server
    run_api_server(port=port)


def cmd_search(query):
    """Run a test search."""
    from rag_engine import LexSportRAG
    rag = LexSportRAG()
    result = rag.search(query)
    print("\n" + "="*60)
    print(f"QUERY: {result['query']}")
    print("="*60)
    print(result['answer'])
    print("\n--- SOURCES ---")
    for c in result['sources']['cases']:
        print(f"  [CAS] {c['case']} ({c['year']}) {c['sport']} — {c['outcome']}")
    for r in result['sources']['regulations']:
        print(f"  [REG] {r['title']} ({r['year']})")
    print(f"\nDatabase used: {result['db_used']}")


def cmd_stats():
    """Show database statistics."""
    from rag_engine import LexSportRAG
    import json
    rag = LexSportRAG()
    stats = rag.get_stats()
    print("\n═══ LEXSPORT DATABASE STATS ═══\n")
    print(f"  Total CAS Awards:    {stats.get('total_cases', 0):,}")
    print(f"  Total Regulations:   {stats.get('total_regulations', 0):,}")
    print("\n  Cases by Sport:")
    for sport, count in (stats.get('cases_by_sport') or {}).items():
        bar = "█" * min(count // 2, 30)
        print(f"    {sport:<30} {count:>4}  {bar}")
    print("\n  Cases by Year:")
    for year, count in (stats.get('cases_by_year') or {}).items():
        print(f"    {year}  {count:>4} awards")
    print("\n  Regulations by Body:")
    for body, count in (stats.get('regs_by_body') or {}).items():
        print(f"    {body:<25} {count} documents")


def cmd_morocco(mode="full", manual_path=None):
    """Run Morocco sports law scraper."""
    print("\n▶ Starting Morocco Sports Law Scraper 🇲🇦...")
    from morocco_scraper import run as run_morocco
    return run_morocco(mode=mode, manual_path=manual_path)


def cmd_gulf(country=None, manual_path=None):
    """Run Gulf States (Saudi/UAE/Qatar) football law scraper."""
    print("\n▶ Starting Gulf States Football Law Scraper 🇸🇦🇦🇪🇶🇦...")
    from gulf_scraper import run as run_gulf
    return run_gulf(country_filter=country, manual_path=manual_path)


def cmd_all():
    """Full pipeline: setup + scrape + morocco + gulf + serve."""
    cmd_setup()
    cmd_scrape()
    cmd_morocco()
    cmd_gulf()
    cmd_serve()


def show_help():
    print("""
USAGE: python run.py <command> [options]

COMMANDS:
  setup                        Install required Python packages
  scrape                       Run CAS + Regulations scrapers (global)
  scrape --max 1000            Scrape up to 1000 CAS awards
  scrape --years 2020-2025     Scrape specific year range
  morocco                      Run Morocco law scraper 🇲🇦
  morocco --mode cas-only      Morocco CAS cases only
  morocco --mode regs-only     Morocco regulations only
  morocco --manual /path       Process manually downloaded PDFs
  gulf                         Run Gulf scraper — Saudi+UAE+Qatar 🇸🇦🇦🇪🇶🇦
  gulf --country saudi         Saudi Arabia only
  gulf --country uae           UAE only
  gulf --country qatar         Qatar only
  gulf --manual /path          Process manually downloaded PDFs
  serve                        Start RAG API server (port 8000)
  serve --port 9000            Start on custom port
  search "your query"          Test a search query
  stats                        Show database statistics
  all                          Full pipeline (setup+scrape+morocco+serve)

EXAMPLES:
  python run.py setup
  python run.py scrape
  python run.py search "FIFA RSTP Article 17 unilateral termination"
  python run.py search "doping sanction first offense reduction"
  python run.py search "image rights football contract"
  python run.py stats
  python run.py serve

API ENDPOINTS (after serve):
  GET http://localhost:8000/search?q=FIFA+Art+17
  GET http://localhost:8000/cases?q=doping&sport=Tennis
  GET http://localhost:8000/regulations?q=WADA
  GET http://localhost:8000/stats
  GET http://localhost:8000/health

CONNECT TO LEXSPORT APP:
  In your LexSport React app, update the Case Research module
  to call your local API instead of direct Claude API:

  const res = await fetch('http://localhost:8000/search?q=' + encodeURIComponent(query))
  const data = await res.json()
  // data.answer = AI answer with real citations
  // data.sources.cases = [{case, year, sport, outcome}, ...]
  // data.sources.regulations = [{title, body, year}, ...]
""")


if __name__ == "__main__":
    print_banner()
    args = sys.argv[1:]

    if not args or args[0] == "help":
        show_help()
    elif args[0] == "setup":
        cmd_setup()
    elif args[0] == "scrape":
        max_awards = 200
        start_year = 2018
        end_year = 2025
        for i, arg in enumerate(args):
            if arg == "--max" and i+1 < len(args):
                max_awards = int(args[i+1])
            elif arg == "--years" and i+1 < len(args):
                parts = args[i+1].split("-")
                if len(parts) == 2:
                    start_year, end_year = int(parts[0]), int(parts[1])
        cmd_scrape(max_awards, start_year, end_year)
    elif args[0] == "serve":
        port = 8000
        for i, arg in enumerate(args):
            if arg == "--port" and i+1 < len(args):
                port = int(args[i+1])
        cmd_serve(port)
    elif args[0] == "search":
        query = " ".join(args[1:]) if len(args) > 1 else "FIFA RSTP Article 17"
        cmd_search(query)
    elif args[0] == "stats":
        cmd_stats()
    elif args[0] == "morocco":
        mode = "full"
        manual_path = None
        for i, arg in enumerate(args):
            if arg == "--mode" and i+1 < len(args):
                mode = args[i+1]
            elif arg == "--manual" and i+1 < len(args):
                manual_path = args[i+1]
        cmd_morocco(mode=mode, manual_path=manual_path)
    elif args[0] == "gulf":
        country = None
        manual_path = None
        for i, arg in enumerate(args):
            if arg == "--country" and i+1 < len(args):
                country = args[i+1]
            elif arg == "--manual" and i+1 < len(args):
                manual_path = args[i+1]
        cmd_gulf(country=country, manual_path=manual_path)
    elif args[0] == "all":
        cmd_all()
    else:
        print(f"Unknown command: {args[0]}")
        show_help()
