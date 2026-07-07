"""
╔══════════════════════════════════════════════════════════════╗
║         LEXSPORT — CAS AWARD SCRAPER v1.0                   ║
║    Court of Arbitration for Sport — Full Archive Scraper     ║
║    Targets: tas-cas.org + jurisprudence.tas-cas.org          ║
╚══════════════════════════════════════════════════════════════╝

HOW TO RUN:
  pip install requests beautifulsoup4 pypdf lxml sqlite3
  python cas_scraper.py

WHAT IT DOES:
  1. Scrapes all CAS award listings from tas-cas.org
  2. Downloads PDF of each award
  3. Extracts full text from PDF
  4. Stores in SQLite database (lexsport.db)
  5. Generates JSON index for the LexSport app
"""

import requests
import sqlite3
import json
import os
import time
import re
import hashlib
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# ── CONFIGURATION ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PDF_DIR = OUTPUT_DIR / "pdfs"
JSON_DIR = OUTPUT_DIR / "json"
DB_PATH = BASE_DIR / "database" / "lexsport.db"

PDF_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Polite scraping — wait between requests
DELAY_BETWEEN_REQUESTS = 2.0   # seconds
DELAY_BETWEEN_PAGES = 3.0      # seconds
MAX_RETRIES = 3

# ── CAS SOURCE URLS ────────────────────────────────────────────
CAS_SOURCES = {
    "main_jurisprudence": "https://www.tas-cas.org/en/jurisprudence/search-for-cas-awards.html",
    "jurisprudence_portal": "https://jurisprudence.tas-cas.org",
    "appeal_awards": "https://www.tas-cas.org/en/jurisprudence/cas-appeal-awards.html",
    "ordinary_awards": "https://www.tas-cas.org/en/jurisprudence/cas-ordinary-arbitration-awards.html",
    "advisory_opinions": "https://www.tas-cas.org/en/jurisprudence/advisory-opinions.html",
}

# ── DATABASE SETUP ─────────────────────────────────────────────
def init_database():
    """Initialize SQLite database with full schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS cas_awards (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number     TEXT UNIQUE,
            title           TEXT,
            year            INTEGER,
            sport           TEXT,
            parties         TEXT,
            claimant        TEXT,
            respondent      TEXT,
            award_type      TEXT,
            decision_date   TEXT,
            panel           TEXT,
            outcome         TEXT,
            summary         TEXT,
            full_text       TEXT,
            key_principles  TEXT,
            pdf_url         TEXT,
            pdf_path        TEXT,
            source_url      TEXT,
            scraped_at      TEXT,
            hash            TEXT
        );

        CREATE TABLE IF NOT EXISTS legal_principles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            award_id    INTEGER,
            principle   TEXT,
            category    TEXT,
            FOREIGN KEY (award_id) REFERENCES cas_awards(id)
        );

        CREATE TABLE IF NOT EXISTS sports_index (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sport   TEXT UNIQUE,
            count   INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS scrape_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at      TEXT,
            awards_found    INTEGER,
            awards_new      INTEGER,
            awards_failed   INTEGER,
            status      TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_case_number ON cas_awards(case_number);
        CREATE INDEX IF NOT EXISTS idx_year ON cas_awards(year);
        CREATE INDEX IF NOT EXISTS idx_sport ON cas_awards(sport);
        CREATE VIRTUAL TABLE IF NOT EXISTS cas_fts USING fts5(
            case_number, title, parties, summary, full_text, key_principles,
            content='cas_awards', content_rowid='id'
        );
    """)

    conn.commit()
    print(f"✓ Database initialized at {DB_PATH}")
    return conn


# ── SCRAPER CORE ───────────────────────────────────────────────
def fetch_page(url, retries=MAX_RETRIES):
    """Fetch a URL with retry logic and polite delays."""
    for attempt in range(retries):
        try:
            time.sleep(DELAY_BETWEEN_REQUESTS)
            response = SESSION.get(url, timeout=15)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  ⚠ Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  ⚠ HTTP {response.status_code} for {url}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed (attempt {attempt+1}): {e}")
            time.sleep(5 * (attempt + 1))
    return None


def download_pdf(url, case_number):
    """Download a CAS award PDF."""
    safe_name = re.sub(r'[^\w\-_]', '_', case_number)
    pdf_path = PDF_DIR / f"{safe_name}.pdf"

    if pdf_path.exists():
        print(f"  → PDF already exists: {safe_name}.pdf")
        return str(pdf_path)

    response = fetch_page(url)
    if response and response.headers.get('content-type', '').startswith('application/pdf'):
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"  ✓ Downloaded: {safe_name}.pdf ({len(response.content)//1024}KB)")
        return str(pdf_path)

    print(f"  ✗ Failed to download PDF: {url}")
    return None


def extract_pdf_text(pdf_path):
    """Extract full text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text.strip())
        full_text = "\n\n".join(text_parts)
        return full_text[:50000]  # Cap at 50K chars per award
    except Exception as e:
        print(f"  ✗ PDF extraction error: {e}")
        return ""


def parse_case_number(text):
    """Extract CAS case number from text."""
    patterns = [
        r'CAS\s+\d{4}/[A-Z]+/\d+',
        r'CAS\s+\d{4}/[A-Z]\s*\d+',
        r'TAS\s+\d{4}/[A-Z]+/\d+',
        r'CAS\s+OG\s+\d+/\d+',
        r'CAS\s+ADD\s+\d+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return None


def parse_year(text):
    """Extract year from case number or text."""
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return int(match.group(0)) if match else None


def detect_sport(text):
    """Detect sport from case text."""
    text_lower = text.lower()
    sports = {
        "Football/Soccer": ["football", "soccer", "fifa", "uefa", "premier league", "la liga", "bundesliga", "serie a", "transfer", "footballer"],
        "Athletics": ["athletics", "track", "field", "iaaf", "world athletics", "runner", "sprinter", "marathon"],
        "Swimming": ["swimming", "fina", "world aquatics", "swimmer", "pool"],
        "Cycling": ["cycling", "uci", "tour de france", "cyclist", "velodrome"],
        "Tennis": ["tennis", "itf", "atp", "wta", "wimbledon", "grand slam"],
        "Basketball": ["basketball", "fiba", "nba", "euroleague"],
        "Boxing/MMA": ["boxing", "mma", "ufc", "wbc", "wba", "ibf"],
        "Rugby": ["rugby", "world rugby", "rfu", "six nations"],
        "Cricket": ["cricket", "icc", "bcci", "test match"],
        "Golf": ["golf", "pga", "lpga", "r&a", "usga"],
        "Esports": ["esports", "e-sports", "gaming", "counter-strike", "league of legends"],
        "Anti-Doping": ["doping", "wada", "usada", "prohibited substance", "banned substance", "tue"],
        "Horse Racing": ["horse", "equestrian", "fei", "jockey", "racing"],
        "Winter Sports": ["skiing", "snowboard", "fis", "biathlon", "bobsled"],
        "Gymnastics": ["gymnastics", "fig", "gymnast"],
        "Volleyball": ["volleyball", "fivb"],
        "Handball": ["handball", "ihf"],
        "Ice Hockey": ["ice hockey", "iihf", "nhl"],
    }
    for sport, keywords in sports.items():
        if any(kw in text_lower for kw in keywords):
            return sport
    return "General Sports Law"


def extract_parties(text):
    """Extract claimant and respondent from case text."""
    lines = text.split('\n')[:30]

    parties_pattern = re.search(
        r'(?:between|Between)\s+(.+?)\s+(?:and|AND|v\.|vs\.)\s+(.+?)(?:\n|$)',
        ' '.join(lines[:10])
    )
    if parties_pattern:
        return parties_pattern.group(1).strip()[:200], parties_pattern.group(2).strip()[:200]

    v_pattern = re.search(r'(.+?)\s+v[s]?\.\s+(.+?)(?:\n|$)', ' '.join(lines[:5]))
    if v_pattern:
        return v_pattern.group(1).strip()[:200], v_pattern.group(2).strip()[:200]

    return "Unknown", "Unknown"


def extract_outcome(text):
    """Extract case outcome from text."""
    text_lower = text.lower()
    outcomes = {
        "Appeal Dismissed": ["appeal is dismissed", "appeal dismissed", "the appeal is rejected"],
        "Appeal Upheld": ["appeal is upheld", "appeal upheld", "appeal is partially upheld", "appeal is allowed"],
        "Sanction Reduced": ["sanction is reduced", "reduced to", "period of ineligibility is reduced"],
        "Sanction Increased": ["sanction is increased", "period increased"],
        "Sanction Annulled": ["sanction is annulled", "decision is annulled", "set aside"],
        "Settlement": ["settled", "settlement", "withdrawn"],
        "Award in Favour": ["in favour of the appellant", "in favor of the appellant"],
        "No Jurisdiction": ["no jurisdiction", "lack of jurisdiction", "inadmissible"],
    }
    for outcome, signals in outcomes.items():
        if any(signal in text_lower for signal in signals):
            return outcome
    return "See Full Decision"


def generate_summary(text, case_number, sport):
    """Generate a structured summary from case text."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    meaningful = [l for l in lines if len(l) > 40][:15]
    intro = " ".join(meaningful[:5])[:500]

    return {
        "case": case_number,
        "sport": sport,
        "intro": intro,
        "total_pages_extracted": len(text) // 2000 + 1,
    }


def extract_key_principles(text):
    """Extract key legal principles from case text."""
    text_lower = text.lower()
    principles = []

    legal_signals = [
        ("Just Cause", ["just cause", "termination with just cause"]),
        ("Overdue Payables", ["overdue payable", "unpaid salary", "salary arrears"]),
        ("Training Compensation", ["training compensation", "art. 20", "article 20"]),
        ("Solidarity Contribution", ["solidarity contribution", "art. 21"]),
        ("Unilateral Termination", ["unilateral termination", "article 17", "art. 17"]),
        ("Image Rights", ["image rights", "personality rights", "likeness"]),
        ("Doping Violation", ["anti-doping", "prohibited substance", "article 10"]),
        ("Proportionality", ["proportionality", "proportionate sanction"]),
        ("Due Process", ["due process", "right to be heard", "fair hearing"]),
        ("Transfer", ["transfer fee", "transfer agreement", "transfer window"]),
        ("Employment", ["employment contract", "employment relationship"]),
        ("Nationality", ["nationality", "eligibility", "change of association"]),
        ("Agent Regulations", ["agent", "intermediary", "representation"]),
        ("TPO", ["third party", "tpo", "third-party ownership"]),
        ("Jurisdiction", ["jurisdiction", "competence", "arbitration clause"]),
    ]

    for principle, signals in legal_signals:
        if any(signal in text_lower for signal in signals):
            principles.append(principle)

    return ", ".join(principles[:8]) if principles else "General Sports Law"


# ── MAIN SCRAPING LOGIC ────────────────────────────────────────

def scrape_cas_jurisprudence_portal(conn):
    """
    Primary scraper targeting the CAS jurisprudence search portal.
    Uses the search API if available, falls back to HTML parsing.
    """
    print("\n" + "="*60)
    print("  SCRAPING CAS JURISPRUDENCE PORTAL")
    print("="*60)

    awards_found = []

    # Try the jurisprudence search portal
    search_url = "https://jurisprudence.tas-cas.org/Shared%20Documents/Forms/AllItems.aspx"
    page = fetch_page(search_url)

    if page and page.status_code == 200:
        soup = BeautifulSoup(page.text, 'lxml')
        # Parse SharePoint-style document library
        links = soup.find_all('a', href=re.compile(r'\.pdf', re.I))
        print(f"  Found {len(links)} PDF links on portal")

        for link in links[:500]:  # Cap at 500 for initial run
            href = link.get('href', '')
            if not href.startswith('http'):
                href = urljoin(search_url, href)
            text = link.get_text(strip=True)
            case_num = parse_case_number(text) or parse_case_number(href)
            if case_num:
                awards_found.append({'url': href, 'case_number': case_num, 'title': text})
    else:
        print("  ⚠ Portal not directly accessible — using structured search")
        awards_found = generate_structured_search_targets()

    print(f"  Total targets: {len(awards_found)}")
    return awards_found


def generate_structured_search_targets():
    """
    Generate structured list of known CAS case URL patterns.
    CAS cases follow predictable URL patterns on their portal.
    """
    targets = []

    # Known CAS case number patterns from public records
    # Format: CAS YEAR/TYPE/NUMBER
    case_types = ['A', 'O', 'TAS', 'ADD', 'OG']
    base_url = "https://jurisprudence.tas-cas.org/Shared%20Documents/"

    # Build list of known high-profile cases + systematic coverage
    known_cases = [
        # Landmark cases
        {"case": "CAS 1986/A/001", "url": f"{base_url}1986_A_001.pdf", "sport": "General"},
        {"case": "CAS 1992/A/053", "url": f"{base_url}1992_A_053.pdf", "sport": "Football"},
        {"case": "CAS 2007/A/1298", "url": f"{base_url}2007_A_1298.pdf", "sport": "Football"},  # Webster
        {"case": "CAS 2008/A/1519", "url": f"{base_url}2008_A_1519.pdf", "sport": "Football"},  # Matuzalem
        {"case": "CAS 2009/A/1810", "url": f"{base_url}2009_A_1810.pdf", "sport": "Football"},  # Mutu
        {"case": "CAS 2011/A/2596", "url": f"{base_url}2011_A_2596.pdf", "sport": "Football"},
        {"case": "CAS 2013/A/3256", "url": f"{base_url}2013_A_3256.pdf", "sport": "Athletics"},
        {"case": "CAS 2016/A/4371", "url": f"{base_url}2016_A_4371.pdf", "sport": "Anti-Doping"},
        {"case": "CAS 2020/A/6785", "url": f"{base_url}2020_A_6785.pdf", "sport": "Football"},
        {"case": "CAS 2021/A/7577", "url": f"{base_url}2021_A_7577.pdf", "sport": "Anti-Doping"},
        {"case": "CAS 2022/A/8540", "url": f"{base_url}2022_A_8540.pdf", "sport": "Football"},
        {"case": "CAS 2023/A/9428", "url": f"{base_url}2023_A_9428.pdf", "sport": "Anti-Doping"},
        {"case": "CAS 2023/A/9672", "url": f"{base_url}2023_A_9672.pdf", "sport": "Football"},
        {"case": "CAS 2024/A/10012", "url": f"{base_url}2024_A_10012.pdf", "sport": "Football"},
    ]

    # Generate systematic coverage: 2010-2024, 100 cases per year
    for year in range(2010, 2025):
        for num in range(1, 101):
            case_num = f"CAS {year}/A/{num:04d}"
            url = f"{base_url}{year}_A_{num:04d}.pdf"
            targets.append({
                "case_number": case_num,
                "url": url,
                "title": case_num
            })

    # Add the known landmark cases
    for kc in known_cases:
        targets.insert(0, {
            "case_number": kc["case"],
            "url": kc["url"],
            "title": kc["case"]
        })

    return targets


def scrape_alternative_sources(conn):
    """
    Scrape alternative free sources when CAS portal is blocked.
    Includes: OpenAlex, SSRN, Google Scholar (via structured queries)
    """
    print("\n" + "="*60)
    print("  SCRAPING ALTERNATIVE FREE SOURCES")
    print("="*60)

    sources = [
        {
            "name": "World Athletics Decisions",
            "url": "https://www.worldathletics.org/about-iaaf/documents/anti-doping",
            "type": "anti-doping"
        },
        {
            "name": "UEFA Disciplinary",
            "url": "https://www.uefa.com/insideuefa/about-uefa/legal/disciplinary/",
            "type": "football"
        },
        {
            "name": "WADA Decisions",
            "url": "https://www.wada-ama.org/en/anti-doping-database",
            "type": "anti-doping"
        },
        {
            "name": "FIFA TMS Decisions",
            "url": "https://www.fifa.com/legal/football-regulatory-documents",
            "type": "football"
        },
    ]

    results = []
    for source in sources:
        print(f"\n  Trying: {source['name']}...")
        page = fetch_page(source['url'])
        if page and page.status_code == 200:
            soup = BeautifulSoup(page.text, 'lxml')
            pdf_links = soup.find_all('a', href=re.compile(r'\.(pdf|PDF)$'))
            doc_links = soup.find_all('a', href=re.compile(r'decision|ruling|award', re.I))
            all_links = pdf_links + doc_links
            print(f"  ✓ Found {len(all_links)} documents")
            for link in all_links[:50]:
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = urljoin(source['url'], href)
                results.append({
                    'url': href,
                    'title': link.get_text(strip=True)[:200],
                    'source': source['name'],
                    'type': source['type'],
                })
        else:
            print(f"  ✗ Could not access {source['name']}")

    return results


def process_and_store_award(conn, case_data):
    """Process a CAS award and store in database."""
    c = conn.cursor()

    case_number = case_data.get('case_number', '')
    url = case_data.get('url', '')
    title = case_data.get('title', case_number)

    # Check if already in database
    existing = c.execute("SELECT id FROM cas_awards WHERE case_number = ?", (case_number,)).fetchone()
    if existing:
        return False, "already_exists"

    # Download PDF if URL is a PDF
    full_text = ""
    pdf_path = None

    if url.endswith('.pdf') or 'pdf' in url.lower():
        pdf_path = download_pdf(url, case_number)
        if pdf_path:
            full_text = extract_pdf_text(pdf_path)

    if not full_text:
        # Try fetching as HTML
        page = fetch_page(url)
        if page and page.status_code == 200:
            soup = BeautifulSoup(page.text, 'lxml')
            full_text = soup.get_text(separator='\n', strip=True)[:30000]

    if not full_text:
        return False, "no_content"

    # Extract metadata
    sport = detect_sport(full_text or title)
    year = parse_year(case_number) or parse_year(title)
    claimant, respondent = extract_parties(full_text)
    outcome = extract_outcome(full_text)
    key_principles = extract_key_principles(full_text)
    summary = json.dumps(generate_summary(full_text, case_number, sport))

    # Determine award type
    award_type = "Appeal" if "/A/" in case_number else \
                 "Ordinary" if "/O/" in case_number else \
                 "Anti-Doping" if "/ADD/" in case_number else \
                 "Olympic" if "/OG/" in case_number else "General"

    # Hash for deduplication
    content_hash = hashlib.md5((case_number + full_text[:500]).encode()).hexdigest()

    try:
        c.execute("""
            INSERT INTO cas_awards
            (case_number, title, year, sport, parties, claimant, respondent,
             award_type, outcome, summary, full_text, key_principles,
             pdf_url, pdf_path, source_url, scraped_at, hash)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            case_number,
            title[:500],
            year,
            sport,
            f"{claimant} v. {respondent}",
            claimant[:500],
            respondent[:500],
            award_type,
            outcome,
            summary,
            full_text,
            key_principles,
            url,
            pdf_path or "",
            url,
            datetime.now().isoformat(),
            content_hash
        ))

        award_id = c.lastrowid

        # Update FTS index
        c.execute("""
            INSERT INTO cas_fts(rowid, case_number, title, parties, summary, full_text, key_principles)
            VALUES (?,?,?,?,?,?,?)
        """, (award_id, case_number, title, f"{claimant} v. {respondent}", summary, full_text[:5000], key_principles))

        # Update sports index
        c.execute("""
            INSERT INTO sports_index (sport, count) VALUES (?, 1)
            ON CONFLICT(sport) DO UPDATE SET count = count + 1
        """, (sport,))

        conn.commit()
        print(f"  ✓ Stored: {case_number} | {sport} | {outcome}")
        return True, "success"

    except sqlite3.IntegrityError:
        return False, "duplicate"
    except Exception as e:
        print(f"  ✗ DB error: {e}")
        return False, str(e)


def export_json_index(conn):
    """Export searchable JSON index for LexSport app."""
    c = conn.cursor()

    # Main index
    awards = c.execute("""
        SELECT case_number, title, year, sport, parties, award_type,
               outcome, key_principles, summary
        FROM cas_awards
        ORDER BY year DESC, case_number ASC
    """).fetchall()

    index = []
    for row in awards:
        case_num, title, year, sport, parties, award_type, outcome, principles, summary_json = row
        try:
            summary = json.loads(summary_json) if summary_json else {}
        except:
            summary = {}
        index.append({
            "case": case_num,
            "title": title,
            "year": year,
            "sport": sport,
            "parties": parties,
            "type": award_type,
            "outcome": outcome,
            "principles": principles.split(", ") if principles else [],
            "intro": summary.get("intro", "")[:300],
        })

    index_path = JSON_DIR / "cas_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump({"total": len(index), "updated": datetime.now().isoformat(), "awards": index}, f, indent=2, ensure_ascii=False)

    # Stats by sport
    stats = c.execute("SELECT sport, count FROM sports_index ORDER BY count DESC").fetchall()
    stats_path = JSON_DIR / "sports_stats.json"
    with open(stats_path, 'w') as f:
        json.dump({"sports": [{"sport": s, "count": n} for s, n in stats]}, f, indent=2)

    print(f"\n✓ JSON index exported: {len(index)} awards → {index_path}")
    print(f"✓ Stats exported → {stats_path}")
    return index_path


def run_scraper(max_awards=500, start_year=2015, end_year=2025):
    """Main scraper entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         LEXSPORT CAS SCRAPER — Starting Run                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    print(f"  Target: {max_awards} awards | Years: {start_year}–{end_year}")
    print(f"  Database: {DB_PATH}")
    print(f"  PDFs: {PDF_DIR}")
    print()

    conn = init_database()
    start_time = datetime.now()

    # 1. Get award targets
    print("STEP 1: Finding CAS award targets...")
    targets = scrape_cas_jurisprudence_portal(conn)

    # Filter by year
    filtered = []
    for t in targets:
        year = parse_year(t.get('case_number', ''))
        if year and start_year <= year <= end_year:
            filtered.append(t)
        elif not year:
            filtered.append(t)  # Include if year unknown

    filtered = filtered[:max_awards]
    print(f"  → {len(filtered)} targets after filtering")

    # 2. Process each award
    print(f"\nSTEP 2: Processing {len(filtered)} awards...")
    found = new = failed = 0

    for i, target in enumerate(filtered, 1):
        case_num = target.get('case_number', f'UNKNOWN_{i}')
        print(f"\n[{i}/{len(filtered)}] {case_num}")

        success, reason = process_and_store_award(conn, target)
        found += 1
        if success:
            new += 1
        elif reason == "already_exists":
            print(f"  → Already in database, skipping")
        else:
            failed += 1

        # Polite delay between pages
        if i % 10 == 0:
            time.sleep(DELAY_BETWEEN_PAGES)
            print(f"\n  === Progress: {i}/{len(filtered)} | New: {new} | Failed: {failed} ===\n")

    # 3. Try alternative sources
    print("\nSTEP 3: Scraping alternative sources...")
    alt_sources = scrape_alternative_sources(conn)
    print(f"  → Found {len(alt_sources)} documents from alternative sources")

    # 4. Export JSON index
    print("\nSTEP 4: Exporting JSON index...")
    export_json_index(conn)

    # 5. Log run
    duration = (datetime.now() - start_time).seconds
    c = conn.cursor()
    c.execute("""
        INSERT INTO scrape_log (run_at, awards_found, awards_new, awards_failed, status)
        VALUES (?,?,?,?,?)
    """, (datetime.now().isoformat(), found, new, failed, "completed"))
    conn.commit()

    # Summary
    total_in_db = c.execute("SELECT COUNT(*) FROM cas_awards").fetchone()[0]

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    SCRAPE COMPLETE                           ║
╠══════════════════════════════════════════════════════════════╣
║  Awards processed:  {found:<38} ║
║  New awards stored: {new:<38} ║
║  Failed:            {failed:<38} ║
║  Total in database: {total_in_db:<38} ║
║  Duration:          {duration}s{'':<37}║
╚══════════════════════════════════════════════════════════════╝
    """)

    conn.close()
    return {"found": found, "new": new, "failed": failed, "total": total_in_db}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LexSport CAS Award Scraper")
    parser.add_argument("--max", type=int, default=500, help="Max awards to process")
    parser.add_argument("--start-year", type=int, default=2015, help="Start year")
    parser.add_argument("--end-year", type=int, default=2025, help="End year")
    args = parser.parse_args()

    run_scraper(max_awards=args.max, start_year=args.start_year, end_year=args.end_year)
