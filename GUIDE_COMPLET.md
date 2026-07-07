# 🏛️ LEXSPORT AI — GUIDE COMPLET TIER 1
## Sports Law Platform — MENA: Maroc · Égypte · Arabie Saoudite · UAE · Qatar

---

## 📁 STRUCTURE DU PROJET

```
lexsport_tier1/
│
├── 📱 APP WEB
│   └── lexsport-complete.jsx     → App React complète (8 modules)
│
├── 🗄️ BASE DE DONNÉES CLOUD
│   ├── supabase_schema.sql       → Tables + fonctions de recherche
│   └── seed_supabase.py          → Upload données vers Supabase
│
├── 🕷️ SCRAPERS (données légales)
│   ├── morocco_scraper.py        → 🇲🇦 Maroc (23 régulations + 9 CAS)
│   ├── egypt_scraper.py          → 🇪🇬 Égypte (13 régulations + 8 CAS)
│   ├── gulf_scraper.py           → 🇸🇦🇦🇪🇶🇦 Gulf (21 régulations + 8 CAS)
│   ├── cas_scraper.py            → CAS global (auto-download PDFs)
│   └── regulations_scraper.py   → FIFA + WADA + UEFA international
│
├── ▶️ COMMANDE CENTRALE
│   └── run.py                    → Lance tout depuis ici
│
├── 📂 IMPORTS MANUELS
│   ├── manual_imports/morocco/   → Mets tes PDFs FRMF ici
│   ├── manual_imports/egypt/     → Mets tes PDFs EFA ici
│   └── manual_imports/gulf/      → Mets tes PDFs SAFF/UAEFA/QFA ici
│
└── 📊 OUTPUTS
    ├── output/json/              → Index JSON générés automatiquement
    ├── output/pdfs/              → PDFs téléchargés
    └── database/lexsport.db     → Base SQLite locale (test)
```

---

## 📊 DONNÉES TIER 1 — CE QUI EST DEDANS

### 🇲🇦 MAROC (23 régulations + 9 cas CAS)
```
CRITIQUE:
  • Loi 30-09 (Sports)
  • Code Travail 65-99
  • FRMF RSTJ 2024 (Transferts)
  • FRMF Agents 2024
  • Code Anti-dopage 04-16
  • FIFA Host Agreement CdM 2030

ÉLEVÉ:
  • Statuts FRMF 2024
  • Règlement Disciplinaire FRMF
  • AMDISS Anti-dopage
  • BAM Arbitrage Sportif
  • + 13 autres sources
```

### 🇪🇬 ÉGYPTE (13 régulations + 8 cas CAS)
```
CRITIQUE:
  • Loi Sport 71/2017
  • Code Travail 12/2003
  • EFA RSTP 2024
  • EFA Agents 2024

ÉLEVÉ:
  • EFA Disciplinaire 2024
  • EFA Anti-dopage
  • CAF RSTP 2024
  • Loi Anti-dopage 55/2017
  • + 5 autres sources

CAS NOTABLES:
  • Zamalek v. FIFA (transfer ban)
  • Al-Ahly agent commission
  • Match-fixing lifetime ban
```

### 🇸🇦 ARABIE SAOUDITE (8 régulations + 3 cas CAS)
```
CRITIQUE:
  • SAFF RSTP 2024
  • Saudi Pro League Regulations
  • SAFF Agents 2023 (post-FIFA)
  • SCAS Arbitrage (nouveau)

ÉLEVÉ:
  • SAFF Disciplinaire
  • Saudi Labour Law
  • SAADC Anti-dopage
  • + 1 autre source
```

### 🇦🇪 UAE (6 régulations + 2 cas CAS)
```
CRITIQUE:
  • UAEFA RSTP 2024
  • DIFC Courts (Common Law)

ÉLEVÉ:
  • UAE Pro League Regulations
  • UAE Labour Law 33/2021
  • UAE NADO
  • UAEFA Statuts
```

### 🇶🇦 QATAR (5 régulations + 3 cas CAS)
```
CRITIQUE:
  • QFA RSTP 2024
  • Qatar Labour Law (Kafala)

ÉLEVÉ:
  • Qatar Stars League
  • Qatar Anti-Doping
  • QFA Statuts
```

### 🌍 INTERNATIONAL (inclus dans les scrapers)
```
• FIFA RSTP 2024              CRITIQUE
• World Anti-Doping Code 2021 CRITIQUE
• FIFA Agent Regulations 2023 CRITIQUE
• UEFA Club Licensing 2024    MOYEN
• AFC Club Licensing 2024     MOYEN
• CAF RSTP 2024               ÉLEVÉ
```

**TOTAL TIER 1: ~80 sources légales + ~30 cas CAS**

---

## 🚀 DÉPLOIEMENT — ÉTAPES POUR DEMAIN (PC)

### PRÉ-REQUIS
```bash
# Python 3.10+ installé
python --version

# Installer les dépendances
pip install supabase requests pypdf beautifulsoup4 lxml
```

---

### ÉTAPE 1 — Supabase (15 min)

**1.1 — Créer le projet**
```
supabase.com → New Project
  Name:     lexsport-mena
  Region:   West EU (Paris)
  Plan:     Free
```

**1.2 — Récupérer les clés**
```
Settings → API
  Project URL:      https://xxx.supabase.co    ← COPIE
  anon key:         eyJhbG...                   ← COPIE
  service_role key: eyJhbG...                   ← COPIE (SECRET)
```

**1.3 — Créer les tables**
```
SQL Editor → New Query
→ Colle TOUT le contenu de supabase_schema.sql
→ Clique RUN
→ Tu dois voir: "LEXSPORT TABLES CREATED"
```

---

### ÉTAPE 2 — Upload des données (10 min)

**2.1 — Configurer les clés dans seed_supabase.py**

Ouvre `seed_supabase.py` et remplace:
```python
SUPABASE_URL = "https://TON_PROJET.supabase.co"
SUPABASE_KEY = "ta_service_role_key"
```

**2.2 — Lancer le seed**
```bash
python seed_supabase.py
```

Résultat attendu:
```
✓ Regulations uploaded: 11
✓ CAS cases uploaded:   9
SEEDING COMPLETE ✅
```

---

### ÉTAPE 3 — Scrapers pays (20 min)

```bash
# Maroc (déjà dans seed, mais pour ajouter plus)
python run.py morocco

# Égypte
python run.py egypt

# Gulf (Saudi + UAE + Qatar)
python run.py gulf

# Ou tout en une commande:
python run.py all
```

---

### ÉTAPE 4 — Déployer l'app sur Vercel (10 min)

**4.1 — Créer compte Vercel**
```
vercel.com → Sign up with GitHub
```

**4.2 — Mettre l'app sur GitHub**
```bash
# Crée un repo GitHub "lexsport-app"
# Upload lexsport-complete.jsx dedans
```

**4.3 — Déployer**
```
Vercel → New Project
→ Import ton repo GitHub "lexsport-app"
→ Framework: React (Vite)
→ Add Environment Variables:
    VITE_SUPABASE_URL    = https://xxx.supabase.co
    VITE_SUPABASE_ANON   = eyJhbG...
    VITE_ANTHROPIC_KEY   = sk-ant-...
→ Deploy
```

**4.4 — Résultat**
```
✅ https://lexsport-app.vercel.app
   Ton app est LIVE sur internet !
```

---

### ÉTAPE 5 — Tester que tout marche (5 min)

```bash
# Test recherche locale
python run.py search "FIFA RSTP Article 17 termination"
python run.py search "FRMF transfert joueur Maroc"
python run.py search "Saudi Pro League foreign player quota"
python run.py search "EFA disciplinary Al-Ahly Egypt"

# Test Supabase (depuis SQL Editor)
SELECT * FROM search_legal_database('FRMF transfert joueur', 'Morocco', 5);
SELECT * FROM regulations WHERE country = 'Egypt' ORDER BY priority;
SELECT * FROM cas_awards WHERE 'Morocco' = ANY(country_tags);
```

---

## 💡 COMMANDES RAPIDES

```bash
# Lancer un scraper spécifique
python run.py morocco              # 🇲🇦 Maroc
python run.py egypt                # 🇪🇬 Égypte
python run.py gulf                 # 🇸🇦🇦🇪🇶🇦 Gulf complet
python run.py gulf --country saudi # Arabie Saoudite seulement
python run.py gulf --country uae   # UAE seulement
python run.py gulf --country qatar # Qatar seulement

# Importer des PDFs manuels
python run.py morocco --manual /chemin/vers/pdfs
python run.py egypt --manual /chemin/vers/pdfs
python run.py gulf --manual /chemin/vers/pdfs

# Recherche dans la base
python run.py search "ta question ici"

# Statistiques
python run.py stats

# Tout en une fois (SETUP COMPLET)
python run.py all

# Upload vers Supabase
python seed_supabase.py
```

---

## 📱 MODULES DE L'APP LEXSPORT

```
🏠 Dashboard         → Stats + activité + briefing IA du matin
⚖️ Contract Analyzer → Analyse risques contrats (4 langues)
🔍 Case Research     → Recherche jurisprudence CAS + droit local
📡 Lead Radar        → Opportunités clients + emails IA
📄 Document Generator→ Rédaction contrats, NDA, lettres
📅 Deadline Calendar → Calendrier deadlines automatique
💰 Revenue Pipeline  → Kanban clients + revenus
👤 Client Manager    → Profils + chat IA par client
```

---

## 💰 MODÈLE ÉCONOMIQUE RECOMMANDÉ

```
STARTER     499 MAD/mois  (~$50)   Solo avocat Maroc/Égypte
PRO         1,500 MAD/mois (~$150) Agents FIFA + Gulf
FIRM        3,500 MAD/mois (~$350) Cabinet multi-pays + équipe

PROJECTION:
  Mois 3:   10 clients  → 5,000-15,000 MAD/mois
  Mois 6:   50 clients  → 25,000-75,000 MAD/mois
  Mois 12: 200 clients  → 100,000+ MAD/mois
```

---

## 🎯 MARCHÉS PRIORITAIRES

```
1. 🇲🇦 Maroc       → Avocats sportifs + agents FIFA + CdM 2030
2. 🇪🇬 Égypte      → Al-Ahly/Zamalek agents + Premier League
3. 🇸🇦 Saudi       → Saudi Pro League agents étrangers
4. 🇦🇪 UAE         → DIFC + Dubai Sports Council
5. 🇶🇦 Qatar       → Post CdM 2022 infrastructure légale
```

---

## ⚠️ NOTES IMPORTANTES

```
1. CLÉS API — Ne jamais exposer service_role key en public
2. SUPABASE FREE — Limite 500MB storage, OK jusqu'à 500 users
3. VERCEL FREE   — Limite 100GB bandwidth, OK pour démarrer
4. CLAUDE API    — Payer à l'usage (~$0.01 par recherche)
5. PDFs MANUELS  — Télécharger depuis frmf.ma, thefa.org.eg,
                    saff.com.sa, uaefa.ae, qfa.qa directement
```

---

## 📞 PROCHAINES ÉTAPES APRÈS TIER 1

```
TIER 2 (après lancement):
  🎮 Esports MENA  → Saudi/UAE Esports Federation
  🥊 Combat Sports → Saudi Riyadh Season (boxing/MMA)
  🏇 Horse Racing  → Dubai/Saudi Cup (FEI rules)
  🇩🇿 Algérie      → FAF + droit sportif algérien
  🇹🇳 Tunisie      → FTF + droit sportif tunisien
```

---

*LexSport AI v1.0 — Tier 1 MENA*
*Built with Claude AI + Supabase + Vercel*
*© 2025 LexSport — All rights reserved*
