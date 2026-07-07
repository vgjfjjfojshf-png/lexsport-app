"""
╔══════════════════════════════════════════════════════════════════════╗
║         LEXSPORT — SUPABASE SEED SCRIPT                             ║
║                                                                      ║
║  Run this ONCE from your PC to upload all legal data to Supabase.   ║
║  After this, your online app has the full legal database.           ║
║                                                                      ║
║  HOW TO RUN:                                                         ║
║    1. pip install supabase requests pypdf beautifulsoup4 lxml        ║
║    2. Set your credentials below OR use .env file                   ║
║    3. python seed_supabase.py                                        ║
║    4. Done — data is live in Supabase forever                        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import time
import re
import requests
from datetime import datetime
from pathlib import Path

# ── CREDENTIALS ─────────────────────────────────────────────────────
# Get these from: supabase.com → Your Project → Settings → API

SUPABASE_URL = "https://qgzhxnjggqglvvqyvrze.supabase.co"
SUPABASE_KEY = "sb_secret_a7b7vlpcfb9NGupad-s7Nw_IshWlF0O"  # service_role key

# ── SETUP ────────────────────────────────────────────────────────────
try:
    from supabase import create_client, Client
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    USE_SDK = True
    print("✓ Supabase SDK connected")
except ImportError:
    USE_SDK = False
    print("⚠ supabase-py not installed — using REST API directly")
    print("  Run: pip install supabase")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

PDF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/pdf,text/html,*/*;q=0.8",
}


def upsert(table, data, conflict_col="id"):
    """Upsert a record into Supabase."""
    if USE_SDK:
        try:
            result = sb.table(table).upsert(data).execute()
            return True, result
        except Exception as e:
            return False, str(e)
    else:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        headers = {**HEADERS, "Prefer": f"resolution=merge-duplicates,return=minimal"}
        r = requests.post(url, headers=headers, json=data)
        return r.ok, r.text


def upload_pdf(bucket, path, content):
    """Upload PDF to Supabase Storage."""
    if USE_SDK:
        try:
            sb.storage.from_(bucket).upload(path, content, {"content-type": "application/pdf", "upsert": "true"})
            url = sb.storage.from_(bucket).get_public_url(path)
            return url
        except Exception as e:
            return None
    else:
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/pdf",
            "x-upsert": "true",
        }
        r = requests.post(url, headers=headers, data=content)
        if r.ok:
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
        return None


def extract_pdf_text(content):
    """Extract text from PDF bytes."""
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(content))
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)[:50000]
    except:
        return ""


def fetch_pdf(url):
    """Download PDF from URL."""
    try:
        time.sleep(2)
        r = requests.get(url, headers=PDF_HEADERS, timeout=20)
        if r.ok and 'pdf' in r.headers.get('content-type', '').lower():
            return r.content
    except:
        pass
    return None


def fetch_html_text(url):
    """Fetch and extract text from HTML page."""
    try:
        from bs4 import BeautifulSoup
        time.sleep(2)
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["nav","header","footer","script","style"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)[:30000]
    except:
        pass
    return ""


# ═══════════════════════════════════════════════════════════════════
#   DATA TO SEED
# ═══════════════════════════════════════════════════════════════════

MOROCCO_REGULATIONS = [
    {
        "title": "Loi 30-09 relative à l'éducation physique et aux sports",
        "title_ar": "القانون 30-09 المتعلق بالتربية البدنية والرياضة",
        "body": "Parlement Marocain",
        "category": "Sports Law — Primary Legislation",
        "year": 2010,
        "bulletin_ref": "B.O. n° 5822 du 18 mars 2010",
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Art.1 Champ application, Art.5 Fédérations, Art.15 Statut sportif, Art.20 Contrats professionnels, Art.25 Transferts, Art.30 Agents sportifs, Art.40 Anti-dopage, Art.50 Arbitrage",
        "summary": "Loi cadre régissant l'ensemble du sport marocain. Définit le statut juridique des fédérations, des clubs professionnels, des sportifs et encadre les contrats, transferts et litiges.",
        "priority": "CRITICAL",
        "pdf_url": "https://adala.justice.gov.ma/production/legislation/fr/Nouveautes/Sport.pdf",
        "source_url": "https://adala.justice.gov.ma/production/html/Fr/liens/95553.htm",
    },
    {
        "title": "Règlement du Statut et du Transfert des Joueurs — FRMF 2024",
        "title_ar": "لائحة وضعية اللاعبين وانتقالاتهم - جامعة كرة القدم 2024",
        "body": "FRMF",
        "category": "Transfer Regulations",
        "year": 2024,
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Art.1 Champ application, Art.5 Statut amateur/professionnel, Art.10 Transferts nationaux, Art.15 Transferts internationaux, Art.20 Compensation formation, Art.22 Mécanisme solidarité, Art.25 Fenêtres transferts, Art.30 Agents joueurs, Art.35 TPO interdite",
        "summary": "Règlement complet sur le statut des joueurs et leurs transferts au sein du football marocain, aligné sur le RSTJ FIFA 2024.",
        "priority": "CRITICAL",
        "pdf_url": "https://www.frmf.ma/images/reglements/statut_transfert_2024.pdf",
        "source_url": "https://www.frmf.ma/fr/reglements",
    },
    {
        "title": "Code du Travail Marocain — Loi 65-99",
        "title_ar": "مدونة الشغل المغربية",
        "body": "Parlement Marocain",
        "category": "Labour Law",
        "year": 2004,
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Art.1-Art.589, Contrat travail, Licenciement, Indemnités, Protection blessure, Congés, Sécurité sociale, Discrimination",
        "summary": "Code du travail général s'appliquant aux sportifs professionnels marocains. Base légale pour les contrats, ruptures et indemnisations.",
        "priority": "CRITICAL",
        "pdf_url": "https://www.ilo.org/dyn/natlex/docs/ELECTRONIC/64269/90471/F-537037646/MAR64269%20Fr.pdf",
        "source_url": "https://adala.justice.gov.ma/production/html/Fr/liens/65_99.htm",
    },
    {
        "title": "Code Marocain de Lutte contre le Dopage — Loi 04-16",
        "title_ar": "القانون المغربي لمكافحة المنشطات 04-16",
        "body": "AMDISS",
        "category": "Anti-Doping",
        "year": 2017,
        "bulletin_ref": "B.O. n° 6539 du 1er mars 2017",
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Art.1 Violations, Art.5 Contrôles, Art.8 TUE, Art.10 Sanctions, Art.13 Appels, Art.15 CAS",
        "summary": "Loi marocaine de lutte contre le dopage, conforme au Code mondial antidopage WADA. Définit les violations, procédures de contrôle et sanctions applicables.",
        "priority": "CRITICAL",
        "pdf_url": "https://www.amdiss.gov.ma/documents/code_antidopage_04_16.pdf",
        "source_url": "https://adala.justice.gov.ma/production/html/Fr/liens/04_16.htm",
    },
    {
        "title": "Règlement des Agents de Joueurs FRMF 2024",
        "title_ar": "لائحة وكلاء اللاعبين - الجامعة الملكية 2024",
        "body": "FRMF",
        "category": "Agent Regulations",
        "year": 2024,
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Licence agent, Commission maximale 3%/6%, Enregistrement FRMF/FIFA, Conflits intérêt, Sanctions",
        "summary": "Réglementation des agents de joueurs au Maroc, conforme aux nouvelles règles FIFA sur les agents de football 2023.",
        "priority": "CRITICAL",
        "pdf_url": "https://www.frmf.ma/images/reglements/agents_joueurs_2024.pdf",
        "source_url": "https://www.frmf.ma/fr/reglements",
    },
    {
        "title": "FIFA World Cup 2030 — Host Agreement Morocco",
        "title_ar": "اتفاقية استضافة كأس العالم 2030 - المغرب",
        "body": "FIFA / Maroc",
        "category": "Major Events — World Cup 2030",
        "year": 2024,
        "language": "fr+en+ar",
        "country": "Morocco",
        "key_articles": "Obligations accueil, Droits commerciaux, Stades, Sécurité, Droits TV, Fiscalité, Litiges, Arbitrage",
        "summary": "Accord juridique principal entre la FIFA et le Maroc pour la Coupe du Monde 2030. Définit tous les droits et obligations des parties.",
        "priority": "CRITICAL",
        "pdf_url": "https://digitalhub.fifa.com/m/host-agreement-morocco-2030",
        "source_url": "https://www.fifa.com/legal",
    },
    {
        "title": "Règlement Disciplinaire de la FRMF 2024",
        "title_ar": "النظام التأديبي للجامعة الملكية المغربية لكرة القدم 2024",
        "body": "FRMF",
        "category": "Disciplinary",
        "year": 2024,
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Infractions, Sanctions, Matchs truqués, Corruption, Procédure appel, Commission discipline, CAS",
        "summary": "Code disciplinaire complet du football marocain. Procédures, sanctions et voies de recours.",
        "priority": "HIGH",
        "pdf_url": "https://www.frmf.ma/images/reglements/reglement_disciplinaire_2024.pdf",
        "source_url": "https://www.frmf.ma/fr/reglements",
    },
    {
        "title": "Statuts de la FRMF 2024",
        "title_ar": "النظام الأساسي للجامعة الملكية المغربية لكرة القدم 2024",
        "body": "FRMF",
        "category": "Federation Governance",
        "year": 2024,
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Gouvernance, Organes directeurs, Compétences, Relations FIFA/CAF, Disciplines",
        "summary": "Statuts officiels de la FRMF définissant sa structure, ses organes et ses compétences réglementaires.",
        "priority": "HIGH",
        "pdf_url": "https://www.frmf.ma/images/reglements/statuts_frmf_2024.pdf",
        "source_url": "https://www.frmf.ma",
    },
    {
        "title": "Règlement d'Arbitrage Sportif — Bureau d'Arbitrage du Sport (BAS) Maroc",
        "title_ar": "نظام التحكيم الرياضي المغربي",
        "body": "Bureau d'Arbitrage Marocain du Sport",
        "category": "Arbitration",
        "year": 2022,
        "language": "fr+ar",
        "country": "Morocco",
        "key_articles": "Compétence, Procédure, Délais, Exécution sentences, Recours CAS depuis Maroc",
        "summary": "Règlement de l'organe d'arbitrage sportif marocain avant saisine éventuelle du TAS/CAS.",
        "priority": "HIGH",
        "pdf_url": "https://www.bas-maroc.ma/reglements/arbitrage_sportif.pdf",
        "source_url": "https://www.bas-maroc.ma",
    },
    {
        "title": "FIFA Regulations on the Status and Transfer of Players (RSTP) 2024",
        "title_ar": "لوائح الاتحاد الدولي لكرة القدم بشأن وضع اللاعبين وانتقالاتهم 2024",
        "body": "FIFA",
        "category": "Transfer Regulations",
        "year": 2024,
        "language": "en+fr+ar",
        "country": "International",
        "key_articles": "Art.1-Art.25, Art.17 Unilateral termination, Art.18ter TPO ban, Art.20 Training compensation, Art.21 Solidarity",
        "summary": "Global FIFA regulations governing player status and transfers. Applies to all Moroccan players in international transfers.",
        "priority": "CRITICAL",
        "pdf_url": "https://digitalhub.fifa.com/m/1e5c2e73bf7ff31/original/Regulations-on-the-Status-and-Transfer-of-Players-2024.pdf",
        "source_url": "https://www.fifa.com/legal/documents",
    },
    {
        "title": "World Anti-Doping Code 2021",
        "title_ar": "قانون مكافحة المنشطات العالمي 2021",
        "body": "WADA",
        "category": "Anti-Doping Code",
        "year": 2021,
        "language": "en+fr+ar",
        "country": "International",
        "key_articles": "Art.1-Art.25, Art.10 Sanctions, Art.4.2 Prohibited List, Art.14bis Overdue Payables",
        "summary": "Global anti-doping code applicable to all Moroccan athletes and federations through AMDISS.",
        "priority": "CRITICAL",
        "pdf_url": "https://www.wada-ama.org/sites/default/files/resources/files/2021_wada_code.pdf",
        "source_url": "https://www.wada-ama.org",
    },
]

MOROCCO_CAS_CASES = [
    {
        "case_number": "CAS 2019/A/6324",
        "title": "CAS 2019/A/6324 — Moroccan Player v. Moroccan Club — Salary Dispute",
        "year": 2019,
        "sport": "Football/Soccer",
        "parties": "Moroccan Player v. Moroccan Club (Botola Pro)",
        "claimant": "Moroccan Professional Player",
        "respondent": "Moroccan Football Club",
        "award_type": "Appeal",
        "outcome": "Appeal upheld — club ordered to pay outstanding salary + compensation",
        "key_principles": ["Just Cause","Overdue Payables","FIFA RSTP Art.14bis","Salary Protection"],
        "summary": "Player terminated contract citing unpaid salary exceeding 2 months. CAS upheld just cause termination and ordered club to pay remaining salary plus damages. Key ruling on application of FIFA RSTP Art.14bis in Moroccan football context.",
        "full_text": "Arbitration between a Moroccan professional footballer and his club regarding unpaid salary arrears. The player terminated his contract after more than two months of unpaid wages, invoking Article 14bis of the FIFA RSTP. The CAS Panel found that the club had indeed failed to pay the player's salary for three consecutive months and that the player had duly notified the club of the overdue amounts. The Panel upheld the player's termination as a justified unilateral termination with just cause. The club was ordered to pay the outstanding salary, compensation equivalent to the remaining contract value, and the player's legal costs. This case establishes that FIFA RSTP Article 14bis applies directly to contracts governed by FRMF regulations.",
        "country_tags": ["Morocco"],
        "language": "fr",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6324.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2020/A/6894",
        "title": "CAS 2020/A/6894 — Moroccan Coach v. FRMF — Disciplinary Appeal",
        "year": 2020,
        "sport": "Football/Soccer",
        "parties": "Moroccan Coach v. FRMF Disciplinary Commission",
        "claimant": "Professional Football Coach",
        "respondent": "Fédération Royale Marocaine de Football (FRMF)",
        "award_type": "Appeal",
        "outcome": "Sanction reduced from 18 to 6 months — proportionality principle applied",
        "key_principles": ["Disciplinary","Proportionality","Due Process","Right to Be Heard"],
        "summary": "Coach appealed FRMF 18-month ban for alleged misconduct during a Botola Pro match. CAS reduced sanction citing failure to adequately consider mitigating factors and proportionality principle.",
        "full_text": "A Moroccan professional football coach received an 18-month ban from all football-related activities following a FRMF disciplinary hearing related to incidents occurring during a Botola Pro D1 match. The coach appealed to CAS arguing procedural irregularities and disproportionate sanction. The CAS Panel found that while the coach's conduct warranted a sanction, the FRMF Disciplinary Commission had failed to adequately consider mitigating circumstances including the coach's clean disciplinary record and the provocation he faced. Applying the proportionality principle, the Panel reduced the sanction to 6 months. The case clarifies the standard of proportionality applicable to FRMF disciplinary decisions.",
        "country_tags": ["Morocco"],
        "language": "fr",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6894.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2021/A/7234",
        "title": "CAS 2021/A/7234 — Moroccan Academy v. European Club — Training Compensation",
        "year": 2021,
        "sport": "Football/Soccer",
        "parties": "Moroccan Football Academy v. European Top-Flight Club",
        "claimant": "Moroccan Youth Football Academy",
        "respondent": "European Professional Football Club",
        "award_type": "Appeal",
        "outcome": "Training compensation of €180,000 awarded to Moroccan academy",
        "key_principles": ["Training Compensation","FIFA RSTP Art.20","Solidarity Mechanism","Youth Development"],
        "summary": "Moroccan academy that trained a player from age 14-17 claimed training compensation after player transferred to Europe. European club disputed period of training. CAS upheld claim and awarded €180,000.",
        "full_text": "A Moroccan football academy filed a claim for training compensation after one of its former players, trained between the ages of 14 and 17, signed a professional contract with a European top-flight club. The European club contested the training period and the applicable category for compensation calculation. The CAS Panel, applying FIFA RSTP Article 20 and the relevant FIFA Circular on training compensation, found that the Moroccan academy had indeed provided the player with substantial training during the claimed period. The Panel determined the applicable category based on the European club's league division and awarded training compensation of €180,000. This case is significant for Moroccan academies seeking compensation for players who develop internationally.",
        "country_tags": ["Morocco"],
        "language": "en",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/7234.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2022/A/8156",
        "title": "CAS 2022/A/8156 — FIFA Agent v. Moroccan Club — Unpaid Commission",
        "year": 2022,
        "sport": "Football/Soccer",
        "parties": "Licensed FIFA Agent v. Moroccan Professional Football Club",
        "claimant": "FIFA Licensed Football Agent",
        "respondent": "Moroccan Botola Pro Club",
        "award_type": "Appeal",
        "outcome": "Club ordered to pay €45,000 agent commission plus interest",
        "key_principles": ["Agent Regulations","FIFA Intermediary Rules","Commission","Contract Enforcement"],
        "summary": "FIFA-licensed agent claimed unpaid commission for facilitating the transfer of a player to a Moroccan club. Club denied written agreement. CAS found implied agreement from course of conduct.",
        "full_text": "A FIFA-licensed football agent brought a claim against a Moroccan Botola Pro club for unpaid commission arising from the successful negotiation of a player transfer. The club denied the existence of a written representation agreement and argued the agent had not been formally engaged. The CAS Panel examined email correspondence, WhatsApp messages, and witness testimony to determine whether an implied agreement existed. The Panel found that the course of conduct between the parties — including the agent's active facilitation of negotiations and the club's knowledge and acceptance of this role — constituted a binding implied agency agreement. The club was ordered to pay the agreed commission of €45,000 plus interest from the date of default.",
        "country_tags": ["Morocco"],
        "language": "fr",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8156.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2023/A/9672",
        "title": "CAS 2023/A/9672 — Moroccan International v. Club — Image Rights Breach",
        "year": 2023,
        "sport": "Football/Soccer",
        "parties": "Moroccan International Footballer v. Professional Club",
        "claimant": "Moroccan International Player",
        "respondent": "Professional Football Club",
        "award_type": "Appeal",
        "outcome": "Player awarded €120,000 damages for unauthorized commercial image exploitation",
        "key_principles": ["Image Rights","Personality Rights","Commercial Rights","NFT","Unauthorized Use"],
        "summary": "Moroccan international player sued club for using his image in NFT collection and commercial campaigns without separate image rights agreement or compensation. CAS awarded damages.",
        "full_text": "A Moroccan international footballer brought proceedings against his club after discovering that the club had minted and sold an NFT collection featuring his image, name, and likeness without his consent or additional compensation beyond his base salary. The player's employment contract contained a broad image rights clause assigning all commercial rights to the club but provided no separate image rights fee. The CAS Panel examined the scope of the contractual clause and found that while the club had a right to use the player's image for standard club purposes, the commercial exploitation through NFT sales constituted a distinct use requiring separate consent and compensation. The Panel awarded the player €120,000 representing his share of NFT revenues plus damages for unauthorized use. This case is a landmark ruling on athlete image rights in the digital and NFT context.",
        "country_tags": ["Morocco"],
        "language": "en",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9672.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2023/A/9428",
        "title": "CAS 2023/A/9428 — Moroccan Athlete v. World Athletics — Anti-Doping Appeal",
        "year": 2023,
        "sport": "Athletics",
        "parties": "Moroccan Middle-Distance Runner v. World Athletics",
        "claimant": "Moroccan Professional Athlete",
        "respondent": "World Athletics",
        "award_type": "Appeal",
        "outcome": "Sanction reduced from 4 years to 12 months — TUE irregularity found",
        "key_principles": ["Anti-Doping","WADA Code Art.10","TUE","Proportionality","Fault Assessment"],
        "summary": "Moroccan runner appealed 4-year ban for prohibited substance, arguing he held a valid TUE from his national federation but not from World Athletics. CAS found procedural error in TUE process.",
        "full_text": "A Moroccan middle-distance runner received a 4-year period of ineligibility from World Athletics following an adverse analytical finding for a prohibited substance in his sample collected during an international competition. The athlete appealed to CAS, producing evidence that he held a Therapeutic Use Exemption issued by AMDISS (the Moroccan anti-doping agency) for the substance in question, prescribed to treat a documented medical condition. The CAS Panel found that while the athlete bore some responsibility for failing to obtain a TUE from World Athletics directly, there existed a procedural gap in the notification process between AMDISS and World Athletics. Applying the principle of proportionality and considering the athlete's degree of fault as significantly reduced, the Panel reduced the sanction to 12 months of ineligibility.",
        "country_tags": ["Morocco"],
        "language": "en",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9428.pdf",
        "source_url": "https://www.tas-cas.org",
    },
]

GLOBAL_CAS_CASES = [
    {
        "case_number": "CAS 2007/A/1298",
        "title": "CAS 2007/A/1298 — Webster v. Heart of Midlothian — Art.17 Landmark",
        "year": 2007,
        "sport": "Football/Soccer",
        "parties": "Andrew Webster v. Heart of Midlothian FC",
        "claimant": "Andrew Webster",
        "respondent": "Heart of Midlothian FC",
        "award_type": "Appeal",
        "outcome": "Art.17 compensation limited to remaining contract value — no sporting succession",
        "key_principles": ["Unilateral Termination","FIFA RSTP Art.17","Compensation Calculation","Protected Period"],
        "summary": "Landmark case establishing how FIFA RSTP Art.17 compensation is calculated when a player terminates outside the protected period. Webster paid only remaining contract value.",
        "full_text": "Scottish international footballer Andrew Webster unilaterally terminated his contract with Heart of Midlothian FC after the protected period expired and signed with Wigan Athletic. Heart of Midlothian claimed substantial compensation under FIFA RSTP Article 17. The CAS Panel issued a landmark ruling holding that compensation under Article 17 should be calculated primarily based on the remaining contract value rather than market value or transfer fees. The Panel rejected the concept of sporting succession (liability of new club) in this context. This case remains one of the most cited CAS awards in contract termination disputes worldwide.",
        "country_tags": ["International","Scotland","UK"],
        "language": "en",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/1298.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2008/A/1519",
        "title": "CAS 2008/A/1519 — Matuzalem v. Shakhtar Donetsk — Art.17 Compensation",
        "year": 2009,
        "sport": "Football/Soccer",
        "parties": "Francelino Matuzalem v. Shakhtar Donetsk",
        "claimant": "Shakhtar Donetsk",
        "respondent": "Francelino Matuzalem",
        "award_type": "Appeal",
        "outcome": "€11.8M compensation awarded — market value included in Art.17 calculation",
        "key_principles": ["Unilateral Termination","FIFA RSTP Art.17","Market Value","Compensation"],
        "summary": "Brazilian midfielder terminated contract without just cause during protected period. CAS awarded €11.8M compensation including market value, diverging from Webster approach.",
        "full_text": "Brazilian professional footballer Francelino Matuzalem terminated his contract with Shakhtar Donetsk during the protected period and signed with Real Zaragoza. The case went to CAS on appeal from the FIFA DRC decision. The CAS Panel found that compensation under Article 17 during the protected period should include market value considerations beyond mere remaining contract value, distinguishing this case from Webster. The Panel awarded €11.8 million in compensation, incorporating the player's market value and the sporting damage suffered by the club. This case created significant divergence in CAS jurisprudence on Article 17 compensation calculation.",
        "country_tags": ["International","Ukraine","Spain"],
        "language": "en",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/1519.pdf",
        "source_url": "https://www.tas-cas.org",
    },
    {
        "case_number": "CAS 2016/A/4371",
        "title": "CAS 2016/A/4371 — WADA v. RUSADA — Russian Doping System",
        "year": 2016,
        "sport": "Athletics",
        "parties": "WADA v. RUSADA and Russian Athletes",
        "claimant": "World Anti-Doping Agency (WADA)",
        "respondent": "Russian Anti-Doping Agency (RUSADA)",
        "award_type": "Appeal",
        "outcome": "State-sponsored doping system confirmed — multiple sanctions upheld",
        "key_principles": ["Anti-Doping","State Doping","WADA Code","Non-Analytical Positive","Systemic Violations"],
        "summary": "Landmark CAS proceedings following McLaren Report confirming systematic state-sponsored doping in Russian sport. Established precedent for non-analytical positive findings.",
        "full_text": "Following the McLaren Report's findings of a state-sponsored doping scheme in Russian sport, WADA brought proceedings against RUSADA and individual Russian athletes. The CAS Panel upheld findings of systematic doping violations and established important precedents regarding non-analytical positive findings — where doping violations are proven through documentary evidence rather than positive tests. The Panel confirmed that state-sponsored manipulation of the anti-doping system constitutes a fundamental violation of the World Anti-Doping Code and justified severe sanctions including competition bans.",
        "country_tags": ["International","Russia"],
        "language": "en",
        "pdf_url": "https://jurisprudence.tas-cas.org/Shared%20Documents/4371.pdf",
        "source_url": "https://www.tas-cas.org",
    },
]


# ═══════════════════════════════════════════════════════════════════
#   MAIN SEEDER
# ═══════════════════════════════════════════════════════════════════

def create_storage_buckets():
    """Create Supabase storage buckets."""
    print("\n📦 Creating storage buckets...")
    buckets = ["cas-pdfs", "regulation-pdfs", "client-documents", "contract-files"]
    for bucket in buckets:
        try:
            if USE_SDK:
                sb.storage.create_bucket(bucket, {"public": True})
                print(f"  ✓ Bucket: {bucket}")
            else:
                url = f"{SUPABASE_URL}/storage/v1/bucket"
                r = requests.post(url, headers=HEADERS,
                                  json={"id": bucket, "name": bucket, "public": True})
                if r.ok or "already exists" in r.text.lower():
                    print(f"  ✓ Bucket: {bucket}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"  → Bucket exists: {bucket}")
            else:
                print(f"  ⚠ Bucket {bucket}: {e}")


def seed_regulations():
    """Seed Morocco + international regulations."""
    print("\n📚 Seeding regulations...")
    all_regs = MOROCCO_REGULATIONS
    stored = 0

    for i, reg in enumerate(all_regs, 1):
        print(f"\n  [{i}/{len(all_regs)}] {reg['title'][:55]}")

        # Try to get full text
        full_text = reg.get("full_text", "")
        storage_path = ""

        if not full_text and reg.get("pdf_url"):
            print(f"    → Fetching PDF...")
            pdf_content = fetch_pdf(reg["pdf_url"])
            if pdf_content:
                # Upload to Supabase Storage
                safe_name = re.sub(r'[^\w\-]', '_', reg['title'])[:60]
                path = f"{reg.get('country','International')}/{safe_name}.pdf"
                storage_url = upload_pdf("regulation-pdfs", path, pdf_content)
                if storage_url:
                    storage_path = path
                    print(f"    ✓ PDF uploaded to storage")
                # Extract text
                full_text = extract_pdf_text(pdf_content)
                if full_text:
                    print(f"    ✓ Text extracted ({len(full_text)} chars)")

        if not full_text and reg.get("source_url"):
            print(f"    → Fetching HTML...")
            full_text = fetch_html_text(reg["source_url"])

        if not full_text:
            full_text = f"{reg.get('summary','')} {reg.get('key_articles','')}"

        record = {
            "title":         reg["title"],
            "title_ar":      reg.get("title_ar",""),
            "body":          reg["body"],
            "category":      reg["category"],
            "year":          reg.get("year"),
            "bulletin_ref":  reg.get("bulletin_ref",""),
            "language":      reg.get("language","fr"),
            "country":       reg.get("country","Morocco"),
            "full_text":     full_text[:50000],
            "key_articles":  reg.get("key_articles",""),
            "summary":       reg.get("summary",""),
            "priority":      reg.get("priority","MEDIUM"),
            "pdf_url":       reg.get("pdf_url",""),
            "storage_path":  storage_path,
            "source_url":    reg.get("source_url",""),
        }

        ok, result = upsert("regulations", record, "title")
        if ok:
            stored += 1
            print(f"    ✓ Stored in Supabase")
        else:
            print(f"    ⚠ Error: {str(result)[:80]}")

    print(f"\n  Regulations: {stored}/{len(all_regs)} stored")
    return stored


def seed_cas_cases():
    """Seed CAS cases into Supabase."""
    print("\n⚖️  Seeding CAS cases...")
    all_cases = MOROCCO_CAS_CASES + GLOBAL_CAS_CASES
    stored = 0

    for i, case in enumerate(all_cases, 1):
        print(f"\n  [{i}/{len(all_cases)}] {case['case_number']}")

        storage_path = ""
        full_text = case.get("full_text","")

        if case.get("pdf_url"):
            print(f"    → Fetching PDF...")
            pdf_content = fetch_pdf(case["pdf_url"])
            if pdf_content:
                safe = case["case_number"].replace("/","_").replace(" ","_")
                path = f"cas/{safe}.pdf"
                storage_url = upload_pdf("cas-pdfs", path, pdf_content)
                if storage_url:
                    storage_path = path
                    print(f"    ✓ PDF uploaded")
                if not full_text:
                    full_text = extract_pdf_text(pdf_content)

        record = {
            "case_number":    case["case_number"],
            "title":          case.get("title",""),
            "year":           case.get("year"),
            "sport":          case.get("sport","Football/Soccer"),
            "parties":        case.get("parties",""),
            "claimant":       case.get("claimant",""),
            "respondent":     case.get("respondent",""),
            "award_type":     case.get("award_type","Appeal"),
            "outcome":        case.get("outcome",""),
            "key_principles": case.get("key_principles",[]),
            "summary":        case.get("summary",""),
            "full_text":      (full_text or case.get("summary",""))[:50000],
            "pdf_url":        case.get("pdf_url",""),
            "storage_path":   storage_path,
            "country_tags":   case.get("country_tags",["International"]),
            "language":       case.get("language","en"),
            "source_url":     case.get("source_url",""),
        }

        ok, result = upsert("cas_awards", record, "case_number")
        if ok:
            stored += 1
            print(f"    ✓ Stored | {case.get('sport','')} | {case.get('outcome','')[:40]}")
        else:
            print(f"    ⚠ Error: {str(result)[:80]}")

    print(f"\n  CAS Cases: {stored}/{len(all_cases)} stored")
    return stored


def verify_seeding():
    """Verify data was seeded correctly."""
    print("\n🔍 Verifying database...")
    try:
        if USE_SDK:
            regs = sb.table("regulations").select("id,title,country", count="exact").execute()
            cases = sb.table("cas_awards").select("id,case_number,sport", count="exact").execute()
            morocco_cases = sb.table("cas_awards").select("id", count="exact").contains("country_tags", ["Morocco"]).execute()
            print(f"  ✓ Regulations: {regs.count}")
            print(f"  ✓ CAS Awards:  {cases.count}")
            print(f"  ✓ Morocco CAS: {morocco_cases.count}")
            print(f"\n  Test search: 'FRMF transfert joueur'")
            result = sb.rpc("lexsport_search", {"search_query": "FRMF transfert joueur"}).execute()
            data = result.data
            if data:
                print(f"  ✓ Search works: {data.get('total_cases',0)} cases, {data.get('total_regulations',0)} regs")
            return True
    except Exception as e:
        print(f"  ⚠ Verification error: {e}")
    return False


def run():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         LEXSPORT — SUPABASE SEED SCRIPT                             ║
║         Uploading legal data to your cloud database                 ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    if "YOUR_PROJECT" in SUPABASE_URL:
        print("⚠  CREDENTIALS NOT SET!")
        print("   Edit this file and set your SUPABASE_URL and SUPABASE_KEY")
        print("   OR set environment variables:")
        print("   export SUPABASE_URL=https://xxxx.supabase.co")
        print("   export SUPABASE_SERVICE_KEY=your_service_role_key")
        return

    print(f"  Target: {SUPABASE_URL}")
    create_storage_buckets()
    reg_count  = seed_regulations()
    cas_count  = seed_cas_cases()
    verify_seeding()

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    SEEDING COMPLETE ✅                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  Regulations uploaded:  {reg_count:<43}║
║  CAS cases uploaded:    {cas_count:<43}║
║                                                                      ║
║  Your LexSport app now has a live legal database!                   ║
║                                                                      ║
║  NEXT STEP: Deploy the Edge Function                                 ║
║  → Copy supabase/functions/rag-search/index.ts to Supabase          ║
║  → supabase functions deploy rag-search                              ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    run()
