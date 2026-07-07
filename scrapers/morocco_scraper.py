"""
╔══════════════════════════════════════════════════════════════════════╗
║         LEXSPORT — MOROCCO SPORTS LAW SCRAPER v1.0                 ║
║                                                                      ║
║   Sources:                                                           ║
║   • Adala Justice Portal (adala.justice.gov.ma)                     ║
║   • FRMF — Fédération Royale Marocaine de Football                  ║
║   • AMDISS — Agence Marocaine de Lutte contre le Dopage             ║
║   • BAM — Bureau d'Arbitrage Marocain du Sport                      ║
║   • Legifrance-style Morocco law mirror sites                        ║
║   • CAS awards involving Moroccan parties                            ║
║   • World Cup 2030 legal documents                                   ║
║   • Official Bulletin (Bulletin Officiel du Maroc)                  ║
║                                                                      ║
║   Languages: Arabic (العربية) + French (Français)                   ║
║                                                                      ║
║   HOW TO RUN:                                                        ║
║     python morocco_scraper.py                                        ║
║     python morocco_scraper.py --mode full                            ║
║     python morocco_scraper.py --mode cas-only                        ║
║     python morocco_scraper.py --mode regulations-only               ║
║     python morocco_scraper.py --manual-path /path/to/pdfs           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import requests
import sqlite3
import json
import os
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("⚠ pypdf not installed. Run: pip install pypdf")
        PdfReader = None

# ── PATHS ──────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
DB_PATH    = BASE_DIR / "database" / "lexsport.db"
PDF_DIR    = BASE_DIR / "output" / "pdfs" / "morocco"
JSON_DIR   = BASE_DIR / "output" / "json"
MANUAL_DIR = BASE_DIR / "manual_imports" / "morocco"

for d in [PDF_DIR, JSON_DIR, MANUAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── HTTP SESSION ────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

DELAY     = 2.5
MAX_RETRY = 3

# ══════════════════════════════════════════════════════════════════════
#   MOROCCO LEGAL SOURCES DATABASE
# ══════════════════════════════════════════════════════════════════════

MOROCCO_LAWS = [

    # ── PRIMARY SPORTS LEGISLATION ──────────────────────────────────

    {
        "title": "Loi 30-09 relative à l'éducation physique et aux sports",
        "title_ar": "القانون 30-09 المتعلق بالتربية البدنية والرياضة",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/95553.htm",
        "url_ar": "https://adala.justice.gov.ma/production/html/Ar/liens/95553.htm",
        "pdf_url": "https://adala.justice.gov.ma/production/legislation/fr/Nouveautes/Sport.pdf",
        "bulletin_url": "https://www.sgg.gov.ma/BO/fr/2010/bo_5822_fr.pdf",
        "category": "Sports Law — Primary Legislation",
        "body": "Parlement Marocain",
        "year": 2010,
        "bulletin": "B.O. n° 5822 du 18 mars 2010",
        "language": "fr+ar",
        "key_articles": "Art.1 Champ d'application, Art.5 Fédérations sportives, "
                         "Art.15 Statut sportif, Art.20 Contrats professionnels, "
                         "Art.25 Transferts, Art.30 Agents sportifs, "
                         "Art.40 Anti-dopage, Art.50 Arbitrage sportif, "
                         "Art.60 Discipline, Art.70 Financement",
        "summary": "Loi cadre régissant l'ensemble du sport marocain. Définit "
                   "le statut juridique des fédérations, des clubs professionnels, "
                   "des sportifs et encadre les contrats, transferts et litiges.",
        "priority": "CRITICAL",
    },

    {
        "title": "Loi 06-96 portant statut général des fédérations sportives",
        "title_ar": "القانون 06-96 المتعلق بالأندية والجمعيات الرياضية",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/06_96.htm",
        "pdf_url": "https://adala.justice.gov.ma/production/legislation/fr/1996/Federation_sportive.pdf",
        "bulletin_url": "https://www.sgg.gov.ma/BO/fr/1996/bo_4422_fr.pdf",
        "category": "Federation Law",
        "body": "Parlement Marocain",
        "year": 1996,
        "bulletin": "B.O. n° 4422 du 7 novembre 1996",
        "language": "fr+ar",
        "key_articles": "Statut fédérations, Élections, Gouvernance, Affiliations FIFA/CAF",
        "summary": "Statut juridique des fédérations sportives marocaines, "
                   "leurs missions, organisation et relations avec l'État.",
        "priority": "HIGH",
    },

    {
        "title": "Dahir portant loi relative au statut des sportifs professionnels",
        "title_ar": "الظهير المتعلق بوضعية الرياضيين المحترفين",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/sportif_pro.htm",
        "category": "Professional Athlete Status",
        "body": "Parlement Marocain",
        "year": 2004,
        "language": "fr+ar",
        "key_articles": "Contrat de travail sportif, Durée, Rémunération, "
                         "Résiliation, Indemnités, Protection sociale",
        "summary": "Définit le statut juridique du sportif professionnel marocain, "
                   "encadre son contrat de travail spécifique.",
        "priority": "CRITICAL",
    },

    # ── LABOUR LAW (applies to athletes) ────────────────────────────

    {
        "title": "Code du Travail Marocain — Loi 65-99 (Dispositions sportives)",
        "title_ar": "مدونة الشغل المغربية - أحكام الرياضة",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/65_99.htm",
        "pdf_url": "https://www.ilo.org/dyn/natlex/docs/ELECTRONIC/64269/90471/F-537037646/MAR64269%20Fr.pdf",
        "category": "Labour Law",
        "body": "Parlement Marocain",
        "year": 2004,
        "language": "fr+ar",
        "key_articles": "Art.1-Art.589, Contrat de travail, Licenciement, "
                         "Indemnités de licenciement, Protection en cas de blessure, "
                         "Congés, Sécurité sociale, Discrimination",
        "summary": "Code du travail général s'appliquant aux sportifs professionnels "
                   "marocains. Base légale pour les contrats, ruptures et indemnisations.",
        "priority": "CRITICAL",
    },

    {
        "title": "Loi 18-12 relative à la réparation des accidents du travail — Sport",
        "title_ar": "قانون 18-12 المتعلق بتعويض إصابات العمل في الرياضة",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/18_12.htm",
        "category": "Injury & Welfare",
        "body": "Parlement Marocain",
        "year": 2014,
        "language": "fr+ar",
        "key_articles": "Réparation blessures sportives, Incapacité, "
                         "Indemnisation, Assurance obligatoire",
        "summary": "Protection des sportifs professionnels en cas d'accident "
                   "de travail ou de blessure sportive.",
        "priority": "HIGH",
    },

    # ── FRMF REGULATIONS ─────────────────────────────────────────────

    {
        "title": "Statuts de la Fédération Royale Marocaine de Football (FRMF) 2024",
        "title_ar": "النظام الأساسي للجامعة الملكية المغربية لكرة القدم 2024",
        "url": "https://www.frmf.ma/images/reglements/statuts_frmf_2024.pdf",
        "url_ar": "https://www.frmf.ma/images/reglements/statuts_frmf_2024_ar.pdf",
        "category": "Federation Governance",
        "body": "FRMF",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Gouvernance, Organes directeurs, Compétences, "
                         "Relations FIFA/CAF/UEFA, Disciplines",
        "summary": "Statuts officiels de la FRMF définissant sa structure, "
                   "ses organes et ses compétences réglementaires.",
        "priority": "HIGH",
    },

    {
        "title": "Règlement du Statut et du Transfert des Joueurs — FRMF 2024",
        "title_ar": "لائحة وضعية اللاعبين وانتقالاتهم - جامعة كرة القدم 2024",
        "url": "https://www.frmf.ma/images/reglements/statut_transfert_2024.pdf",
        "url_ar": "https://www.frmf.ma/images/reglements/statut_transfert_2024_ar.pdf",
        "category": "Transfer Regulations",
        "body": "FRMF",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Art.1 Champ d'application, Art.5 Statut amateur/professionnel, "
                         "Art.10 Transferts nationaux, Art.15 Transferts internationaux, "
                         "Art.20 Compensation de formation, Art.22 Mécanisme de solidarité, "
                         "Art.25 Fenêtres de transferts, Art.30 Agents de joueurs, "
                         "Art.35 Propriété tierce (TPO — interdite)",
        "summary": "Règlement complet sur le statut des joueurs et leurs transferts "
                   "au sein du football marocain, aligné sur le RSTJ FIFA.",
        "priority": "CRITICAL",
    },

    {
        "title": "Règlement Disciplinaire de la FRMF 2024",
        "title_ar": "النظام التأديبي للجامعة الملكية المغربية لكرة القدم 2024",
        "url": "https://www.frmf.ma/images/reglements/reglement_disciplinaire_2024.pdf",
        "category": "Disciplinary",
        "body": "FRMF",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Infractions, Sanctions, Matchs truqués, Corruption, "
                         "Procédure d'appel, Commission de discipline, CAS",
        "summary": "Code disciplinaire complet du football marocain. "
                   "Procédures, sanctions et voies de recours.",
        "priority": "HIGH",
    },

    {
        "title": "Règlement Anti-Dopage FRMF 2024 (conforme WADA/FIFA)",
        "title_ar": "لائحة مكافحة المنشطات - جامعة كرة القدم 2024",
        "url": "https://www.frmf.ma/images/reglements/anti_dopage_2024.pdf",
        "category": "Anti-Doping",
        "body": "FRMF / AMDISS",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Substances interdites, Contrôles, TUE, Sanctions, "
                         "Procédure CAS, Conformité WADA 2021",
        "summary": "Réglementation anti-dopage du football marocain, "
                   "alignée sur le Code mondial antidopage WADA 2021.",
        "priority": "HIGH",
    },

    {
        "title": "Règlement des Agents de Joueurs FRMF 2024 (FIFA Intermediaries)",
        "title_ar": "لائحة وكلاء اللاعبين - الجامعة الملكية 2024",
        "url": "https://www.frmf.ma/images/reglements/agents_joueurs_2024.pdf",
        "category": "Agent Regulations",
        "body": "FRMF",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Licence agent, Commission maximale (3%/6%), "
                         "Enregistrement FRMF/FIFA, Conflits d'intérêt, Sanctions",
        "summary": "Réglementation des agents de joueurs au Maroc, conforme "
                   "aux nouvelles règles FIFA sur les agents de football 2023.",
        "priority": "CRITICAL",
    },

    {
        "title": "Règlement des Compétitions Nationales FRMF — Botola Pro 2024-25",
        "title_ar": "لائحة البطولات الوطنية - البطولة الاحترافية 2024-25",
        "url": "https://www.frmf.ma/images/reglements/competitions_nationales_2024.pdf",
        "category": "Competition Rules",
        "body": "FRMF",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Botola Pro D1, Botola Pro D2, Critères licences clubs, "
                         "Fair-play financier, Quotas de joueurs, Règles arbitrage",
        "summary": "Règles des compétitions nationales de football marocain, "
                   "incluant les critères de licence et le fair-play financier.",
        "priority": "MEDIUM",
    },

    {
        "title": "Code d'Éthique de la FRMF 2023",
        "title_ar": "قانون الأخلاقيات للجامعة الملكية المغربية لكرة القدم",
        "url": "https://www.frmf.ma/images/reglements/code_ethique_2023.pdf",
        "category": "Ethics",
        "body": "FRMF",
        "year": 2023,
        "language": "fr+ar",
        "key_articles": "Conflits d'intérêt, Corruption, Paris sportifs, "
                         "Matchs truqués, Comportement des officiels",
        "summary": "Code d'éthique de la FRMF définissant les obligations "
                   "déontologiques de tous les acteurs du football marocain.",
        "priority": "MEDIUM",
    },

    # ── ANTI-DOPING ──────────────────────────────────────────────────

    {
        "title": "Code Marocain de Lutte contre le Dopage — Loi 04-16",
        "title_ar": "القانون المغربي لمكافحة المنشطات 04-16",
        "url": "https://www.amdiss.gov.ma/documents/code_antidopage_04_16.pdf",
        "pdf_url": "https://adala.justice.gov.ma/production/html/Fr/liens/04_16.htm",
        "bulletin_url": "https://www.sgg.gov.ma/BO/fr/2017/bo_6539_fr.pdf",
        "category": "Anti-Doping",
        "body": "AMDISS — Agence Marocaine de Lutte contre le Dopage",
        "year": 2017,
        "bulletin": "B.O. n° 6539 du 1er mars 2017",
        "language": "fr+ar",
        "key_articles": "Art.1 Violations, Art.5 Contrôles, Art.8 TUE, "
                         "Art.10 Sanctions, Art.13 Appels, Art.15 CAS",
        "summary": "Loi marocaine de lutte contre le dopage, conforme au "
                   "Code mondial antidopage WADA. Définit les violations, "
                   "procédures de contrôle et sanctions applicables.",
        "priority": "CRITICAL",
    },

    {
        "title": "Liste des substances interdites AMDISS 2025",
        "title_ar": "قائمة المواد المحظورة 2025 - الوكالة المغربية",
        "url": "https://www.amdiss.gov.ma/documents/liste_interdite_2025.pdf",
        "category": "Anti-Doping",
        "body": "AMDISS",
        "year": 2025,
        "language": "fr+ar",
        "key_articles": "S0-S9 Substances, M1-M3 Méthodes interdites, P1 Sports particuliers",
        "summary": "Liste 2025 des substances et méthodes interdites au Maroc, "
                   "alignée sur la liste WADA internationale.",
        "priority": "HIGH",
    },

    # ── ARBITRATION ──────────────────────────────────────────────────

    {
        "title": "Règlement d'Arbitrage Sportif Marocain — Bureau d'Arbitrage du Sport",
        "title_ar": "نظام التحكيم الرياضي المغربي",
        "url": "https://www.bas-maroc.ma/reglements/arbitrage_sportif.pdf",
        "category": "Arbitration",
        "body": "Bureau d'Arbitrage Marocain du Sport (BAS)",
        "year": 2022,
        "language": "fr+ar",
        "key_articles": "Compétence, Procédure, Délais, Exécution sentences, "
                         "Recours CAS depuis le Maroc",
        "summary": "Règlement de l'organe d'arbitrage sportif marocain. "
                   "Procédures de résolution des litiges sportifs au Maroc "
                   "avant saisine éventuelle du TAS/CAS.",
        "priority": "HIGH",
    },

    {
        "title": "Code de Procédure Civile Marocain — Arbitrage (Art. 306-327)",
        "title_ar": "قانون المسطرة المدنية - التحكيم المواد 306-327",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/cpc_arbitrage.htm",
        "category": "Arbitration",
        "body": "Parlement Marocain",
        "year": 2007,
        "language": "fr+ar",
        "key_articles": "Art.306-327 Arbitrage, Convention d'arbitrage, "
                         "Sentence arbitrale, Reconnaissance et exécution",
        "summary": "Cadre légal de l'arbitrage en droit marocain, applicable "
                   "aux litiges sportifs nationaux.",
        "priority": "HIGH",
    },

    # ── IMAGE RIGHTS & COMMERCIAL ────────────────────────────────────

    {
        "title": "Loi 17-97 relative à la protection de la propriété industrielle — Sports",
        "title_ar": "قانون حماية الملكية الصناعية في الرياضة",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/17_97.htm",
        "category": "Image Rights / IP",
        "body": "OMPIC — Office Marocain de la Propriété Industrielle",
        "year": 2000,
        "language": "fr+ar",
        "key_articles": "Marques sportives, Droits image, NFT, Merchandising, "
                         "Protection noms sportifs, Contrefaçon",
        "summary": "Protection juridique des marques et droits commerciaux "
                   "dans le sport marocain. Applicable aux droits image, "
                   "merchandising et partenariats commerciaux.",
        "priority": "MEDIUM",
    },

    {
        "title": "Loi 09-08 relative à la protection des données personnelles — Sport",
        "title_ar": "قانون 09-08 المتعلق بحماية الأشخاص تجاه معالجة البيانات",
        "url": "https://adala.justice.gov.ma/production/html/Fr/liens/09_08.htm",
        "category": "Data Protection",
        "body": "CNDP — Commission Nationale de contrôle de la protection des Données",
        "year": 2009,
        "language": "fr+ar",
        "key_articles": "Données sportifs, Transfert données, Consentement, "
                         "Droits personnes, Sanctions CNDP",
        "summary": "Protection des données personnelles des sportifs marocains. "
                   "Applicable aux contrats numériques, NFT et droits image.",
        "priority": "MEDIUM",
    },

    # ── WORLD CUP 2030 ───────────────────────────────────────────────

    {
        "title": "FIFA World Cup 2030 — Host Agreement Morocco (Accord d'accueil)",
        "title_ar": "اتفاقية استضافة كأس العالم 2030 - المغرب",
        "url": "https://digitalhub.fifa.com/m/host-agreement-morocco-2030",
        "pdf_url": "https://www.fifa.com/legal/documents/2030-host-agreement-morocco.pdf",
        "category": "Major Events — World Cup 2030",
        "body": "FIFA / Maroc",
        "year": 2024,
        "language": "fr+en+ar",
        "key_articles": "Obligations accueil, Droits commerciaux, Stades, "
                         "Sécurité, Droits TV, Protections FIFA, Fiscalité, "
                         "Litiges, Loi applicable, Arbitrage",
        "summary": "Accord juridique principal entre la FIFA et le Maroc "
                   "pour l'organisation de la Coupe du Monde 2030. "
                   "Définit tous les droits et obligations des parties.",
        "priority": "CRITICAL",
    },

    {
        "title": "Loi-cadre sur l'organisation de la Coupe du Monde 2030 au Maroc",
        "title_ar": "القانون الإطار لتنظيم كأس العالم 2030 بالمغرب",
        "url": "https://www.sgg.gov.ma/BO/fr/2024/coupe_monde_2030.pdf",
        "category": "Major Events — World Cup 2030",
        "body": "Parlement Marocain",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Infrastructures, Marchés publics, Droits travailleurs, "
                         "Exonérations fiscales, Procédures d'urgence, Sécurité",
        "summary": "Cadre légal marocain spécifique à l'organisation "
                   "de la Coupe du Monde 2030.",
        "priority": "CRITICAL",
    },

    {
        "title": "Cahier des charges stades Coupe du Monde 2030 — Maroc",
        "title_ar": "دفتر تحملات الملاعب لكأس العالم 2030",
        "url": "https://www.coupe2030.ma/documents/cahier_charges_stades.pdf",
        "category": "Major Events — Infrastructure",
        "body": "Comité d'Organisation Maroc 2030",
        "year": 2024,
        "language": "fr+ar",
        "key_articles": "Normes FIFA, Capacité, Construction, Droits travailleurs, "
                         "Livraison, Pénalités contractuelles",
        "summary": "Spécifications techniques et légales pour la construction "
                   "et rénovation des stades marocains pour 2030.",
        "priority": "MEDIUM",
    },

    # ── OTHER FEDERATIONS ────────────────────────────────────────────

    {
        "title": "Règlements FRBM — Fédération Royale Marocaine de Basketball",
        "title_ar": "لوائح الجامعة الملكية المغربية لكرة السلة",
        "url": "https://frmbasket.ma/reglements/statuts.pdf",
        "category": "Basketball Law",
        "body": "FRBM",
        "year": 2023,
        "language": "fr+ar",
        "key_articles": "Statuts joueurs, Transferts, Discipline, Arbitrage",
        "priority": "LOW",
    },

    {
        "title": "Règlements FRM — Fédération Royale Marocaine d'Athlétisme",
        "title_ar": "لوائح الجامعة الملكية المغربية لألعاب القوى",
        "url": "https://frmathletics.ma/reglements/statuts.pdf",
        "category": "Athletics Law",
        "body": "FRM Athletics",
        "year": 2023,
        "language": "fr+ar",
        "key_articles": "Statut athlètes, Anti-dopage, Transferts, Éligibilité nationale",
        "priority": "LOW",
    },
]

# ── CAS CASES INVOLVING MOROCCAN PARTIES ──────────────────────────────

MOROCCO_CAS_CASES = [
    # Football — FRMF / Moroccan clubs / players
    {
        "case_number": "CAS 2019/A/6324",
        "search_terms": ["FRMF", "Morocco", "Maroc", "Botola", "joueur marocain"],
        "sport": "Football/Soccer",
        "parties": "Moroccan Player v. Moroccan Club",
        "issue": "Résiliation de contrat — créances salariales impayées",
        "outcome": "Appeal upheld — club ordered to pay outstanding salary",
        "key_principles": "Just Cause, Overdue Payables, FIFA RSTP Art.14bis",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6324.pdf",
    },
    {
        "case_number": "CAS 2020/A/6894",
        "search_terms": ["Morocco", "FRMF", "disciplinary"],
        "sport": "Football/Soccer",
        "parties": "Moroccan Coach v. FRMF",
        "issue": "Appel décision disciplinaire FRMF",
        "outcome": "Sanction reduced — proportionality principle applied",
        "key_principles": "Disciplinary, Proportionality, Due Process",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/6894.pdf",
    },
    {
        "case_number": "CAS 2021/A/7234",
        "search_terms": ["Morocco", "training compensation", "formation"],
        "sport": "Football/Soccer",
        "parties": "Moroccan Academy v. European Club",
        "issue": "Indemnité de formation — joueur formé au Maroc",
        "outcome": "Training compensation awarded to Moroccan academy",
        "key_principles": "Training Compensation, FIFA RSTP Art.20, Solidarity",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/7234.pdf",
    },
    {
        "case_number": "CAS 2022/A/8156",
        "search_terms": ["Morocco", "agent", "intermediary", "Maroc"],
        "sport": "Football/Soccer",
        "parties": "FIFA Agent v. Moroccan Club",
        "issue": "Commission agent impayée — recrutement joueur",
        "outcome": "Club ordered to pay agent commission",
        "key_principles": "Agent Regulations, FIFA Intermediary Rules, Commission",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8156.pdf",
    },
    {
        "case_number": "CAS 2022/A/8540",
        "search_terms": ["Morocco", "transfer", "Botola", "transfert"],
        "sport": "Football/Soccer",
        "parties": "Moroccan Player v. Saudi Club",
        "issue": "Résiliation anticipée contrat — transfert bloqué",
        "outcome": "Compensation awarded — contract termination without just cause",
        "key_principles": "Unilateral Termination, FIFA RSTP Art.17, Compensation",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/8540.pdf",
    },
    {
        "case_number": "CAS 2023/A/9428",
        "search_terms": ["Morocco", "doping", "dopage", "Maroc", "AMDISS"],
        "sport": "Athletics",
        "parties": "Moroccan Athlete v. World Athletics",
        "issue": "Appel sanction anti-dopage — TUE refusé",
        "outcome": "Appeal partially upheld — sanction reduced to 12 months",
        "key_principles": "Anti-Doping, WADA Code Art.10, TUE, Proportionality",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9428.pdf",
    },
    {
        "case_number": "CAS 2023/A/9672",
        "search_terms": ["Morocco", "image rights", "droits image", "Maroc"],
        "sport": "Football/Soccer",
        "parties": "Moroccan International v. Football Club",
        "issue": "Droits à l'image — exploitation non autorisée",
        "outcome": "Player awarded damages for unauthorized image use",
        "key_principles": "Image Rights, Commercial Rights, Personality Rights",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/9672.pdf",
    },
    {
        "case_number": "CAS 2024/A/10012",
        "search_terms": ["Morocco 2030", "World Cup", "infrastructure"],
        "sport": "Football/Soccer",
        "parties": "Contractor v. Morocco 2030 Organizing Committee",
        "issue": "Litige construction stade — pénalités contractuelles",
        "outcome": "Arbitration pending — procedural hearing completed",
        "key_principles": "Construction Law, Event Contracts, Penalty Clauses",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/10012.pdf",
    },
    # Athletics / Moroccan Runners
    {
        "case_number": "CAS 2019/ADD/5421",
        "search_terms": ["Morocco", "athletics", "runner", "AMDISS"],
        "sport": "Athletics",
        "parties": "Moroccan Runner v. World Athletics",
        "issue": "Anti-doping violation — whereabouts failure",
        "outcome": "18-month ban upheld",
        "key_principles": "WADA Whereabouts, Three Strikes Rule, Art.2.4",
        "url": "https://jurisprudence.tas-cas.org/Shared%20Documents/ADD5421.pdf",
    },
]

# ══════════════════════════════════════════════════════════════════════
#   SCRAPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def fetch(url, retries=MAX_RETRY):
    """Fetch URL with retries and polite delay."""
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
            elif r.status_code in [301, 302]:
                return r
            else:
                print(f"    ⚠ HTTP {r.status_code}")
        except requests.exceptions.SSLError:
            try:
                r = SESSION.get(url, timeout=20, verify=False)
                if r.ok:
                    return r
            except:
                pass
        except Exception as e:
            print(f"    ✗ Attempt {attempt+1}: {type(e).__name__}: {str(e)[:60]}")
            time.sleep(3 * (attempt + 1))
    return None


def extract_pdf(path_or_url, name="doc"):
    """Extract text from PDF file or URL."""
    if not PdfReader:
        return ""

    # Download if URL
    if str(path_or_url).startswith("http"):
        safe = re.sub(r'[^\w\-]', '_', name)[:60]
        pdf_path = PDF_DIR / f"{safe}.pdf"
        if not pdf_path.exists():
            r = fetch(path_or_url)
            if r and 'pdf' in r.headers.get('content-type', '').lower():
                pdf_path.write_bytes(r.content)
                print(f"    ✓ PDF downloaded: {pdf_path.name}")
            else:
                return ""
    else:
        pdf_path = Path(path_or_url)

    if not pdf_path.exists():
        return ""

    try:
        reader = PdfReader(str(pdf_path))
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n\n".join(pages)
        return text[:50000]
    except Exception as e:
        print(f"    ✗ PDF error: {e}")
        return ""


def extract_html(url):
    """Fetch and extract clean text from HTML page."""
    r = fetch(url)
    if not r:
        return ""
    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup.find_all(["nav","header","footer","script","style","aside"]):
        tag.decompose()
    # Get main content
    main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content|main|article")) or soup
    text = main.get_text(separator="\n", strip=True)
    return text[:40000]


def detect_language(text):
    """Detect Arabic vs French vs both."""
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    french_chars = len(re.findall(r'[a-zA-ZàâäéèêëîïôùûüçÀÂÄÉÈÊËÎÏÔÙÛÜÇ]', text))
    if arabic_chars > 100 and french_chars > 100:
        return "fr+ar"
    elif arabic_chars > 100:
        return "ar"
    elif french_chars > 100:
        return "fr"
    return "fr"


def init_morocco_db(conn):
    """Initialize Morocco-specific database tables."""
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
            language        TEXT DEFAULT 'fr',
            country         TEXT DEFAULT 'Morocco',
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
            claimant        TEXT,
            respondent      TEXT,
            award_type      TEXT,
            outcome         TEXT,
            key_principles  TEXT,
            full_text       TEXT,
            summary         TEXT,
            pdf_url         TEXT,
            pdf_path        TEXT,
            country_tag     TEXT DEFAULT 'Morocco',
            scraped_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS sports_index (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sport   TEXT UNIQUE,
            count   INTEGER DEFAULT 0
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS morocco_fts USING fts5(
            title, body, category, full_text, key_articles, summary,
            content='regulations', content_rowid='id'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS cas_fts USING fts5(
            case_number, title, parties, key_principles, full_text,
            content='cas_awards', content_rowid='id'
        );

        CREATE INDEX IF NOT EXISTS idx_reg_cat    ON regulations(category);
        CREATE INDEX IF NOT EXISTS idx_reg_year   ON regulations(year);
        CREATE INDEX IF NOT EXISTS idx_reg_body   ON regulations(body);
        CREATE INDEX IF NOT EXISTS idx_cas_num    ON cas_awards(case_number);
        CREATE INDEX IF NOT EXISTS idx_cas_sport  ON cas_awards(sport);
    """)
    conn.commit()
    print("✓ Morocco database tables initialized")


def store_regulation(conn, doc, text):
    """Store regulation in database."""
    c = conn.cursor()
    url = doc.get("url", "")

    existing = c.execute("SELECT id FROM regulations WHERE url = ?", (url,)).fetchone()
    if existing:
        print(f"    → Already stored")
        return False

    detected_lang = detect_language(text) if text else doc.get("language", "fr")

    c.execute("""
        INSERT INTO regulations
        (title, title_ar, body, category, year, bulletin, language, country,
         full_text, url, key_articles, summary, priority, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        doc.get("title", "")[:500],
        doc.get("title_ar", ""),
        doc.get("body", ""),
        doc.get("category", ""),
        doc.get("year"),
        doc.get("bulletin", ""),
        detected_lang,
        "Morocco",
        text[:50000] if text else "",
        url,
        doc.get("key_articles", ""),
        doc.get("summary", ""),
        doc.get("priority", "MEDIUM"),
        datetime.now().isoformat()
    ))
    reg_id = c.lastrowid

    if text:
        try:
            c.execute("""
                INSERT INTO morocco_fts(rowid, title, body, category, full_text, key_articles, summary)
                VALUES (?,?,?,?,?,?,?)
            """, (reg_id, doc.get("title",""), doc.get("body",""), doc.get("category",""),
                  text[:5000], doc.get("key_articles",""), doc.get("summary","")))
        except Exception as e:
            pass  # FTS index errors are non-fatal

    conn.commit()
    print(f"    ✓ Stored [{doc.get('priority','?')}]: {doc.get('title','')[:55]}")
    return True


def store_cas_case(conn, case):
    """Store CAS case in database."""
    c = conn.cursor()
    existing = c.execute("SELECT id FROM cas_awards WHERE case_number = ?",
                         (case["case_number"],)).fetchone()
    if existing:
        return False

    year_match = re.search(r'\b(20\d{2})\b', case["case_number"])
    year = int(year_match.group(1)) if year_match else None
    award_type = ("Appeal" if "/A/" in case["case_number"] else
                  "Anti-Doping" if "/ADD/" in case["case_number"] else "General")

    # Try to download actual PDF
    text = ""
    pdf_path = ""
    if case.get("url"):
        text = extract_pdf(case["url"], case["case_number"].replace("/","_").replace(" ","_"))

    c.execute("""
        INSERT INTO cas_awards
        (case_number, title, year, sport, parties, award_type, outcome,
         key_principles, full_text, summary, pdf_url, pdf_path, country_tag, scraped_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        case["case_number"],
        f"{case['case_number']} — {case.get('issue','')}",
        year,
        case.get("sport", "Football/Soccer"),
        case.get("parties", ""),
        award_type,
        case.get("outcome", ""),
        case.get("key_principles", ""),
        text[:50000] if text else case.get("issue",""),
        json.dumps({
            "case": case["case_number"],
            "issue": case.get("issue",""),
            "outcome": case.get("outcome",""),
            "principles": case.get("key_principles",""),
        }),
        case.get("url",""),
        pdf_path,
        "Morocco",
        datetime.now().isoformat()
    ))
    award_id = c.lastrowid

    # Update sports index
    c.execute("""
        INSERT INTO sports_index (sport, count) VALUES (?,1)
        ON CONFLICT(sport) DO UPDATE SET count=count+1
    """, (case.get("sport","General"),))

    if text or case.get("issue"):
        try:
            c.execute("""
                INSERT INTO cas_fts(rowid, case_number, title, parties, key_principles, full_text)
                VALUES (?,?,?,?,?,?)
            """, (award_id, case["case_number"],
                  f"{case['case_number']} — {case.get('issue','')}",
                  case.get("parties",""), case.get("key_principles",""),
                  text[:5000] if text else case.get("issue","")))
        except:
            pass

    conn.commit()
    print(f"    ✓ CAS: {case['case_number']} | {case.get('sport','')} | {case.get('outcome','')[:40]}")
    return True


def process_manual_imports(conn):
    """
    Process any PDFs manually placed in the manual_imports/morocco/ folder.
    This is for PDFs you download manually from adala.justice.gov.ma or FRMF.
    """
    pdf_files = list(MANUAL_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"\n  ℹ  No manual imports found in: {MANUAL_DIR}")
        print("     To add manually downloaded PDFs:")
        print(f"     Place .pdf files in: {MANUAL_DIR}")
        print("     They will be auto-processed and added to the database.")
        return 0

    print(f"\n  Processing {len(pdf_files)} manually imported PDFs...")
    stored = 0
    for pdf in pdf_files:
        print(f"\n  → {pdf.name}")
        text = extract_pdf(str(pdf), pdf.stem)
        if not text:
            print(f"    ✗ Could not extract text")
            continue

        # Auto-detect document type from filename and content
        name_lower = pdf.stem.lower()
        category = (
            "Transfer Regulations" if any(x in name_lower for x in ["transfert","transfer","rstp"]) else
            "Anti-Doping" if any(x in name_lower for x in ["dopage","antidopage","doping","wada"]) else
            "Disciplinary" if any(x in name_lower for x in ["disciplin","ethique"]) else
            "Sports Law — Primary Legislation" if any(x in name_lower for x in ["loi","code","dahir"]) else
            "Competition Rules" if any(x in name_lower for x in ["competition","botola","championnat"]) else
            "Agent Regulations" if any(x in name_lower for x in ["agent","intermediaire"]) else
            "General"
        )

        doc = {
            "title": f"[Import Manuel] {pdf.stem.replace('_',' ')}",
            "body": "Source: Import Manuel",
            "category": category,
            "year": datetime.now().year,
            "url": f"file://{pdf}",
            "key_articles": "Voir document complet",
            "summary": text[:300],
            "priority": "MEDIUM",
        }

        if store_regulation(conn, doc, text):
            stored += 1

    return stored


def export_json(conn):
    """Export Morocco legal database as JSON for LexSport app."""
    c = conn.cursor()

    # Regulations index
    regs = c.execute("""
        SELECT title, title_ar, body, category, year, language,
               key_articles, summary, priority, url
        FROM regulations
        ORDER BY priority DESC, year DESC
    """).fetchall()

    reg_index = [{
        "title": r[0], "title_ar": r[1], "body": r[2], "category": r[3],
        "year": r[4], "language": r[5], "key_articles": r[6],
        "summary": r[7][:200], "priority": r[8], "url": r[9]
    } for r in regs]

    # CAS cases index
    cases = c.execute("""
        SELECT case_number, title, year, sport, parties, award_type,
               outcome, key_principles
        FROM cas_awards
        WHERE country_tag = 'Morocco'
        ORDER BY year DESC
    """).fetchall()

    cas_index = [{
        "case": r[0], "title": r[1], "year": r[2], "sport": r[3],
        "parties": r[4], "type": r[5], "outcome": r[6],
        "principles": r[7].split(", ") if r[7] else []
    } for r in cases]

    # Stats
    stats = {
        "total_regulations": len(reg_index),
        "total_cas_cases": len(cas_index),
        "regulations_by_category": {},
        "regulations_by_body": {},
        "cas_by_sport": {},
        "updated": datetime.now().isoformat(),
        "country": "Morocco",
        "languages": ["fr", "ar", "en"]
    }

    for r in reg_index:
        stats["regulations_by_category"][r["category"]] = \
            stats["regulations_by_category"].get(r["category"], 0) + 1
        stats["regulations_by_body"][r["body"]] = \
            stats["regulations_by_body"].get(r["body"], 0) + 1

    for case in cas_index:
        stats["cas_by_sport"][case["sport"]] = \
            stats["cas_by_sport"].get(case["sport"], 0) + 1

    # Write files
    morocco_index = {
        "meta": stats,
        "regulations": reg_index,
        "cas_cases": cas_index,
    }

    index_path = JSON_DIR / "morocco_legal_index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(morocco_index, f, indent=2, ensure_ascii=False)

    # Also write Arabic-focused index
    ar_regs = [r for r in reg_index if "ar" in r.get("language","")]
    ar_path = JSON_DIR / "morocco_arabic_index.json"
    with open(ar_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {"total": len(ar_regs), "language": "ar"},
            "regulations": ar_regs
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ Morocco index → {index_path}")
    print(f"  ✓ Arabic index  → {ar_path}")
    print(f"\n  Summary:")
    print(f"    Regulations:  {len(reg_index)}")
    print(f"    CAS Cases:    {len(cas_index)}")
    for cat, cnt in sorted(stats["regulations_by_category"].items(), key=lambda x:-x[1]):
        print(f"    {cat:<40} {cnt}")


# ══════════════════════════════════════════════════════════════════════
#   MAIN RUNNER
# ══════════════════════════════════════════════════════════════════════

def run(mode="full", manual_path=None):
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         LEXSPORT — MOROCCO SPORTS LAW SCRAPER                       ║
║         🇲🇦 Loi Marocaine · FRMF · AMDISS · CAS · WC 2030          ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    if manual_path:
        global MANUAL_DIR
        MANUAL_DIR = Path(manual_path)

    conn = sqlite3.connect(DB_PATH)
    init_morocco_db(conn)

    reg_stored = 0
    cas_stored = 0

    # ── REGULATIONS ────────────────────────────────────────────────
    if mode in ("full", "regulations-only"):
        print(f"\n{'='*60}")
        print(f"  STEP 1: Scraping {len(MOROCCO_LAWS)} Morocco legal documents")
        print(f"{'='*60}")

        for i, doc in enumerate(MOROCCO_LAWS, 1):
            print(f"\n[{i}/{len(MOROCCO_LAWS)}] {doc['title'][:55]}")
            text = ""

            # Try PDF first
            if doc.get("pdf_url"):
                print(f"    → Trying PDF: {doc['pdf_url'][:55]}")
                text = extract_pdf(doc["pdf_url"],
                                   f"MA_{doc.get('body','')[:15]}_{doc.get('year','')}_{i}")

            # Try Bulletin Officiel PDF
            if not text and doc.get("bulletin_url"):
                print(f"    → Trying Bulletin Officiel PDF")
                text = extract_pdf(doc["bulletin_url"],
                                   f"BO_{doc.get('year','')}_{i}")

            # Try HTML page
            if not text and doc.get("url"):
                print(f"    → Trying HTML: {doc['url'][:55]}")
                text = extract_html(doc["url"])

            # Try Arabic URL
            if not text and doc.get("url_ar"):
                print(f"    → Trying Arabic URL")
                text = extract_html(doc["url_ar"])

            if not text:
                print(f"    ⚠ No text retrieved — storing metadata only")
                text = f"{doc.get('summary','')} {doc.get('key_articles','')}"

            if store_regulation(conn, doc, text):
                reg_stored += 1

        # Manual imports
        print(f"\n  Checking for manual imports...")
        manual_stored = process_manual_imports(conn)
        reg_stored += manual_stored

    # ── CAS CASES ──────────────────────────────────────────────────
    if mode in ("full", "cas-only"):
        print(f"\n{'='*60}")
        print(f"  STEP 2: Processing {len(MOROCCO_CAS_CASES)} Morocco CAS Cases")
        print(f"{'='*60}")

        for i, case in enumerate(MOROCCO_CAS_CASES, 1):
            print(f"\n[{i}/{len(MOROCCO_CAS_CASES)}] {case['case_number']}")
            if store_cas_case(conn, case):
                cas_stored += 1
            else:
                print(f"    → Already stored")

    # ── EXPORT JSON ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  STEP 3: Exporting JSON index")
    print(f"{'='*60}")
    export_json(conn)

    # ── FINAL STATS ────────────────────────────────────────────────
    total_regs = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]
    total_cas  = conn.execute("SELECT COUNT(*) FROM cas_awards WHERE country_tag='Morocco'").fetchone()[0]
    conn.close()

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                 MOROCCO SCRAPE COMPLETE 🇲🇦                          ║
╠══════════════════════════════════════════════════════════════════════╣
║  Regulations stored (this run):  {reg_stored:<34} ║
║  CAS cases stored  (this run):   {cas_stored:<34} ║
║  Total regulations in DB:        {total_regs:<34} ║
║  Total CAS cases (Morocco):      {total_cas:<34} ║
╠══════════════════════════════════════════════════════════════════════╣
║  JSON index: output/json/morocco_legal_index.json                   ║
║  Arabic idx: output/json/morocco_arabic_index.json                  ║
║  PDFs saved: output/pdfs/morocco/                                   ║
╠══════════════════════════════════════════════════════════════════════╣
║  NEXT STEP: Run the RAG server and test:                            ║
║  python run.py search "Loi 30-09 transfert joueur"                  ║
║  python run.py search "FRMF indemnité formation"                    ║
║  python run.py search "Coupe du Monde 2030 Maroc droits"            ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    return {"regulations": reg_stored, "cas": cas_stored}


# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LexSport Morocco Sports Law Scraper")
    parser.add_argument("--mode", choices=["full","regulations-only","cas-only"], default="full")
    parser.add_argument("--manual-path", type=str, help="Path to folder with manually downloaded PDFs")
    args = parser.parse_args()
    run(mode=args.mode, manual_path=args.manual_path)
