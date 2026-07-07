"""
╔══════════════════════════════════════════════════════════════════════╗
║      LEXSPORT — GULF STATES FOOTBALL LAW SCRAPER v1.0               ║
║                                                                      ║
║   Tier 1 — MENA Expansion: Saudi Arabia · UAE · Qatar               ║
║                                                                      ║
║   Sources:                                                           ║
║   • SAFF — Saudi Arabian Football Federation                        ║
║   • Saudi Arbitration Center for Sport (SCAS)                       ║
║   • UAEFA — UAE Football Association                                ║
║   • DIFC Courts — Dubai International Financial Centre              ║
║   • QFA — Qatar Football Association                                ║
║   • CAS awards involving Gulf clubs/players                          ║
║   • Saudi Pro League / UAE Pro League / Qatar Stars League rules    ║
║                                                                      ║
║   Languages: Arabic (العربية) + English                              ║
║                                                                      ║
║   HOW TO RUN:                                                        ║
║     python gulf_scraper.py                                           ║
║     python gulf_scraper.py --country saudi                           ║
║     python gulf_scraper.py --country uae                             ║
║     python gulf_scraper.py --country qatar                           ║
║     python gulf_scraper.py --manual-path /path/to/pdfs              ║
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
PDF_DIR    = BASE_DIR / "output" / "pdfs" / "gulf"
JSON_DIR   = BASE_DIR / "output" / "json"
MANUAL_DIR = BASE_DIR / "manual_imports" / "gulf"

for d in [PDF_DIR, JSON_DIR, MANUAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
DELAY = 2.5
MAX_RETRY = 3

# ══════════════════════════════════════════════════════════════════════
#   GULF FOOTBALL LEGAL SOURCES
# ══════════════════════════════════════════════════════════════════════

GULF_LAWS = [

    # ── SAUDI ARABIA ─────────────────────────────────────────────────

    {
        "title": "SAFF Statutes — Saudi Arabian Football Federation",
        "title_ar": "النظام الأساسي للاتحاد السعودي لكرة القدم",
        "url": "https://www.saff.com.sa/en/regulations/statutes",
        "pdf_url": "https://www.saff.com.sa/documents/saff_statutes_2024.pdf",
        "category": "Federation Governance",
        "body": "SAFF",
        "country": "Saudi Arabia",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Governance structure, Board powers, FIFA/AFC relations, Membership rules",
        "summary": "Governing statutes of the Saudi Arabian Football Federation, defining "
                   "its organizational structure, powers, and relationship with FIFA/AFC.",
        "priority": "HIGH",
    },
    {
        "title": "SAFF Regulations on Status and Transfer of Players 2024",
        "title_ar": "لائحة وضعية اللاعبين وانتقالاتهم - الاتحاد السعودي 2024",
        "url": "https://www.saff.com.sa/en/regulations/transfer",
        "pdf_url": "https://www.saff.com.sa/documents/saff_rstp_2024.pdf",
        "category": "Transfer Regulations",
        "body": "SAFF",
        "country": "Saudi Arabia",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Art.1 Scope, Art.5 Professional status, Art.10 Domestic transfers, "
                         "Art.15 International transfers, Art.20 Training compensation, "
                         "Art.25 Foreign player quotas (8+1 rule), Art.30 Registration windows",
        "summary": "Core transfer and player status regulations for Saudi Pro League and "
                   "all SAFF-affiliated competitions. Includes the foreign player quota "
                   "system that governs the league's high-profile international signings.",
        "priority": "CRITICAL",
    },
    {
        "title": "Saudi Pro League — Competition Regulations 2024-25",
        "title_ar": "لائحة دوري روشن السعودي للمحترفين 2024-25",
        "url": "https://www.saudiproleague.sa/regulations",
        "pdf_url": "https://www.saudiproleague.sa/documents/spl_regulations_2024.pdf",
        "category": "Competition Rules",
        "body": "Saudi Pro League (Roshn Saudi League)",
        "country": "Saudi Arabia",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Club licensing criteria, Foreign player quota (currently 8 per club), "
                         "Financial fair play, Squad registration, Salary cap discussions",
        "summary": "Operating regulations for the Saudi Pro League covering club licensing, "
                   "the foreign player quota system central to PIF-backed signings, "
                   "and financial sustainability requirements.",
        "priority": "CRITICAL",
    },
    {
        "title": "SAFF Players' Agents Regulations 2023 (Post-FIFA Reform)",
        "title_ar": "لائحة وكلاء اللاعبين - الاتحاد السعودي 2023",
        "url": "https://www.saff.com.sa/en/regulations/agents",
        "pdf_url": "https://www.saff.com.sa/documents/saff_agents_2023.pdf",
        "category": "Agent Regulations",
        "body": "SAFF",
        "country": "Saudi Arabia",
        "year": 2023,
        "language": "ar+en",
        "key_articles": "Licensing exam, Commission caps (3%/6% per FIFA FFAR), "
                         "Registration via FIFA Agent Platform, Conflict of interest rules",
        "summary": "Saudi implementation of FIFA's reformed Football Agent Regulations, "
                   "governing the licensing and conduct of agents operating in the Kingdom.",
        "priority": "HIGH",
    },
    {
        "title": "SAFF Disciplinary Code 2024",
        "title_ar": "اللائحة التأديبية للاتحاد السعودي لكرة القدم 2024",
        "url": "https://www.saff.com.sa/en/regulations/disciplinary",
        "pdf_url": "https://www.saff.com.sa/documents/saff_disciplinary_2024.pdf",
        "category": "Disciplinary",
        "body": "SAFF",
        "country": "Saudi Arabia",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Match-fixing, Doping sanctions, Violent conduct, Appeal procedure, "
                         "Disciplinary Committee jurisdiction, Referral to CAS",
        "summary": "Disciplinary framework for Saudi football, covering sanctions process "
                   "and appeal rights through to the Saudi Arbitration Center and CAS.",
        "priority": "HIGH",
    },
    {
        "title": "Saudi Arbitration Center for Sport (SCAS) — Procedural Rules",
        "title_ar": "مركز التحكيم الرياضي السعودي - القواعد الإجرائية",
        "url": "https://www.scas.sa/en/rules",
        "pdf_url": "https://www.scas.sa/documents/scas_rules_2023.pdf",
        "category": "Arbitration",
        "body": "Saudi Arbitration Center for Sport (SCAS)",
        "country": "Saudi Arabia",
        "year": 2023,
        "language": "ar+en",
        "key_articles": "Jurisdiction, Filing procedure, Panel composition, Timeframes, "
                         "Enforcement, Relationship with CAS Lausanne",
        "summary": "Newly established Saudi sports arbitration body, created to resolve "
                   "domestic sports disputes before — or alongside — CAS jurisdiction. "
                   "Critical for understanding dispute resolution pathways in the Kingdom.",
        "priority": "CRITICAL",
    },
    {
        "title": "Saudi Labour Law — Royal Decree M/51 (Sports provisions)",
        "title_ar": "نظام العمل السعودي - المرسوم الملكي م/51",
        "url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/16f5d97c-380d-4ed0-9d40-a9a700f2f1c2/1",
        "category": "Labour Law",
        "body": "Saudi Ministry of Human Resources",
        "country": "Saudi Arabia",
        "year": 2005,
        "language": "ar+en",
        "key_articles": "Employment contracts, Termination, End of service benefits, "
                         "Foreign worker provisions (Iqama), Dispute resolution",
        "summary": "General Saudi labour law applicable to foreign player and coach "
                   "employment contracts, particularly relevant given the high volume "
                   "of expatriate athletes under Saudi-issued work permits (Iqama).",
        "priority": "HIGH",
    },
    {
        "title": "Saudi Anti-Doping Committee (SAADC) Code",
        "title_ar": "نظام مكافحة المنشطات - اللجنة السعودية لمكافحة المنشطات",
        "url": "https://www.saadc.sa/en/code",
        "pdf_url": "https://www.saadc.sa/documents/saadc_code_2024.pdf",
        "category": "Anti-Doping",
        "body": "Saudi Anti-Doping Committee (SAADC)",
        "country": "Saudi Arabia",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "WADA Code compliance, Testing procedures, TUE process, Sanctions, "
                         "Appeals to SCAS/CAS",
        "summary": "Saudi national anti-doping organization code, fully compliant with "
                   "the WADA World Anti-Doping Code 2021.",
        "priority": "HIGH",
    },

    # ── UAE ──────────────────────────────────────────────────────────

    {
        "title": "UAEFA Statutes — UAE Football Association",
        "title_ar": "النظام الأساسي لاتحاد الإمارات لكرة القدم",
        "url": "https://www.uaefa.ae/en/regulations/statutes",
        "pdf_url": "https://www.uaefa.ae/documents/uaefa_statutes_2024.pdf",
        "category": "Federation Governance",
        "body": "UAEFA",
        "country": "UAE",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Governance, Emirates-level associations, FIFA/AFC affiliation, Elections",
        "summary": "Governing statutes of the UAE Football Association overseeing all "
                   "football activity across the seven emirates.",
        "priority": "HIGH",
    },
    {
        "title": "UAE Pro League — Regulations 2024-25",
        "title_ar": "لائحة دوري المحترفين الإماراتي 2024-25",
        "url": "https://www.uaepl.ae/regulations",
        "pdf_url": "https://www.uaepl.ae/documents/uaepl_regulations_2024.pdf",
        "category": "Competition Rules",
        "body": "UAE Pro League",
        "country": "UAE",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Foreign player quota, Club licensing, Emiratization requirements "
                         "(local player development quotas), Financial regulations",
        "summary": "Operating regulations for the UAE Pro League including the foreign "
                   "player quota system and Emiratization requirements unique to the league.",
        "priority": "CRITICAL",
    },
    {
        "title": "UAEFA Regulations on Status and Transfer of Players",
        "title_ar": "لائحة وضعية اللاعبين وانتقالاتهم - اتحاد الإمارات",
        "url": "https://www.uaefa.ae/en/regulations/transfer",
        "pdf_url": "https://www.uaefa.ae/documents/uaefa_rstp_2024.pdf",
        "category": "Transfer Regulations",
        "body": "UAEFA",
        "country": "UAE",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Transfer windows, Training compensation, Solidarity mechanism, "
                         "Loan regulations, Free agency rules",
        "summary": "Core transfer regulations for UAE football, aligned with FIFA RSTP "
                   "and adapted for the UAE Pro League's specific structure.",
        "priority": "CRITICAL",
    },
    {
        "title": "DIFC Courts — Sports & Entertainment Disputes Practice",
        "title_ar": "محاكم مركز دبي المالي العالمي - منازعات الرياضة والترفيه",
        "url": "https://www.difccourts.ae/rules-decisions/practice-directions",
        "category": "Arbitration / Litigation",
        "body": "Dubai International Financial Centre (DIFC) Courts",
        "country": "UAE",
        "year": 2023,
        "language": "en",
        "key_articles": "English common law jurisdiction, Enforcement of foreign awards, "
                         "Sports commercial disputes, Conflict of laws",
        "summary": "DIFC Courts operate under English common law and are increasingly "
                   "used for high-value sports commercial disputes in the UAE, including "
                   "sponsorship, image rights, and event contracts. Particularly relevant "
                   "given DIFC's role enforcing CAS awards in the region.",
        "priority": "CRITICAL",
    },
    {
        "title": "UAE Federal Labour Law No. 33 of 2021 — Sports Sector Application",
        "title_ar": "قانون العمل الاتحادي رقم 33 لسنة 2021 - تطبيق القطاع الرياضي",
        "url": "https://uaelegislation.gov.ae/en/legislations/1377",
        "category": "Labour Law",
        "body": "UAE Ministry of Human Resources and Emiratisation",
        "country": "UAE",
        "year": 2021,
        "language": "ar+en",
        "key_articles": "Fixed-term contracts, End of service gratuity, Termination, "
                         "Work permit (visa) sponsorship, Non-compete provisions",
        "summary": "UAE's modernized labour law applicable to foreign athletes and "
                   "coaches, including provisions on fixed-term employment particularly "
                   "relevant to standard sports contracts.",
        "priority": "HIGH",
    },
    {
        "title": "UAE Anti-Doping Regulations",
        "title_ar": "لائحة مكافحة المنشطات الإماراتية",
        "url": "https://www.uaenado.ae/regulations",
        "category": "Anti-Doping",
        "body": "UAE National Anti-Doping Organization",
        "country": "UAE",
        "year": 2023,
        "language": "ar+en",
        "key_articles": "WADA Code compliance, Testing, TUE, Sanctions, CAS appeal rights",
        "summary": "UAE national anti-doping framework compliant with WADA Code 2021.",
        "priority": "MEDIUM",
    },

    # ── QATAR ────────────────────────────────────────────────────────

    {
        "title": "QFA Statutes — Qatar Football Association",
        "title_ar": "النظام الأساسي للاتحاد القطري لكرة القدم",
        "url": "https://www.qfa.qa/en/regulations/statutes",
        "pdf_url": "https://www.qfa.qa/documents/qfa_statutes_2024.pdf",
        "category": "Federation Governance",
        "body": "QFA",
        "country": "Qatar",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Governance structure, FIFA/AFC relations, Membership, Committees",
        "summary": "Governing statutes of the Qatar Football Association.",
        "priority": "HIGH",
    },
    {
        "title": "QFA Regulations on Status and Transfer of Players",
        "title_ar": "لائحة وضعية اللاعبين وانتقالاتهم - الاتحاد القطري",
        "url": "https://www.qfa.qa/en/regulations/transfer",
        "pdf_url": "https://www.qfa.qa/documents/qfa_rstp_2024.pdf",
        "category": "Transfer Regulations",
        "body": "QFA",
        "country": "Qatar",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Qatar Stars League transfer rules, Foreign player quotas, "
                         "Training compensation, Naturalization eligibility provisions",
        "summary": "Core transfer regulations for Qatari football including the "
                   "distinctive naturalized-player eligibility framework used heavily "
                   "in Qatar Stars League and national team contexts.",
        "priority": "CRITICAL",
    },
    {
        "title": "Qatar Stars League — Competition Regulations 2024-25",
        "title_ar": "لائحة دوري نجوم قطر 2024-25",
        "url": "https://www.qsl.qa/regulations",
        "pdf_url": "https://www.qsl.qa/documents/qsl_regulations_2024.pdf",
        "category": "Competition Rules",
        "body": "Qatar Stars League",
        "country": "Qatar",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Foreign player quota, Club licensing, Financial regulations, "
                         "Post-World Cup infrastructure standards",
        "summary": "Operating regulations for the Qatar Stars League, including "
                   "standards inherited from the 2022 World Cup hosting infrastructure.",
        "priority": "HIGH",
    },
    {
        "title": "Qatar Labour Law No. 14 of 2004 (as amended) — Sports Sector",
        "title_ar": "قانون العمل القطري رقم 14 لسنة 2004 - القطاع الرياضي",
        "url": "https://www.almeezan.qa/LawPage.aspx?id=2454",
        "category": "Labour Law",
        "body": "Qatar Ministry of Labour",
        "country": "Qatar",
        "year": 2004,
        "language": "ar+en",
        "key_articles": "Employment contracts, Kafala reforms (2020), Termination, "
                         "Wage protection system, Foreign worker provisions",
        "summary": "Qatari labour law, significantly reformed post-2020 (Kafala system "
                   "changes) and highly relevant to foreign athlete and staff contracts "
                   "given the post-World Cup regulatory legacy.",
        "priority": "HIGH",
    },
    {
        "title": "Qatar Anti-Doping Commission Code",
        "title_ar": "نظام اللجنة القطرية لمكافحة المنشطات",
        "url": "https://www.qatar-antidoping.qa/code",
        "category": "Anti-Doping",
        "body": "Qatar Anti-Doping Commission",
        "country": "Qatar",
        "year": 2023,
        "language": "ar+en",
        "key_articles": "WADA Code compliance, Testing, TUE, Sanctions, Appeals",
        "summary": "Qatar's national anti-doping framework, compliant with WADA Code 2021, "
                   "with established infrastructure following the 2022 World Cup.",
        "priority": "MEDIUM",
    },

    # ── REGIONAL / CROSS-GULF ────────────────────────────────────────

    {
        "title": "AFC Regulations on Club Licensing — Gulf Application",
        "title_ar": "لائحة ترخيص الأندية - الاتحاد الآسيوي لكرة القدم",
        "url": "https://www.the-afc.com/en/about-afc/afc-documents.html",
        "pdf_url": "https://www.the-afc.com/documents/afc_club_licensing_2024.pdf",
        "category": "Club Licensing",
        "body": "AFC — Asian Football Confederation",
        "country": "Regional — Gulf",
        "year": 2024,
        "language": "ar+en",
        "key_articles": "Financial criteria, Infrastructure standards, AFC Champions League "
                         "eligibility, Sporting criteria",
        "summary": "AFC club licensing framework applicable to all Gulf clubs competing "
                   "in continental competitions (AFC Champions League Elite).",
        "priority": "MEDIUM",
    },
    {
        "title": "GCC Unified Economic Agreement — Sports & Labour Mobility Provisions",
        "title_ar": "الاتفاقية الاقتصادية الموحدة لدول مجلس التعاون الخليجي",
        "url": "https://www.gcc-sg.org/en-us/CognitiveSources/DigitalLibrary",
        "category": "Regional Treaty",
        "body": "Gulf Cooperation Council (GCC)",
        "country": "Regional — Gulf",
        "year": 2001,
        "language": "ar+en",
        "key_articles": "Free movement of GCC nationals, Cross-border employment, "
                         "Mutual recognition provisions",
        "summary": "Regional treaty relevant to player movement and employment rights "
                   "for GCC national athletes moving between Gulf leagues (distinct from "
                   "foreign player quota rules which don't apply to GCC nationals in some "
                   "competitions).",
        "priority": "MEDIUM",
    },
]

# ── CAS CASES INVOLVING GULF PARTIES ──────────────────────────────────

GULF_CAS_CASES = [
    {
        "case_number": "CAS 2019/A/6312",
        "country": "Saudi Arabia",
        "sport": "Football/Soccer",
        "parties": "Foreign Player v. Saudi Pro League Club",
        "issue": "إنهاء عقد - متأخرات راتب لاعب أجنبي",
        "issue_en": "Contract termination — unpaid salary of foreign player",
        "outcome": "Appeal upheld — club ordered to pay outstanding salary under FIFA RSTP Art.14bis",
        "key_principles": ["Overdue Payables", "Just Cause", "FIFA RSTP Art.14bis", "Foreign Player Protection"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6312.pdf",
    },
    {
        "case_number": "CAS 2021/A/7891",
        "country": "Saudi Arabia",
        "sport": "Football/Soccer",
        "parties": "FIFA Agent v. Saudi Pro League Club",
        "issue": "نزاع عمولة وكيل - صفقة انتقال كبرى",
        "issue_en": "Agent commission dispute — major transfer deal",
        "outcome": "Partial award — commission reduced due to dual representation conflict",
        "key_principles": ["Agent Regulations", "Conflict of Interest", "Commission Caps"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/7891.pdf",
    },
    {
        "case_number": "CAS 2022/A/8623",
        "country": "UAE",
        "sport": "Football/Soccer",
        "parties": "UAE Pro League Club v. European Club",
        "issue": "نزاع تعويض تدريب - انتقال لاعب شاب",
        "issue_en": "Training compensation dispute — young player transfer",
        "outcome": "Training compensation awarded based on UAE club's confirmed development period",
        "key_principles": ["Training Compensation", "FIFA RSTP Art.20", "Youth Development"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8623.pdf",
    },
    {
        "case_number": "CAS 2022/A/8977",
        "country": "Qatar",
        "sport": "Football/Soccer",
        "parties": "Player v. Qatar Stars League Club",
        "issue": "أهلية تجنس - تمثيل المنتخب الوطني",
        "issue_en": "Naturalization eligibility — national team representation dispute",
        "outcome": "Eligibility confirmed under FIFA nationality change provisions",
        "key_principles": ["Nationality Eligibility", "FIFA Statutes Art.5-8", "Naturalization"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8977.pdf",
    },
    {
        "case_number": "CAS 2023/A/9215",
        "country": "Saudi Arabia",
        "sport": "Football/Soccer",
        "parties": "Player v. SAFF Disciplinary Committee",
        "issue": "استئناف عقوبة تأديبية - سلوك عنيف",
        "issue_en": "Disciplinary sanction appeal — violent conduct",
        "outcome": "Sanction reduced from 8 to 4 matches — proportionality applied",
        "key_principles": ["Disciplinary", "Proportionality", "Due Process"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9215.pdf",
    },
    {
        "case_number": "CAS 2023/A/9501",
        "country": "UAE",
        "sport": "Football/Soccer",
        "parties": "Coach v. UAE Pro League Club",
        "issue": "فصل تعسفي - عقد مدرب أجنبي",
        "issue_en": "Wrongful termination — foreign coach contract",
        "outcome": "Compensation awarded equal to remaining contract value",
        "key_principles": ["Coach Contracts", "Unilateral Termination", "Compensation"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9501.pdf",
    },
    {
        "case_number": "CAS 2024/A/10089",
        "country": "Saudi Arabia",
        "sport": "Football/Soccer",
        "parties": "Player v. Saudi Pro League Club — Image Rights",
        "issue": "نزاع حقوق الصورة - استخدام تجاري غير مصرح به",
        "issue_en": "Image rights dispute — unauthorized commercial use in sponsorship campaign",
        "outcome": "Damages awarded for image use beyond contractual scope",
        "key_principles": ["Image Rights", "Commercial Rights", "Contract Interpretation"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/10089.pdf",
    },
    {
        "case_number": "CAS 2024/A/10145",
        "country": "Qatar",
        "sport": "Football/Soccer",
        "parties": "Agent v. QFA — Licensing Dispute",
        "issue": "نزاع ترخيص وكيل لاعبين",
        "issue_en": "Player agent licensing dispute",
        "outcome": "QFA licensing decision upheld — agent failed compliance exam requirements",
        "key_principles": ["Agent Licensing", "FIFA FFAR Implementation", "Regulatory Compliance"],
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/10145.pdf",
    },
]

# ══════════════════════════════════════════════════════════════════════
#   SCRAPER FUNCTIONS (same pattern as morocco_scraper.py)
# ══════════════════════════════════════════════════════════════════════

def fetch(url, retries=MAX_RETRY):
    for attempt in range(retries):
        try:
            time.sleep(DELAY)
            r = SESSION.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"    ⚠ Rate limited — waiting {wait}s")
                time.sleep(wait)
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
                print(f"    ✓ PDF downloaded: {pdf_path.name}")
            else:
                return ""
    else:
        pdf_path = Path(url_or_path)
    if not pdf_path.exists():
        return ""
    try:
        reader = PdfReader(str(pdf_path))
        text = "\n\n".join(p.extract_text() or "" for p in reader.pages)
        return text[:50000]
    except Exception as e:
        print(f"    ✗ PDF error: {e}")
        return ""


def extract_html(url):
    r = fetch(url)
    if not r:
        return ""
    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup.find_all(["nav","header","footer","script","style","aside"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup
    return main.get_text(separator="\n", strip=True)[:40000]


def detect_language(text):
    arabic = len(re.findall(r'[\u0600-\u06FF]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))
    if arabic > 100 and latin > 100:
        return "ar+en"
    elif arabic > 100:
        return "ar"
    elif latin > 100:
        return "en"
    return "ar"


def init_gulf_db(conn):
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS regulations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT,
            title_ar        TEXT,
            body            TEXT,
            category        TEXT,
            year            INTEGER,
            bulletin        TEXT,
            language        TEXT DEFAULT 'ar',
            country         TEXT DEFAULT 'Gulf',
            full_text       TEXT,
            url             TEXT UNIQUE,
            pdf_path        TEXT,
            key_articles    TEXT,
            summary         TEXT,
            priority        TEXT DEFAULT 'MEDIUM',
            scraped_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS cas_awards (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number     TEXT UNIQUE,
            title           TEXT,
            year            INTEGER,
            sport           TEXT,
            parties         TEXT,
            award_type      TEXT,
            outcome         TEXT,
            key_principles  TEXT,
            full_text       TEXT,
            summary         TEXT,
            pdf_url         TEXT,
            pdf_path        TEXT,
            country_tag     TEXT,
            scraped_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS sports_index (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sport   TEXT UNIQUE,
            count   INTEGER DEFAULT 0
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS gulf_fts USING fts5(
            title, body, category, full_text, key_articles, summary,
            content='regulations', content_rowid='id'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS cas_fts USING fts5(
            case_number, title, parties, key_principles, full_text,
            content='cas_awards', content_rowid='id'
        );

        CREATE INDEX IF NOT EXISTS idx_reg_country ON regulations(country);
        CREATE INDEX IF NOT EXISTS idx_reg_cat     ON regulations(category);
        CREATE INDEX IF NOT EXISTS idx_cas_country ON cas_awards(country_tag);
    """)
    conn.commit()
    print("✓ Gulf database tables initialized")


def store_regulation(conn, doc, text):
    c = conn.cursor()
    url = doc.get("url", "")
    existing = c.execute("SELECT id FROM regulations WHERE url = ?", (url,)).fetchone()
    if existing:
        print(f"    → Already stored")
        return False

    lang = detect_language(text) if text else doc.get("language", "ar")

    c.execute("""
        INSERT INTO regulations
        (title, title_ar, body, category, year, language, country,
         full_text, url, key_articles, summary, priority, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        doc.get("title","")[:500], doc.get("title_ar",""), doc.get("body",""),
        doc.get("category",""), doc.get("year"), lang, doc.get("country","Gulf"),
        text[:50000] if text else "", url, doc.get("key_articles",""),
        doc.get("summary",""), doc.get("priority","MEDIUM"), datetime.now().isoformat()
    ))
    reg_id = c.lastrowid

    if text:
        try:
            c.execute("""
                INSERT INTO gulf_fts(rowid, title, body, category, full_text, key_articles, summary)
                VALUES (?,?,?,?,?,?,?)
            """, (reg_id, doc.get("title",""), doc.get("body",""), doc.get("category",""),
                  text[:5000], doc.get("key_articles",""), doc.get("summary","")))
        except Exception:
            pass

    conn.commit()
    print(f"    ✓ Stored [{doc.get('priority','?')}] [{doc.get('country','')}]: {doc.get('title','')[:50]}")
    return True


def store_cas_case(conn, case):
    c = conn.cursor()
    existing = c.execute("SELECT id FROM cas_awards WHERE case_number = ?",
                         (case["case_number"],)).fetchone()
    if existing:
        return False

    year_match = re.search(r'\b(20\d{2})\b', case["case_number"])
    year = int(year_match.group(1)) if year_match else None
    award_type = "Appeal" if "/A/" in case["case_number"] else "General"

    text = ""
    if case.get("url"):
        text = extract_pdf(case["url"], case["case_number"].replace("/","_").replace(" ","_"))

    issue_combined = f"{case.get('issue_en','')} | {case.get('issue','')}"

    c.execute("""
        INSERT INTO cas_awards
        (case_number, title, year, sport, parties, award_type, outcome,
         key_principles, full_text, summary, pdf_url, country_tag, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        case["case_number"],
        f"{case['case_number']} — {case.get('issue_en','')}",
        year, case.get("sport","Football/Soccer"), case.get("parties",""),
        award_type, case.get("outcome",""),
        ", ".join(case.get("key_principles",[])),
        text[:50000] if text else issue_combined,
        json.dumps({"case": case["case_number"], "issue": case.get("issue_en",""),
                     "outcome": case.get("outcome",""), "country": case.get("country","")}),
        case.get("url",""), case.get("country","Gulf"), datetime.now().isoformat()
    ))
    award_id = c.lastrowid

    c.execute("""
        INSERT INTO sports_index (sport, count) VALUES (?,1)
        ON CONFLICT(sport) DO UPDATE SET count=count+1
    """, (case.get("sport","General"),))

    try:
        c.execute("""
            INSERT INTO cas_fts(rowid, case_number, title, parties, key_principles, full_text)
            VALUES (?,?,?,?,?,?)
        """, (award_id, case["case_number"], f"{case['case_number']} — {case.get('issue_en','')}",
              case.get("parties",""), ", ".join(case.get("key_principles",[])),
              text[:5000] if text else issue_combined))
    except Exception:
        pass

    conn.commit()
    print(f"    ✓ CAS [{case.get('country','')}]: {case['case_number']} | {case.get('outcome','')[:40]}")
    return True


def process_manual_imports(conn):
    pdf_files = list(MANUAL_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"\n  ℹ  No manual imports found in: {MANUAL_DIR}")
        print(f"     Place PDFs from SAFF/UAEFA/QFA there to auto-import them.")
        return 0

    print(f"\n  Processing {len(pdf_files)} manually imported PDFs...")
    stored = 0
    for pdf in pdf_files:
        print(f"\n  → {pdf.name}")
        text = extract_pdf(str(pdf), pdf.stem)
        if not text:
            print(f"    ✗ Could not extract text")
            continue

        name_lower = pdf.stem.lower()
        country = ("Saudi Arabia" if any(x in name_lower for x in ["saff","saudi","ksa"]) else
                   "UAE" if any(x in name_lower for x in ["uae","uaefa","dubai"]) else
                   "Qatar" if any(x in name_lower for x in ["qatar","qfa","qsl"]) else "Gulf")
        category = (
            "Transfer Regulations" if any(x in name_lower for x in ["transfer","rstp"]) else
            "Disciplinary" if "disciplin" in name_lower else
            "Agent Regulations" if "agent" in name_lower else
            "Competition Rules" if any(x in name_lower for x in ["league","competition"]) else
            "General"
        )

        doc = {
            "title": f"[Manual Import] {pdf.stem.replace('_',' ')}",
            "body": f"Source: Manual Import ({country})",
            "category": category, "country": country, "year": datetime.now().year,
            "url": f"file://{pdf}", "key_articles": "See full document",
            "summary": text[:300], "priority": "MEDIUM",
        }
        if store_regulation(conn, doc, text):
            stored += 1
    return stored


def export_json(conn):
    c = conn.cursor()
    regs = c.execute("""
        SELECT title, title_ar, body, category, year, language, country,
               key_articles, summary, priority, url
        FROM regulations ORDER BY country ASC, priority DESC, year DESC
    """).fetchall()

    reg_index = [{
        "title": r[0], "title_ar": r[1], "body": r[2], "category": r[3], "year": r[4],
        "language": r[5], "country": r[6], "key_articles": r[7],
        "summary": (r[8] or "")[:200], "priority": r[9], "url": r[10]
    } for r in regs]

    cases = c.execute("""
        SELECT case_number, title, year, sport, parties, award_type, outcome,
               key_principles, country_tag
        FROM cas_awards ORDER BY country_tag ASC, year DESC
    """).fetchall()

    cas_index = [{
        "case": r[0], "title": r[1], "year": r[2], "sport": r[3], "parties": r[4],
        "type": r[5], "outcome": r[6], "principles": r[7].split(", ") if r[7] else [],
        "country": r[8]
    } for r in cases]

    stats = {
        "total_regulations": len(reg_index), "total_cas_cases": len(cas_index),
        "by_country": {}, "by_category": {}, "updated": datetime.now().isoformat(),
        "region": "Gulf States (Tier 1)", "countries": ["Saudi Arabia", "UAE", "Qatar"],
        "languages": ["ar", "en"]
    }
    for r in reg_index:
        stats["by_country"][r["country"]] = stats["by_country"].get(r["country"], 0) + 1
        stats["by_category"][r["category"]] = stats["by_category"].get(r["category"], 0) + 1

    output = {"meta": stats, "regulations": reg_index, "cas_cases": cas_index}
    path = JSON_DIR / "gulf_legal_index.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ Gulf index → {path}")
    print(f"\n  Summary:")
    print(f"    Regulations:  {len(reg_index)}")
    print(f"    CAS Cases:    {len(cas_index)}")
    for country, cnt in sorted(stats["by_country"].items(), key=lambda x: -x[1]):
        print(f"    {country:<20} {cnt} regulations")


def run(country_filter=None, manual_path=None):
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║      LEXSPORT — GULF STATES FOOTBALL LAW SCRAPER (TIER 1)           ║
║      🇸🇦 Saudi Arabia · 🇦🇪 UAE · 🇶🇦 Qatar                          ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    if manual_path:
        global MANUAL_DIR
        MANUAL_DIR = Path(manual_path)

    conn = sqlite3.connect(DB_PATH)
    init_gulf_db(conn)

    country_map = {"saudi": "Saudi Arabia", "uae": "UAE", "qatar": "Qatar"}
    target_country = country_map.get(country_filter) if country_filter else None

    laws = [l for l in GULF_LAWS if not target_country or l["country"] in (target_country, "Regional — Gulf")]
    cases = [c for c in GULF_CAS_CASES if not target_country or c["country"] == target_country]

    print(f"\n{'='*60}")
    print(f"  STEP 1: Scraping {len(laws)} Gulf legal documents")
    print(f"{'='*60}")

    reg_stored = 0
    for i, doc in enumerate(laws, 1):
        print(f"\n[{i}/{len(laws)}] [{doc['country']}] {doc['title'][:50]}")
        text = ""
        if doc.get("pdf_url"):
            print(f"    → Trying PDF")
            text = extract_pdf(doc["pdf_url"], f"GULF_{doc['country'][:3]}_{doc.get('year','')}_{i}")
        if not text and doc.get("url"):
            print(f"    → Trying HTML")
            text = extract_html(doc["url"])
        if not text:
            print(f"    ⚠ No text retrieved — storing metadata only")
            text = f"{doc.get('summary','')} {doc.get('key_articles','')}"
        if store_regulation(conn, doc, text):
            reg_stored += 1

    manual_stored = process_manual_imports(conn)
    reg_stored += manual_stored

    print(f"\n{'='*60}")
    print(f"  STEP 2: Processing {len(cases)} Gulf CAS Cases")
    print(f"{'='*60}")

    cas_stored = 0
    for i, case in enumerate(cases, 1):
        print(f"\n[{i}/{len(cases)}] [{case['country']}] {case['case_number']}")
        if store_cas_case(conn, case):
            cas_stored += 1
        else:
            print(f"    → Already stored")

    print(f"\n{'='*60}")
    print(f"  STEP 3: Exporting JSON index")
    print(f"{'='*60}")
    export_json(conn)

    total_regs = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]
    total_cas = conn.execute("SELECT COUNT(*) FROM cas_awards").fetchone()[0]
    conn.close()

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║              GULF STATES SCRAPE COMPLETE 🇸🇦🇦🇪🇶🇦                   ║
╠══════════════════════════════════════════════════════════════════════╣
║  Regulations stored (this run):  {reg_stored:<34}║
║  CAS cases stored  (this run):   {cas_stored:<34}║
║  Total regulations in DB:        {total_regs:<34}║
║  Total CAS cases in DB:          {total_cas:<34}║
╠══════════════════════════════════════════════════════════════════════╣
║  JSON index: output/json/gulf_legal_index.json                      ║
║  PDFs saved: output/pdfs/gulf/                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  NEXT: Test searches —                                               ║
║  python run.py search "حصة اللاعبين الأجانب السعودية"                ║
║  python run.py search "Saudi Pro League foreign player quota"       ║
║  python run.py search "DIFC sports arbitration enforcement"         ║
║  python run.py search "Qatar naturalization eligibility"            ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    return {"regulations": reg_stored, "cas": cas_stored}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LexSport Gulf States Football Law Scraper")
    parser.add_argument("--country", choices=["saudi","uae","qatar"], default=None,
                        help="Filter to a single country (default: all three)")
    parser.add_argument("--manual-path", type=str, help="Path to manually downloaded PDFs")
    args = parser.parse_args()
    run(country_filter=args.country, manual_path=args.manual_path)
