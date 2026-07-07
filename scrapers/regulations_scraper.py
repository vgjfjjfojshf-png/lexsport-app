"""
╔══════════════════════════════════════════════════════════════╗
║     LEXSPORT — REGULATIONS SCRAPER v1.0                     ║
║    FIFA · WADA · UEFA · World Athletics · IOC               ║
╚══════════════════════════════════════════════════════════════╝

Scrapes all free sports law regulations from official bodies.
Run after cas_scraper.py to build the complete legal database.
"""

import requests
import sqlite3
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "lexsport.db"
PDF_DIR = BASE_DIR / "output" / "pdfs" / "regulations"
JSON_DIR = BASE_DIR / "output" / "json"
PDF_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
DELAY = 2.0


def init_regulations_db(conn):
    """Add regulations tables to database."""
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS regulations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT,
            body            TEXT,
            category        TEXT,
            year            INTEGER,
            version         TEXT,
            language        TEXT DEFAULT 'en',
            full_text       TEXT,
            url             TEXT,
            pdf_path        TEXT,
            key_articles    TEXT,
            scraped_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS regulation_articles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_id          INTEGER,
            article_number  TEXT,
            article_title   TEXT,
            article_text    TEXT,
            FOREIGN KEY (reg_id) REFERENCES regulations(id)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS reg_fts USING fts5(
            title, body, category, full_text, key_articles,
            content='regulations', content_rowid='id'
        );

        CREATE INDEX IF NOT EXISTS idx_reg_category ON regulations(category);
        CREATE INDEX IF NOT EXISTS idx_reg_year ON regulations(year);
    """)
    conn.commit()
    print("✓ Regulations tables initialized")


def fetch(url, delay=DELAY):
    time.sleep(delay)
    try:
        r = SESSION.get(url, timeout=15)
        return r if r.status_code == 200 else None
    except Exception as e:
        print(f"  ✗ Fetch failed: {e}")
        return None


def download_and_extract_pdf(url, name):
    safe = re.sub(r'[^\w\-]', '_', name)[:80]
    path = PDF_DIR / f"{safe}.pdf"
    if path.exists():
        try:
            reader = PdfReader(str(path))
            return " ".join(p.extract_text() or "" for p in reader.pages)[:40000]
        except:
            pass
    r = SESSION.get(url, timeout=20)
    if r.ok and 'pdf' in r.headers.get('content-type','').lower():
        path.write_bytes(r.content)
        try:
            reader = PdfReader(str(path))
            return " ".join(p.extract_text() or "" for p in reader.pages)[:40000]
        except:
            return ""
    return ""


def store_regulation(conn, data):
    c = conn.cursor()
    existing = c.execute("SELECT id FROM regulations WHERE url = ?", (data['url'],)).fetchone()
    if existing:
        return False

    c.execute("""
        INSERT INTO regulations
        (title, body, category, year, version, language, full_text, url, pdf_path, key_articles, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get('title','')[:500],
        data.get('body','')[:200],
        data.get('category','General'),
        data.get('year', datetime.now().year),
        data.get('version',''),
        data.get('language','en'),
        data.get('full_text','')[:50000],
        data.get('url',''),
        data.get('pdf_path',''),
        data.get('key_articles',''),
        datetime.now().isoformat()
    ))
    reg_id = c.lastrowid

    # Index articles
    text = data.get('full_text','')
    articles = re.findall(r'(Article\s+\d+[a-z]*[bis|ter]*)\s*[–\-—:]\s*([^\n]+)\n((?:[^\n]+\n?){1,10})', text, re.I)
    for art_num, art_title, art_text in articles[:50]:
        c.execute("""
            INSERT INTO regulation_articles (reg_id, article_number, article_title, article_text)
            VALUES (?,?,?,?)
        """, (reg_id, art_num.strip(), art_title.strip()[:200], art_text.strip()[:2000]))

    # FTS
    c.execute("""
        INSERT INTO reg_fts(rowid, title, body, category, full_text, key_articles)
        VALUES (?,?,?,?,?,?)
    """, (reg_id, data.get('title',''), data.get('body',''), data.get('category',''),
          data.get('full_text','')[:5000], data.get('key_articles','')))

    conn.commit()
    print(f"  ✓ Stored: {data.get('title','')[:60]}")
    return True


# ── SCRAPERS ───────────────────────────────────────────────────

def scrape_fifa(conn):
    """Scrape FIFA legal documents."""
    print("\n" + "="*55)
    print("  FIFA REGULATIONS")
    print("="*55)

    # These are the direct PDF URLs for key FIFA documents (publicly available)
    fifa_docs = [
        {
            "title": "FIFA Regulations on the Status and Transfer of Players (RSTP) 2024",
            "url": "https://digitalhub.fifa.com/m/1e5c2e73bf7ff31/original/Regulations-on-the-Status-and-Transfer-of-Players-2024.pdf",
            "category": "Transfer Regulations",
            "body": "FIFA",
            "year": 2024,
            "key_articles": "Art.1-Art.25, Art.17, Art.18ter, Art.20, Art.21"
        },
        {
            "title": "FIFA Regulations on the Status and Transfer of Players (RSTP) 2023",
            "url": "https://digitalhub.fifa.com/m/27aa897efbde1b20/original/Regulations-on-the-Status-and-Transfer-of-Players-2023.pdf",
            "category": "Transfer Regulations",
            "body": "FIFA",
            "year": 2023,
            "key_articles": "Art.17, Art.18, Art.18ter, Art.20, Art.21"
        },
        {
            "title": "FIFA Code of Ethics 2023",
            "url": "https://digitalhub.fifa.com/m/58e7b77eb0717aa/original/FIFA-Code-of-Ethics-2023-Edition.pdf",
            "category": "Ethics",
            "body": "FIFA",
            "year": 2023,
            "key_articles": "Art.1-Art.50"
        },
        {
            "title": "FIFA Football Agent Regulations 2023",
            "url": "https://digitalhub.fifa.com/m/1ffe54d1598c2bc5/original/FIFA-Football-Agent-Regulations.pdf",
            "category": "Agent Regulations",
            "body": "FIFA",
            "year": 2023,
            "key_articles": "Art.1-Art.40, Licensing, Commission Caps"
        },
        {
            "title": "FIFA Disciplinary Code 2023",
            "url": "https://digitalhub.fifa.com/m/3879cf4b02685de7/original/FIFA-Disciplinary-Code-EN.pdf",
            "category": "Disciplinary",
            "body": "FIFA",
            "year": 2023,
            "key_articles": "Art.1-Art.160"
        },
        {
            "title": "FIFA Statutes 2023",
            "url": "https://digitalhub.fifa.com/m/14a2d2bed5ffa235/original/FIFA-Statutes-2023_EN.pdf",
            "category": "Governance",
            "body": "FIFA",
            "year": 2023,
            "key_articles": "Art.1-Art.90"
        },
        {
            "title": "FIFA Working with Intermediaries Regulations",
            "url": "https://digitalhub.fifa.com/m/735e89a9af7c0e25/original/Working-with-Intermediaries-Regulations-2015.pdf",
            "category": "Intermediary",
            "body": "FIFA",
            "year": 2015,
            "key_articles": "Art.1-Art.10"
        },
    ]

    stored = 0
    for doc in fifa_docs:
        print(f"\n  Fetching: {doc['title'][:55]}...")
        text = download_and_extract_pdf(doc['url'], f"FIFA_{doc['year']}_{doc['category']}")
        if not text:
            # Try fetching page instead
            page = fetch(doc['url'])
            text = page.text[:30000] if page else ""

        doc['full_text'] = text
        if store_regulation(conn, doc):
            stored += 1
        else:
            print(f"  → Already stored")

    print(f"\n  FIFA: {stored}/{len(fifa_docs)} regulations stored")
    return stored


def scrape_wada(conn):
    """Scrape WADA anti-doping documents."""
    print("\n" + "="*55)
    print("  WADA ANTI-DOPING CODE & STANDARDS")
    print("="*55)

    wada_docs = [
        {
            "title": "World Anti-Doping Code 2021",
            "url": "https://www.wada-ama.org/sites/default/files/resources/files/2021_wada_code.pdf",
            "category": "Anti-Doping Code",
            "body": "WADA",
            "year": 2021,
            "key_articles": "Art.1-Art.25, Art.10 (Sanctions), Art.4.2 (Prohibited List)"
        },
        {
            "title": "WADA Prohibited List 2025",
            "url": "https://www.wada-ama.org/sites/default/files/2024-09/2025list_en_final.pdf",
            "category": "Prohibited List",
            "body": "WADA",
            "year": 2025,
            "key_articles": "S0-S9, M1-M3, P1"
        },
        {
            "title": "WADA Prohibited List 2024",
            "url": "https://www.wada-ama.org/sites/default/files/2023-09/2024list_en.pdf",
            "category": "Prohibited List",
            "body": "WADA",
            "year": 2024,
            "key_articles": "S0-S9, M1-M3"
        },
        {
            "title": "WADA International Standard for Testing and Investigations 2021",
            "url": "https://www.wada-ama.org/sites/default/files/resources/files/isti_2021.pdf",
            "category": "Testing Standards",
            "body": "WADA",
            "year": 2021,
            "key_articles": "Art.1-Art.14"
        },
        {
            "title": "WADA International Standard for Therapeutic Use Exemptions 2024",
            "url": "https://www.wada-ama.org/sites/default/files/2023-10/istue_2024_en_final.pdf",
            "category": "TUE Standards",
            "body": "WADA",
            "year": 2024,
            "key_articles": "TUE Criteria, Art.4-Art.7"
        },
        {
            "title": "WADA International Standard for Results Management 2021",
            "url": "https://www.wada-ama.org/sites/default/files/resources/files/isrm_2021.pdf",
            "category": "Results Management",
            "body": "WADA",
            "year": 2021,
            "key_articles": "Art.1-Art.12, Provisional Suspensions"
        },
    ]

    stored = 0
    for doc in wada_docs:
        print(f"\n  Fetching: {doc['title'][:55]}...")
        text = download_and_extract_pdf(doc['url'], f"WADA_{doc['year']}_{doc['category']}")
        doc['full_text'] = text
        if store_regulation(conn, doc):
            stored += 1
        else:
            print(f"  → Already stored")

    print(f"\n  WADA: {stored}/{len(wada_docs)} documents stored")
    return stored


def scrape_uefa(conn):
    """Scrape UEFA regulations."""
    print("\n" + "="*55)
    print("  UEFA REGULATIONS")
    print("="*55)

    uefa_docs = [
        {
            "title": "UEFA Champions League Regulations 2024-25",
            "url": "https://documents.uefa.com/r/Regulations-of-the-UEFA-Champions-League-2024/25",
            "category": "Competition Rules",
            "body": "UEFA",
            "year": 2024,
            "key_articles": "Eligibility, Financial Rules, Disciplinary"
        },
        {
            "title": "UEFA Club Licensing and Financial Sustainability Regulations 2024",
            "url": "https://documents.uefa.com/r/UEFA-Club-Licensing-and-Financial-Sustainability-Regulations-2024",
            "category": "Financial Regulations",
            "body": "UEFA",
            "year": 2024,
            "key_articles": "Licensing Criteria, Financial Sustainability, Squad Cost Ratio"
        },
        {
            "title": "UEFA Disciplinary Regulations 2024",
            "url": "https://documents.uefa.com/r/UEFA-Disciplinary-Regulations-2024",
            "category": "Disciplinary",
            "body": "UEFA",
            "year": 2024,
            "key_articles": "Art.1-Art.80"
        },
        {
            "title": "UEFA Anti-Doping Regulations 2024",
            "url": "https://documents.uefa.com/r/UEFA-Anti-Doping-Regulations-2024",
            "category": "Anti-Doping",
            "body": "UEFA",
            "year": 2024,
            "key_articles": "Testing, TUE, Sanctions"
        },
    ]

    stored = 0
    for doc in uefa_docs:
        print(f"\n  Fetching: {doc['title'][:55]}...")
        # Try PDF first, then HTML
        text = download_and_extract_pdf(doc['url'], f"UEFA_{doc['year']}_{doc['category']}")
        if not text:
            page = fetch(doc['url'])
            if page:
                soup = BeautifulSoup(page.text, 'lxml')
                text = soup.get_text(separator='\n', strip=True)[:30000]
        doc['full_text'] = text
        if store_regulation(conn, doc):
            stored += 1
        else:
            print(f"  → Already stored")

    print(f"\n  UEFA: {stored}/{len(uefa_docs)} documents stored")
    return stored


def scrape_national_laws(conn):
    """Store key national sports law references."""
    print("\n" + "="*55)
    print("  NATIONAL SPORTS LAW")
    print("="*55)

    # Key national law texts that are freely available
    national_laws = [
        {
            "title": "Spanish Royal Decree 1006/1985 — Professional Sportspeople Labour Relations",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1985-11547",
            "category": "National Law",
            "body": "Spain",
            "year": 1985,
            "language": "es",
            "key_articles": "Art.1-Art.24, Injury Protection, Termination Rights"
        },
        {
            "title": "French Sports Code (Code du Sport) — Selected Provisions",
            "url": "https://www.legifrance.gouv.fr/codes/id/LEGITEXT000006071318",
            "category": "National Law",
            "body": "France",
            "year": 2006,
            "language": "fr",
            "key_articles": "L100-L600, Professional Sport, Anti-Doping"
        },
        {
            "title": "UK Sports Act 1999",
            "url": "https://www.legislation.gov.uk/ukpga/1999/29/contents",
            "category": "National Law",
            "body": "United Kingdom",
            "year": 1999,
            "language": "en",
            "key_articles": "UK Anti-Doping, Sport England Powers"
        },
        {
            "title": "US Amateur Sports Act (Ted Stevens Olympic & Amateur Sports Act)",
            "url": "https://www.law.cornell.edu/uscode/text/36/subtitle-II/part-B/chapter-2205",
            "category": "National Law",
            "body": "USA",
            "year": 2020,
            "language": "en",
            "key_articles": "USOPC, NGB Governance, Athlete Rights"
        },
    ]

    stored = 0
    for doc in national_laws:
        print(f"\n  Fetching: {doc['title'][:55]}...")
        page = fetch(doc['url'])
        text = ""
        if page:
            soup = BeautifulSoup(page.text, 'lxml')
            # Remove nav, headers, footers
            for tag in soup.find_all(['nav','header','footer','script','style']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)[:30000]
        doc['full_text'] = text
        if store_regulation(conn, doc):
            stored += 1
        else:
            print(f"  → Already stored")

    print(f"\n  National Laws: {stored}/{len(national_laws)} stored")
    return stored


def export_regulations_json(conn):
    """Export regulations index to JSON."""
    c = conn.cursor()
    regs = c.execute("""
        SELECT title, body, category, year, language, key_articles, url
        FROM regulations ORDER BY year DESC, body ASC
    """).fetchall()

    index = [{"title": r[0], "body": r[1], "category": r[2], "year": r[3],
               "language": r[4], "key_articles": r[5], "url": r[6]} for r in regs]

    path = JSON_DIR / "regulations_index.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"total": len(index), "updated": datetime.now().isoformat(), "regulations": index}, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Regulations index exported: {len(index)} documents → {path}")

    # Summary by body
    summary = c.execute("SELECT body, COUNT(*) FROM regulations GROUP BY body ORDER BY COUNT(*) DESC").fetchall()
    print("\n  Summary by regulatory body:")
    for body, count in summary:
        print(f"    {body:<25} {count} documents")


def run_regulations_scraper():
    """Main entry point for regulations scraper."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     LEXSPORT REGULATIONS SCRAPER — Starting Run             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    conn = sqlite3.connect(DB_PATH)
    init_regulations_db(conn)

    total = 0
    total += scrape_fifa(conn)
    total += scrape_wada(conn)
    total += scrape_uefa(conn)
    total += scrape_national_laws(conn)
    export_regulations_json(conn)

    db_count = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║               REGULATIONS SCRAPE COMPLETE                   ║
╠══════════════════════════════════════════════════════════════╣
║  New documents stored:  {total:<35} ║
║  Total in database:     {db_count:<35} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    conn.close()


if __name__ == "__main__":
    run_regulations_scraper()
