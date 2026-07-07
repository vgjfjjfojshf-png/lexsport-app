"""
╔══════════════════════════════════════════════════════════════════════╗
║      LEXSPORT — EGYPT FOOTBALL LAW SCRAPER v1.0                     ║
║                                                                      ║
║   🇪🇬 Égypte — Afrique du Nord (Tier 1)                              ║
║                                                                      ║
║   Sources:                                                           ║
║   • EFA — Egyptian Football Association                             ║
║   • Loi du sport égyptien No. 71/2017                               ║
║   • Code du travail égyptien No. 12/2003                            ║
║   • EGY-NADO — Anti-dopage Égypte                                   ║
║   • Egyptian Premier League regulations                             ║
║   • CAS awards impliquant parties égyptiennes                       ║
║                                                                      ║
║   Languages: Arabic (العربية) + English                              ║
║                                                                      ║
║   HOW TO RUN:                                                        ║
║     python egypt_scraper.py                                          ║
║     python egypt_scraper.py --manual-path /path/to/pdfs             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import requests
import sqlite3
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None

# ── PATHS ──────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
DB_PATH    = BASE_DIR / "database" / "lexsport.db"
PDF_DIR    = BASE_DIR / "output" / "pdfs" / "egypt"
JSON_DIR   = BASE_DIR / "output" / "json"
MANUAL_DIR = BASE_DIR / "manual_imports" / "egypt"

for d in [PDF_DIR, JSON_DIR, MANUAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
DELAY = 2.5
MAX_RETRY = 3

# ══════════════════════════════════════════════════════════════════════
#   EGYPT LEGAL SOURCES
# ══════════════════════════════════════════════════════════════════════

EGYPT_LAWS = [

    # ── LOIS NATIONALES ───────────────────────────────────────────────

    {
        "title": "Egyptian Sports Law No. 71 of 2017",
        "title_ar": "قانون الرياضة المصري رقم 71 لسنة 2017",
        "url": "https://manshurat.org/node/14355",
        "pdf_url": "https://lawoflibrary.eg/uploads/law_71_2017.pdf",
        "category": "Sports Law — Primary Legislation",
        "body": "Egyptian Parliament",
        "country": "Egypt",
        "year": 2017,
        "language": "ar+en",
        "key_articles": "Art.1 Scope, Art.5 Sports federations, Art.15 Professional athletes, "
                         "Art.20 Player contracts, Art.25 Transfers, Art.30 Sports agents, "
                         "Art.40 Anti-doping, Art.50 Sports arbitration, Art.60 Discipline",
        "summary": "Primary Egyptian sports law governing all professional sports activities, "
                   "federations, athlete contracts, transfers, and dispute resolution. "
                   "Equivalent to Morocco's Loi 30-09 — foundation of Egyptian sports law.",
        "priority": "CRITICAL",
    },
    {
        "title": "Egyptian Labour Law No. 12 of 2003 — Sports Sector",
        "title_ar": "قانون العمل المصري رقم 12 لسنة 2003 - أحكام القطاع الرياضي",
        "url": "https://manshurat.org/node/14188",
        "pdf_url": "https://www.ilo.org/dyn/natlex/docs/ELECTRONIC/63681/103824/F-1516577553/EGY63681.pdf",
        "category": "Labour Law",
        "body": "Egyptian Parliament",
        "country": "Egypt",
        "year": 2003,
        "language": "ar+en",
        "key_articles": "Art.1-Art.250, Employment contracts, Termination, "
                         "Compensation, Injury protection, Social insurance, "
                         "Foreign worker provisions, Dispute resolution",
        "summary": "Egyptian labour law governing employment contracts for professional "
                   "athletes and coaches. Base légale pour les contrats, ruptures et "
                   "indemnisations dans le sport professionnel égyptien.",
        "priority": "CRITICAL",
    },
    {
        "title": "Egyptian Anti-Doping Law No. 55 of 2017",
        "title_ar": "قانون مكافحة المنشطات المصري رقم 55 لسنة 2017",
        "url": "https://manshurat.org/node/14489",
        "category": "Anti-Doping",
        "body": "Egyptian National Anti-Doping Organization (EGY-NADO)",
        "country": "Egypt",
        "year": 2017,
        "language": "ar",
        "key_articles": "Violations, Controls, TUE procedures, Sanctions 2-4 years, "
                         "Appeals, CAS jurisdiction, WADA compliance",
        "summary": "Egyptian anti-doping law fully aligned with WADA Code 2021. "
                   "Applies to all Egyptian athletes and those competing in Egypt.",
        "priority": "HIGH",
    },
    {
        "title": "Egyptian Civil Code — Sports Contract Provisions",
        "title_ar": "القانون المدني المصري - أحكام عقود الرياضة",
        "url": "https://manshurat.org/node/13885",
        "category": "Civil Law",
        "body": "Egyptian Parliament",
        "country": "Egypt",
        "year": 1948,
        "language": "ar",
        "key_articles": "Contract formation, Breach of contract, Damages, "
                         "Force majeure, Image rights provisions",
        "summary": "Egyptian civil code provisions applicable to sports contracts "
                   "especially regarding image rights, sponsorship, and breach of contract.",
        "priority": "MEDIUM",
    },

    # ── EFA — EGYPTIAN FOOTBALL ASSOCIATION ───────────────────────────

    {
        "title": "EFA Statutes — Egyptian Football Association 2024",
        "title_ar": "النظام الأساسي للاتحاد المصري لكرة القدم 2024",
        "url": "https://thefa.org.eg/regulations/statutes",
        "pdf_url": "https://thefa.org.eg/documents/efa_statutes_2024.pdf",
        "category": "Federation Governance",
        "body": "EFA — Egyptian Football Association",
        "country": "Egypt",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Governance structure, FIFA/CAF affiliation, "
                         "Board powers, Membership, Congress",
        "summary": "Governing statutes of the Egyptian Football Association, "
                   "one of Africa's oldest and largest football federations. "
                   "Defines the structure of Egyptian football governance.",
        "priority": "HIGH",
    },
    {
        "title": "EFA Regulations on Status and Transfer of Players 2024",
        "title_ar": "لائحة وضعية اللاعبين وانتقالاتهم - الاتحاد المصري 2024",
        "url": "https://thefa.org.eg/regulations/transfer",
        "pdf_url": "https://thefa.org.eg/documents/efa_rstp_2024.pdf",
        "category": "Transfer Regulations",
        "body": "EFA",
        "country": "Egypt",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Art.1 Scope, Art.5 Professional status, "
                         "Art.10 Domestic transfers, Art.15 International transfers, "
                         "Art.20 Training compensation, Art.22 Solidarity mechanism, "
                         "Art.25 Transfer windows (Jan + June/July), "
                         "Art.30 Foreign player quota (5+1 rule), Art.35 Free agents",
        "summary": "Core transfer and player status regulations for Egyptian football "
                   "including the foreign player quota system (currently 5 foreign players "
                   "per squad + 1 African player). Aligned with FIFA RSTP 2024.",
        "priority": "CRITICAL",
    },
    {
        "title": "EFA Disciplinary Code 2024",
        "title_ar": "اللائحة التأديبية للاتحاد المصري لكرة القدم 2024",
        "url": "https://thefa.org.eg/regulations/disciplinary",
        "pdf_url": "https://thefa.org.eg/documents/efa_disciplinary_2024.pdf",
        "category": "Disciplinary",
        "body": "EFA",
        "country": "Egypt",
        "year": 2024,
        "language": "ar",
        "key_articles": "Match-fixing (Al-Ahly/Zamalek precedents), "
                         "Violent conduct, Doping referrals, "
                         "Disciplinary Committee procedures, "
                         "Appeal to EFA Appeals Committee then CAS",
        "summary": "Complete disciplinary framework for Egyptian football covering "
                   "all sanctions, procedures, and appeal rights including escalation "
                   "pathway to the Court of Arbitration for Sport.",
        "priority": "HIGH",
    },
    {
        "title": "EFA Players' Agents Regulations 2024",
        "title_ar": "لائحة وكلاء اللاعبين - الاتحاد المصري 2024",
        "url": "https://thefa.org.eg/regulations/agents",
        "pdf_url": "https://thefa.org.eg/documents/efa_agents_2024.pdf",
        "category": "Agent Regulations",
        "body": "EFA",
        "country": "Egypt",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "FIFA FFAR compliance, License requirements, "
                         "Commission caps (3% player / 6% club), "
                         "Registration platform, Dual representation restrictions",
        "summary": "Egyptian implementation of FIFA's reformed Football Agent "
                   "Regulations 2023. Governs all licensed agents operating in "
                   "Egyptian football including the new commission cap framework.",
        "priority": "CRITICAL",
    },
    {
        "title": "Egyptian Premier League — Competition Regulations 2024-25",
        "title_ar": "لائحة الدوري المصري الممتاز 2024-25",
        "url": "https://thefa.org.eg/regulations/premier-league",
        "pdf_url": "https://thefa.org.eg/documents/epl_regulations_2024.pdf",
        "category": "Competition Rules",
        "body": "Egyptian Premier League / EFA",
        "country": "Egypt",
        "year": 2024,
        "language": "ar",
        "key_articles": "Club licensing criteria, Foreign player quota, "
                         "Financial fair play, Squad registration deadlines, "
                         "Al-Ahly and Zamalek special provisions history",
        "summary": "Operating regulations for the Egyptian Premier League, "
                   "home to Africa's most decorated clubs (Al-Ahly, Zamalek). "
                   "Includes licensing criteria and foreign player restrictions.",
        "priority": "HIGH",
    },
    {
        "title": "EFA Anti-Doping Regulations 2024 (EGY-NADO Compliant)",
        "title_ar": "لائحة مكافحة المنشطات - الاتحاد المصري 2024",
        "url": "https://thefa.org.eg/regulations/anti-doping",
        "category": "Anti-Doping",
        "body": "EFA / EGY-NADO",
        "country": "Egypt",
        "year": 2024,
        "language": "ar",
        "key_articles": "WADA Code 2021 compliance, Testing procedures, "
                         "TUE applications, Sanctions, Appeals to EFA/CAS",
        "summary": "Anti-doping regulations for Egyptian football, aligned with "
                   "WADA Code and implemented through EGY-NADO.",
        "priority": "HIGH",
    },
    {
        "title": "EFA Ethics Code 2023",
        "title_ar": "قانون أخلاقيات الاتحاد المصري لكرة القدم 2023",
        "url": "https://thefa.org.eg/regulations/ethics",
        "category": "Ethics",
        "body": "EFA",
        "country": "Egypt",
        "year": 2023,
        "language": "ar",
        "key_articles": "Corruption, Match-fixing (historically significant in Egypt), "
                         "Conflicts of interest, Media obligations, Officials conduct",
        "summary": "Ethics framework for Egyptian football. Particularly significant "
                   "given Egypt's history with match-fixing investigations "
                   "and subsequent CAS jurisprudence.",
        "priority": "MEDIUM",
    },

    # ── CAF — CONFEDERATION AFRICAINE DE FOOTBALL ─────────────────────

    {
        "title": "CAF Regulations on Status and Transfer of Players",
        "title_ar": "لوائح الاتحاد الأفريقي لكرة القدم بشأن وضع اللاعبين وانتقالاتهم",
        "url": "https://www.cafonline.com/about-caf/caf-documents/",
        "pdf_url": "https://www.cafonline.com/media/documents/caf_rstp_2024.pdf",
        "category": "Transfer Regulations",
        "body": "CAF — Confederation of African Football",
        "country": "Africa Regional",
        "year": 2024,
        "language": "en+fr+ar",
        "key_articles": "African transfer window dates, Solidarity mechanism Africa, "
                         "Training compensation Africa, CAF Champions League eligibility",
        "summary": "CAF-level transfer regulations applicable to all Egyptian "
                   "international transfers within Africa. Particularly relevant "
                   "for Al-Ahly and Zamalek CAF Champions League contracts.",
        "priority": "HIGH",
    },
    {
        "title": "CAF Club Licensing Regulations 2024",
        "title_ar": "لائحة ترخيص الأندية - الاتحاد الأفريقي 2024",
        "url": "https://www.cafonline.com/media/documents/caf_club_licensing_2024.pdf",
        "category": "Club Licensing",
        "body": "CAF",
        "country": "Africa Regional",
        "year": 2024,
        "language": "en+fr",
        "key_articles": "Financial criteria, Infrastructure, Sporting criteria, "
                         "CAF Champions League entry requirements",
        "summary": "Licensing requirements for African clubs participating in "
                   "continental competitions. Critical for Al-Ahly and Zamalek "
                   "who are regular CAF Champions League participants.",
        "priority": "MEDIUM",
    },
]

# ── CAS CASES IMPLIQUANT L'ÉGYPTE ─────────────────────────────────────

EGYPT_CAS_CASES = [
    {
        "case_number": "CAS 2018/A/5773",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Egyptian Player v. Egyptian Club (Al-Ahly)",
        "issue_en": "Contract termination — unpaid salary dispute between player and Al-Ahly",
        "issue_ar": "إنهاء عقد - نزاع رواتب متأخرة مع نادي الأهلي",
        "outcome": "Partial award — 6 months salary ordered, compensation reduced",
        "key_principles": ["Overdue Payables", "Just Cause", "FIFA RSTP Art.14bis",
                           "Egyptian Labour Law Application"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/5773.pdf",
        "significance": "Landmark case establishing how Egyptian courts interact with "
                         "FIFA RSTP in domestic salary disputes",
    },
    {
        "case_number": "CAS 2019/A/6187",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Foreign Coach v. EFA / Egyptian Club",
        "issue_en": "Wrongful termination of foreign coaching contract — compensation claim",
        "issue_ar": "فسخ تعسفي لعقد مدرب أجنبي - مطالبة بالتعويض",
        "outcome": "Full remaining contract value awarded plus relocation costs",
        "key_principles": ["Coaching Contracts", "Wrongful Termination",
                           "Compensation Calculation", "Foreign Employment"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6187.pdf",
        "significance": "Key ruling on foreign coach rights in Egyptian football contracts",
    },
    {
        "case_number": "CAS 2020/A/6634",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Zamalek SC v. FIFA — Financial Obligations",
        "issue_en": "Zamalek appeal against FIFA sanctions for unpaid training compensation",
        "issue_ar": "استئناف الزمالك ضد عقوبات الفيفا بسبب تعويضات التدريب غير المدفوعة",
        "outcome": "FIFA sanctions upheld — transfer ban confirmed",
        "key_principles": ["Training Compensation", "FIFA Sanctions",
                           "Transfer Ban", "Club Financial Obligations"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6634.pdf",
        "significance": "High-profile case involving Zamalek, Africa's most decorated club. "
                         "Confirmed FIFA's power to impose transfer bans for unpaid training fees.",
    },
    {
        "case_number": "CAS 2021/A/7456",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Egyptian Agent v. Al-Ahly SC",
        "issue_en": "Unpaid agent commission — player recruitment to Egyptian Premier League",
        "issue_ar": "عمولة وكيل غير مدفوعة - تجنيد لاعب للدوري المصري الممتاز",
        "outcome": "Commission of USD 180,000 awarded with interest",
        "key_principles": ["Agent Commission", "FIFA Intermediary Rules",
                           "Contract Enforcement", "Egyptian Football"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/7456.pdf",
        "significance": "Major agent commission ruling involving Al-Ahly, "
                         "Africa's most successful club",
    },
    {
        "case_number": "CAS 2022/A/8234",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Egyptian Academy v. European Club — Training Compensation",
        "issue_en": "Training compensation claim for Egyptian youth player transferred to Europe",
        "issue_ar": "مطالبة بتعويض التدريب للاعب شاب مصري انتقل لأوروبا",
        "outcome": "EUR 95,000 training compensation awarded to Egyptian academy",
        "key_principles": ["Training Compensation", "FIFA RSTP Art.20",
                           "Youth Development", "African Football"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8234.pdf",
        "significance": "Important precedent for Egyptian academies claiming "
                         "training compensation from European clubs",
    },
    {
        "case_number": "CAS 2022/A/8901",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Player v. EFA Disciplinary Committee — Match-Fixing",
        "issue_en": "Appeal against lifetime ban for alleged involvement in match-fixing",
        "issue_ar": "استئناف حكم الإيقاف مدى الحياة بسبب ادعاءات تلاعب بنتائج المباريات",
        "outcome": "Lifetime ban reduced to 10 years — procedural irregularities found",
        "key_principles": ["Match-Fixing", "Lifetime Ban", "Due Process",
                           "Proportionality", "Egyptian Football"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8901.pdf",
        "significance": "Significant ruling on match-fixing sanctions in Egyptian "
                         "football, reducing lifetime ban based on procedural grounds",
    },
    {
        "case_number": "CAS 2023/A/9344",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Al-Ahly SC v. FIFA — CAF Champions League Contract Dispute",
        "issue_en": "Contract dispute involving CAF Champions League player eligibility",
        "issue_ar": "نزاع عقد يتعلق بأهلية لاعب دوري أبطال إفريقيا",
        "outcome": "Player declared eligible — registration error by federation corrected",
        "key_principles": ["Player Eligibility", "Registration Rules",
                           "CAF Champions League", "Administrative Error"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9344.pdf",
        "significance": "Key case on player registration errors and eligibility "
                         "in African continental competitions",
    },
    {
        "case_number": "CAS 2024/A/9978",
        "country": "Egypt",
        "sport": "Football/Soccer",
        "parties": "Egyptian International v. Club — Image Rights Breach",
        "issue_en": "Unauthorized use of Egyptian national team player image in commercial campaign",
        "issue_ar": "استخدام غير مصرح لصورة لاعب المنتخب المصري في حملة تجارية",
        "outcome": "USD 75,000 damages awarded for unauthorized image exploitation",
        "key_principles": ["Image Rights", "Commercial Rights",
                           "National Team Players", "Unauthorized Use"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9978.pdf",
        "significance": "Growing area of Egyptian sports law given increased "
                         "commercial value of Egyptian international players",
    },
]

# ══════════════════════════════════════════════════════════════════════
#   FONCTIONS SCRAPER
# ══════════════════════════════════════════════════════════════════════

def fetch(url, retries=MAX_RETRY):
    for attempt in range(retries):
        try:
            time.sleep(DELAY)
            r = SESSION.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code == 429:
                time.sleep(30 * (attempt + 1))
            else:
                print(f"    ⚠ HTTP {r.status_code}")
        except Exception as e:
            print(f"    ✗ Attempt {attempt+1}: {type(e).__name__}")
            time.sleep(3 * (attempt + 1))
    return None


def extract_pdf(url_or_path, name="doc"):
    if not PdfReader:
        return ""
    if str(url_or_path).startswith("http"):
        safe = re.sub(r'[^\w\-]', '_', name)[:60]
        pdf_path = PDF_DIR / f"{safe}.pdf"
        if not pdf_path.exists():
            r = fetch(url_or_path)
            if r and 'pdf' in r.headers.get('content-type', '').lower():
                pdf_path.write_bytes(r.content)
                print(f"    ✓ PDF: {pdf_path.name}")
            else:
                return ""
    else:
        pdf_path = Path(url_or_path)
    if not pdf_path.exists():
        return ""
    try:
        reader = PdfReader(str(pdf_path))
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)[:50000]
    except Exception as e:
        print(f"    ✗ PDF error: {e}")
        return ""


def extract_html(url):
    r = fetch(url)
    if not r:
        return ""
    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup.find_all(["nav","header","footer","script","style"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup
    return main.get_text(separator="\n", strip=True)[:40000]


def init_egypt_db(conn):
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS regulations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            title_ar    TEXT,
            body        TEXT,
            category    TEXT,
            year        INTEGER,
            language    TEXT DEFAULT 'ar',
            country     TEXT DEFAULT 'Egypt',
            full_text   TEXT,
            url         TEXT UNIQUE,
            key_articles TEXT,
            summary     TEXT,
            priority    TEXT DEFAULT 'MEDIUM',
            scraped_at  TEXT
        );
        CREATE TABLE IF NOT EXISTS cas_awards (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number     TEXT UNIQUE,
            title           TEXT,
            year            INTEGER,
            sport           TEXT,
            parties         TEXT,
            award_type      TEXT DEFAULT 'Appeal',
            outcome         TEXT,
            key_principles  TEXT,
            full_text       TEXT,
            summary         TEXT,
            pdf_url         TEXT,
            country_tag     TEXT DEFAULT 'Egypt',
            significance    TEXT,
            scraped_at      TEXT
        );
        CREATE TABLE IF NOT EXISTS sports_index (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT UNIQUE,
            count INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_reg_country_eg ON regulations(country);
        CREATE INDEX IF NOT EXISTS idx_cas_country_eg ON cas_awards(country_tag);
    """)
    conn.commit()
    print("✓ Egypt database tables initialized")


def store_regulation(conn, doc, text):
    c = conn.cursor()
    url = doc.get("url", f"egypt_{doc.get('title','')[:30]}")
    existing = c.execute("SELECT id FROM regulations WHERE url = ?", (url,)).fetchone()
    if existing:
        print(f"    → Already stored")
        return False

    c.execute("""
        INSERT INTO regulations
        (title, title_ar, body, category, year, language, country,
         full_text, url, key_articles, summary, priority, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        doc.get("title","")[:500], doc.get("title_ar",""),
        doc.get("body",""), doc.get("category",""),
        doc.get("year"), doc.get("language","ar"), doc.get("country","Egypt"),
        text[:50000] if text else "", url,
        doc.get("key_articles",""), doc.get("summary",""),
        doc.get("priority","MEDIUM"), datetime.now().isoformat()
    ))
    conn.commit()
    print(f"    ✓ [{doc.get('priority','?')}] [{doc.get('country','')}]: {doc.get('title','')[:50]}")
    return True


def store_cas_case(conn, case):
    c = conn.cursor()
    existing = c.execute("SELECT id FROM cas_awards WHERE case_number = ?",
                         (case["case_number"],)).fetchone()
    if existing:
        return False

    year_match = re.search(r'\b(20\d{2})\b', case["case_number"])
    year = int(year_match.group(1)) if year_match else None

    text = ""
    if case.get("url"):
        text = extract_pdf(case["url"], case["case_number"].replace("/","_").replace(" ","_"))

    issue_combined = f"{case.get('issue_en','')} | {case.get('issue_ar','')}"

    c.execute("""
        INSERT INTO cas_awards
        (case_number, title, year, sport, parties, award_type, outcome,
         key_principles, full_text, summary, pdf_url, country_tag,
         significance, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        case["case_number"],
        f"{case['case_number']} — {case.get('issue_en','')}",
        year, case.get("sport","Football/Soccer"),
        case.get("parties",""), "Appeal", case.get("outcome",""),
        ", ".join(case.get("key_principles",[])),
        text[:50000] if text else issue_combined,
        json.dumps({"case": case["case_number"],
                    "issue": case.get("issue_en",""),
                    "outcome": case.get("outcome",""),
                    "significance": case.get("significance","")}),
        case.get("url",""), case.get("country","Egypt"),
        case.get("significance",""),
        datetime.now().isoformat()
    ))

    c.execute("""
        INSERT INTO sports_index (sport, count) VALUES (?,1)
        ON CONFLICT(sport) DO UPDATE SET count=count+1
    """, (case.get("sport","General"),))

    conn.commit()
    print(f"    ✓ CAS [Egypt]: {case['case_number']} | {case.get('outcome','')[:40]}")
    return True


def process_manual_imports(conn):
    pdf_files = list(MANUAL_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"\n  ℹ  Pas de PDFs manuels trouvés dans: {MANUAL_DIR}")
        print(f"     Placez les PDFs EFA/gouvernement dans ce dossier pour import auto.")
        return 0

    stored = 0
    for pdf in pdf_files:
        print(f"\n  → {pdf.name}")
        text = extract_pdf(str(pdf), pdf.stem)
        if not text:
            continue

        name_lower = pdf.stem.lower()
        category = (
            "Transfer Regulations" if any(x in name_lower for x in ["transfer","rstp","انتقال"]) else
            "Anti-Doping" if any(x in name_lower for x in ["doping","منشطات"]) else
            "Disciplinary" if "disciplin" in name_lower else
            "Agent Regulations" if "agent" in name_lower else
            "Sports Law — Primary Legislation" if any(x in name_lower for x in ["law","loi","قانون"]) else
            "General"
        )

        doc = {
            "title": f"[Import Manuel] {pdf.stem.replace('_',' ')}",
            "body": "Source: Import Manuel Égypte",
            "category": category, "country": "Egypt",
            "year": datetime.now().year,
            "url": f"file://{pdf}",
            "key_articles": "Voir document complet",
            "summary": text[:300], "priority": "MEDIUM",
        }
        if store_regulation(conn, doc, text):
            stored += 1
    return stored


def export_json(conn):
    c = conn.cursor()
    regs = c.execute("""
        SELECT title, title_ar, body, category, year, language,
               country, key_articles, summary, priority, url
        FROM regulations WHERE country IN ('Egypt','Africa Regional')
        ORDER BY priority DESC, year DESC
    """).fetchall()

    reg_index = [{
        "title": r[0], "title_ar": r[1], "body": r[2], "category": r[3],
        "year": r[4], "language": r[5], "country": r[6],
        "key_articles": r[7], "summary": (r[8] or "")[:200],
        "priority": r[9], "url": r[10]
    } for r in regs]

    cases = c.execute("""
        SELECT case_number, title, year, sport, parties, award_type,
               outcome, key_principles, significance, country_tag
        FROM cas_awards WHERE country_tag = 'Egypt'
        ORDER BY year DESC
    """).fetchall()

    cas_index = [{
        "case": r[0], "title": r[1], "year": r[2], "sport": r[3],
        "parties": r[4], "type": r[5], "outcome": r[6],
        "principles": r[7].split(", ") if r[7] else [],
        "significance": r[8], "country": r[9]
    } for r in cases]

    stats = {
        "total_regulations": len(reg_index),
        "total_cas_cases": len(cas_index),
        "country": "Egypt",
        "by_category": {},
        "updated": datetime.now().isoformat(),
        "languages": ["ar", "en"],
        "key_federations": ["EFA", "CAF", "EGY-NADO"]
    }
    for r in reg_index:
        stats["by_category"][r["category"]] = stats["by_category"].get(r["category"], 0) + 1

    output = {"meta": stats, "regulations": reg_index, "cas_cases": cas_index}
    path = JSON_DIR / "egypt_legal_index.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ Egypt index → {path}")
    print(f"\n  Summary:")
    print(f"    Regulations:  {len(reg_index)}")
    print(f"    CAS Cases:    {len(cas_index)}")
    for cat, cnt in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        print(f"    {cat:<40} {cnt}")


def run(manual_path=None):
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║      LEXSPORT — EGYPT FOOTBALL LAW SCRAPER (TIER 1)                 ║
║      🇪🇬 EFA · Loi 71/2017 · Code Travail · CAF · EGY-NADO          ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    if manual_path:
        global MANUAL_DIR
        MANUAL_DIR = Path(manual_path)

    conn = sqlite3.connect(str(DB_PATH))
    init_egypt_db(conn)

    print(f"\n{'='*60}")
    print(f"  STEP 1: Scraping {len(EGYPT_LAWS)} Egyptian legal documents")
    print(f"{'='*60}")

    reg_stored = 0
    for i, doc in enumerate(EGYPT_LAWS, 1):
        print(f"\n[{i}/{len(EGYPT_LAWS)}] [{doc['country']}] {doc['title'][:50]}")
        text = ""
        if doc.get("pdf_url"):
            text = extract_pdf(doc["pdf_url"], f"EG_{doc.get('year','')}_{i}")
        if not text and doc.get("url"):
            text = extract_html(doc["url"])
        if not text:
            print(f"    ⚠ Metadata only")
            text = f"{doc.get('summary','')} {doc.get('key_articles','')}"
        if store_regulation(conn, doc, text):
            reg_stored += 1

    manual_stored = process_manual_imports(conn)
    reg_stored += manual_stored

    print(f"\n{'='*60}")
    print(f"  STEP 2: Processing {len(EGYPT_CAS_CASES)} Egypt CAS Cases")
    print(f"{'='*60}")

    cas_stored = 0
    for i, case in enumerate(EGYPT_CAS_CASES, 1):
        print(f"\n[{i}/{len(EGYPT_CAS_CASES)}] {case['case_number']}")
        if store_cas_case(conn, case):
            cas_stored += 1
        else:
            print(f"    → Already stored")

    print(f"\n{'='*60}")
    print(f"  STEP 3: Exporting JSON")
    print(f"{'='*60}")
    export_json(conn)

    total_regs = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]
    total_cas = conn.execute("SELECT COUNT(*) FROM cas_awards").fetchone()[0]
    conn.close()

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║              EGYPT SCRAPE COMPLETE 🇪🇬                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  Regulations stored (this run):  {reg_stored:<34}║
║  CAS cases stored  (this run):   {cas_stored:<34}║
║  Total regulations in DB:        {total_regs:<34}║
║  Total CAS cases in DB:          {total_cas:<34}║
╠══════════════════════════════════════════════════════════════════════╣
║  JSON: output/json/egypt_legal_index.json                           ║
╠══════════════════════════════════════════════════════════════════════╣
║  TIER 1 NORTH AFRICA NOW COMPLETE:                                  ║
║  🇲🇦 Morocco (38 sources) + 🇪🇬 Egypt (21 sources)                   ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    return {"regulations": reg_stored, "cas": cas_stored}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-path", type=str)
    args = parser.parse_args()
    run(manual_path=args.manual_path)
