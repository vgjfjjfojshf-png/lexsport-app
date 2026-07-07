-- ╔══════════════════════════════════════════════════════════════════╗
-- ║     LEXSPORT — SUPABASE DATABASE SCHEMA                         ║
-- ║     Paste this entire file into Supabase SQL Editor             ║
-- ║     Dashboard → SQL Editor → New Query → Paste → Run           ║
-- ╚══════════════════════════════════════════════════════════════════╝

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

CREATE TABLE IF NOT EXISTS cas_awards (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number     TEXT UNIQUE NOT NULL,
    title           TEXT,
    year            INTEGER,
    sport           TEXT,
    parties         TEXT,
    claimant        TEXT,
    respondent      TEXT,
    award_type      TEXT,
    outcome         TEXT,
    summary         TEXT,
    full_text       TEXT,
    key_principles  TEXT[],
    pdf_url         TEXT,
    storage_path    TEXT,
    country_tags    TEXT[],
    language        TEXT DEFAULT 'en',
    source_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS regulations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           TEXT NOT NULL,
    title_ar        TEXT,
    title_fr        TEXT,
    body            TEXT NOT NULL,
    category        TEXT NOT NULL,
    year            INTEGER,
    version         TEXT,
    bulletin_ref    TEXT,
    language        TEXT DEFAULT 'fr',
    country         TEXT DEFAULT 'Morocco',
    full_text       TEXT,
    key_articles    TEXT,
    summary         TEXT,
    priority        TEXT DEFAULT 'MEDIUM',
    pdf_url         TEXT,
    storage_path    TEXT,
    source_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS regulation_articles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    regulation_id   UUID REFERENCES regulations(id) ON DELETE CASCADE,
    article_number  TEXT,
    article_title   TEXT,
    article_text    TEXT,
    language        TEXT DEFAULT 'fr',
    tags            TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS legal_principles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT UNIQUE NOT NULL,
    name_fr         TEXT,
    name_ar         TEXT,
    description     TEXT,
    related_articles TEXT[],
    case_count      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS firms (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    plan            TEXT DEFAULT 'trial',
    seats           INTEGER DEFAULT 1,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    trial_ends_at   TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '14 days'),
    country         TEXT,
    language        TEXT DEFAULT 'en',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    firm_id         UUID REFERENCES firms(id),
    name            TEXT,
    role            TEXT DEFAULT 'lawyer',
    language        TEXT DEFAULT 'en',
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clients (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    name_ar         TEXT,
    sport           TEXT,
    email           TEXT,
    phone           TEXT,
    nationality     TEXT,
    date_of_birth   DATE,
    agent_name      TEXT,
    status          TEXT DEFAULT 'active',
    notes           TEXT,
    avatar_color    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cases (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    client_id       UUID REFERENCES clients(id),
    title           TEXT NOT NULL,
    type            TEXT,
    status          TEXT DEFAULT 'active',
    value           DECIMAL(12,2),
    currency        TEXT DEFAULT 'EUR',
    deadline        DATE,
    court           TEXT,
    notes           TEXT,
    assigned_to     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contracts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    client_id       UUID REFERENCES clients(id),
    case_id         UUID REFERENCES cases(id),
    title           TEXT,
    raw_text        TEXT,
    risk_score      INTEGER,
    risk_level      TEXT,
    sport           TEXT,
    category        TEXT,
    contract_type   TEXT,
    analysis        JSONB,
    language        TEXT DEFAULT 'en',
    storage_path    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    client_id       UUID REFERENCES clients(id),
    case_id         UUID REFERENCES cases(id),
    title           TEXT NOT NULL,
    type            TEXT,
    content         TEXT,
    sport           TEXT,
    language        TEXT DEFAULT 'en',
    storage_path    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deadlines (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    case_id         UUID REFERENCES cases(id),
    client_id       UUID REFERENCES clients(id),
    title           TEXT NOT NULL,
    due_date        DATE NOT NULL,
    type            TEXT,
    status          TEXT DEFAULT 'pending',
    urgency         TEXT DEFAULT 'medium',
    reminder_sent   BOOLEAN DEFAULT FALSE,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS research_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id),
    query           TEXT NOT NULL,
    answer          TEXT,
    sources         JSONB,
    domain          TEXT,
    language        TEXT DEFAULT 'en',
    db_used         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS leads (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    sport           TEXT,
    issue           TEXT,
    urgency         TEXT DEFAULT 'medium',
    estimated_value DECIMAL(12,2),
    currency        TEXT DEFAULT 'USD',
    source          TEXT,
    status          TEXT DEFAULT 'new',
    outreach_sent   TEXT,
    notes           TEXT,
    deadline_days   INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usage_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id         UUID REFERENCES firms(id),
    user_id         UUID REFERENCES users(id),
    action          TEXT NOT NULL,
    tokens_used     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- SEARCH VECTORS
ALTER TABLE cas_awards ADD COLUMN IF NOT EXISTS search_vector TSVECTOR
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', COALESCE(case_number,'')), 'A') ||
        setweight(to_tsvector('english', COALESCE(title,'')), 'A') ||
        setweight(to_tsvector('english', COALESCE(parties,'')), 'B') ||
        setweight(to_tsvector('english', COALESCE(outcome,'')), 'B') ||
        setweight(to_tsvector('english', COALESCE(summary,'')), 'C') ||
        setweight(to_tsvector('english', COALESCE(LEFT(full_text,10000),'')), 'D')
    ) STORED;

ALTER TABLE regulations ADD COLUMN IF NOT EXISTS search_vector TSVECTOR
    GENERATED ALWAYS AS (
        setweight(to_tsvector('french', COALESCE(title,'')), 'A') ||
        setweight(to_tsvector('french', COALESCE(body,'')), 'A') ||
        setweight(to_tsvector('french', COALESCE(key_articles,'')), 'B') ||
        setweight(to_tsvector('french', COALESCE(summary,'')), 'C') ||
        setweight(to_tsvector('french', COALESCE(LEFT(full_text,10000),'')), 'D')
    ) STORED;

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_cas_search    ON cas_awards USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_reg_search    ON regulations USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_cas_year      ON cas_awards(year DESC);
CREATE INDEX IF NOT EXISTS idx_cas_sport     ON cas_awards(sport);
CREATE INDEX IF NOT EXISTS idx_cas_country   ON cas_awards USING GIN(country_tags);
CREATE INDEX IF NOT EXISTS idx_reg_body      ON regulations(body);
CREATE INDEX IF NOT EXISTS idx_reg_category  ON regulations(category);
CREATE INDEX IF NOT EXISTS idx_cases_firm    ON cases(firm_id);
CREATE INDEX IF NOT EXISTS idx_clients_firm  ON clients(firm_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due ON deadlines(due_date ASC);
CREATE INDEX IF NOT EXISTS idx_cas_trgm      ON cas_awards USING GIN(case_number gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_reg_trgm      ON regulations USING GIN(title gin_trgm_ops);

-- RLS
ALTER TABLE firms             ENABLE ROW LEVEL SECURITY;
ALTER TABLE users             ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients           ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases             ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts         ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents         ENABLE ROW LEVEL SECURITY;
ALTER TABLE deadlines         ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_history  ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads             ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs        ENABLE ROW LEVEL SECURITY;
ALTER TABLE cas_awards        ENABLE ROW LEVEL SECURITY;
ALTER TABLE regulations       ENABLE ROW LEVEL SECURITY;
ALTER TABLE regulation_articles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_firm"        ON firms            FOR ALL USING (id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_members"    ON users            FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_clients"    ON clients          FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_cases"      ON cases            FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_contracts"  ON contracts        FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_documents"  ON documents        FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_deadlines"  ON deadlines        FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_research"   ON research_history FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_leads"      ON leads            FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "firm_usage"      ON usage_logs       FOR ALL USING (firm_id = (SELECT firm_id FROM users WHERE id = auth.uid()));
CREATE POLICY "public_cas"      ON cas_awards       FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "public_regs"     ON regulations      FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "public_articles" ON regulation_articles FOR SELECT USING (auth.role() = 'authenticated');

-- SEARCH FUNCTIONS
CREATE OR REPLACE FUNCTION search_cas_awards(
    search_query TEXT, filter_sport TEXT DEFAULT NULL,
    filter_year_from INTEGER DEFAULT NULL, filter_year_to INTEGER DEFAULT NULL,
    filter_country TEXT DEFAULT NULL, result_limit INTEGER DEFAULT 5
) RETURNS TABLE (
    case_number TEXT, title TEXT, year INTEGER, sport TEXT, parties TEXT,
    award_type TEXT, outcome TEXT, key_principles TEXT[], summary TEXT,
    excerpt TEXT, rank REAL
) LANGUAGE SQL STABLE AS $$
    SELECT c.case_number, c.title, c.year, c.sport, c.parties, c.award_type,
           c.outcome, c.key_principles, c.summary, LEFT(c.full_text, 800),
           ts_rank(c.search_vector, websearch_to_tsquery('english', search_query))
    FROM cas_awards c
    WHERE c.search_vector @@ websearch_to_tsquery('english', search_query)
      AND (filter_sport  IS NULL OR c.sport ILIKE '%'||filter_sport||'%')
      AND (filter_year_from IS NULL OR c.year >= filter_year_from)
      AND (filter_year_to   IS NULL OR c.year <= filter_year_to)
      AND (filter_country   IS NULL OR filter_country = ANY(c.country_tags))
    ORDER BY rank DESC LIMIT result_limit;
$$;

CREATE OR REPLACE FUNCTION search_regulations(
    search_query TEXT, filter_body TEXT DEFAULT NULL,
    filter_country TEXT DEFAULT NULL, filter_language TEXT DEFAULT NULL,
    result_limit INTEGER DEFAULT 3
) RETURNS TABLE (
    title TEXT, title_ar TEXT, body TEXT, category TEXT, year INTEGER,
    language TEXT, key_articles TEXT, summary TEXT, excerpt TEXT, rank REAL
) LANGUAGE SQL STABLE AS $$
    SELECT r.title, r.title_ar, r.body, r.category, r.year, r.language,
           r.key_articles, r.summary, LEFT(r.full_text, 600),
           ts_rank(r.search_vector, websearch_to_tsquery('french', search_query))
    FROM regulations r
    WHERE r.search_vector @@ websearch_to_tsquery('french', search_query)
      AND (filter_body     IS NULL OR r.body    ILIKE '%'||filter_body||'%')
      AND (filter_country  IS NULL OR r.country  = filter_country)
      AND (filter_language IS NULL OR r.language ILIKE '%'||filter_language||'%')
    ORDER BY rank DESC LIMIT result_limit;
$$;

CREATE OR REPLACE FUNCTION lexsport_search(
    search_query TEXT, filter_sport TEXT DEFAULT NULL, filter_country TEXT DEFAULT NULL
) RETURNS JSONB LANGUAGE PLPGSQL STABLE AS $$
DECLARE cas_r JSONB; reg_r JSONB; BEGIN
    SELECT jsonb_agg(row_to_json(r)) INTO cas_r
    FROM search_cas_awards(search_query, filter_sport, NULL, NULL, filter_country, 5) r;
    SELECT jsonb_agg(row_to_json(r)) INTO reg_r
    FROM search_regulations(search_query, NULL, filter_country, NULL, 3) r;
    RETURN jsonb_build_object(
        'query', search_query,
        'cas_cases', COALESCE(cas_r,'[]'::jsonb),
        'regulations', COALESCE(reg_r,'[]'::jsonb),
        'total_cases', jsonb_array_length(COALESCE(cas_r,'[]'::jsonb)),
        'total_regulations', jsonb_array_length(COALESCE(reg_r,'[]'::jsonb)),
        'searched_at', NOW()
    );
END; $$;

CREATE OR REPLACE FUNCTION get_firm_stats(p_firm_id UUID) RETURNS JSONB LANGUAGE PLPGSQL STABLE AS $$
DECLARE r JSONB; BEGIN
    SELECT jsonb_build_object(
        'total_clients',     (SELECT COUNT(*) FROM clients WHERE firm_id=p_firm_id),
        'active_cases',      (SELECT COUNT(*) FROM cases WHERE firm_id=p_firm_id AND status='active'),
        'pipeline_value',    (SELECT COALESCE(SUM(value),0) FROM cases WHERE firm_id=p_firm_id AND status!='closed_lost'),
        'contracts_analyzed',(SELECT COUNT(*) FROM contracts WHERE firm_id=p_firm_id),
        'docs_generated',    (SELECT COUNT(*) FROM documents WHERE firm_id=p_firm_id),
        'upcoming_deadlines',(SELECT COUNT(*) FROM deadlines WHERE firm_id=p_firm_id AND due_date>=NOW() AND status='pending'),
        'urgent_deadlines',  (SELECT COUNT(*) FROM deadlines WHERE firm_id=p_firm_id AND due_date<=NOW()+INTERVAL '7 days' AND status='pending'),
        'research_queries',  (SELECT COUNT(*) FROM research_history WHERE firm_id=p_firm_id),
        'cas_database_size', (SELECT COUNT(*) FROM cas_awards),
        'regulations_count', (SELECT COUNT(*) FROM regulations)
    ) INTO r; RETURN r;
END; $$;

CREATE OR REPLACE FUNCTION update_updated_at() RETURNS TRIGGER LANGUAGE PLPGSQL AS $$
BEGIN NEW.updated_at=NOW(); RETURN NEW; END; $$;

CREATE TRIGGER trg_cas_updated     BEFORE UPDATE ON cas_awards  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_reg_updated     BEFORE UPDATE ON regulations FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_clients_updated BEFORE UPDATE ON clients     FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_cases_updated   BEFORE UPDATE ON cases       FOR EACH ROW EXECUTE FUNCTION update_updated_at();

INSERT INTO legal_principles (name, name_fr, name_ar, description, related_articles) VALUES
('Just Cause','Juste Cause','السبب المشروع','Valid reason to terminate a contract without compensation',ARRAY['FIFA RSTP Art.14']),
('Overdue Payables','Créances Impayées','المستحقات المتأخرة','2+ months unpaid salary constitutes just cause',ARRAY['FIFA RSTP Art.14bis']),
('Unilateral Termination','Résiliation Unilatérale','الفسخ الانفرادي','Termination without just cause triggers compensation',ARRAY['FIFA RSTP Art.17']),
('Training Compensation','Compensation de Formation','تعويض التكوين','Fee paid to clubs that trained a player aged 12-23',ARRAY['FIFA RSTP Art.20']),
('Solidarity Contribution','Mécanisme de Solidarité','مساهمة التضامن','5% of transfer fee distributed to training clubs',ARRAY['FIFA RSTP Art.21']),
('Proportionality','Proportionnalité','التناسب','Sanction must be proportionate to the violation',ARRAY['WADA Code Art.10']),
('Due Process','Droit à un Procès Équitable','حق التقاضي العادل','Right to be heard before any sanction is imposed',ARRAY['CAS Procedural Rules']),
('Image Rights','Droits à l''Image','حقوق الصورة','Athlete control over commercial use of their likeness',ARRAY['FRMF Art.15']),
('TPO Ban','Interdiction TPO','حظر الملكية الثالثة','Third party ownership of player rights is prohibited',ARRAY['FIFA RSTP Art.18ter']),
('Doping Violation','Violation Anti-Dopage','انتهاك مكافحة المنشطات','Use or possession of prohibited substance or method',ARRAY['WADA Code Art.2']),
('TUE','Autorisation Usage Thérapeutique','الإعفاء العلاجي','Therapeutic Use Exemption for medical treatment',ARRAY['WADA ISTUE']),
('Agent Commission','Commission Agent','عمولة الوكيل','FIFA cap: 3% player-funded, 6% club-funded',ARRAY['FIFA Agent Regs 2023'])
ON CONFLICT (name) DO NOTHING;
