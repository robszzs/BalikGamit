"""
styles.py — Professional CSS styles for BalikGamit.
Call inject_styles() once at app startup.
"""

import streamlit as st


def inject_styles() -> None:
    st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  :root {
    --blue: #164EC6;
    --blue-dark: #0F3A96;
    --blue-mid: #1A5ED8;
    --yellow: #F5C800;
    --yellow-light: #FFFBEB;
    --blue-light: #EEF3FF;
    --surface: #FAFBFC;
    --card: #FFFFFF;
    --muted: #6B7280;
    --border: #E2E6EA;
    --border-strong: #CDD3DA;
    --text: #111827;
    --text-secondary: #4B5563;
    --red-subtle: #FEF2F2;
    --green-subtle: #F0FDF4;
    --amber-subtle: #FFFBEB;
    --radius: 10px;
    --radius-lg: 14px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    --shadow: 0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
    --shadow-lg: 0 10px 30px rgba(0,0,0,.10), 0 4px 8px rgba(0,0,0,.06);
  }

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
    -webkit-font-smoothing: antialiased;
  }

  .main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
  .stApp { background: var(--surface); }

  [data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--border);
  }
  [data-testid="stSidebar"] .block-container { padding: 1.5rem 1.25rem; }

  .stButton > button {
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .875rem !important;
    letter-spacing: -.01em !important;
    transition: all .15s ease !important;
    border: 1px solid transparent !important;
  }
  .stButton > button[kind="primary"] {
    background: var(--blue) !important;
    color: white !important;
    box-shadow: 0 1px 3px rgba(22,78,198,.3) !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: var(--blue-dark) !important;
    box-shadow: 0 4px 10px rgba(22,78,198,.35) !important;
    transform: translateY(-1px);
  }
  .stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--text) !important;
    border-color: var(--border-strong) !important;
    box-shadow: var(--shadow-sm) !important;
  }
  .stButton > button[kind="secondary"]:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
  }

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div,
  .stMultiSelect > div > div {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border-strong) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .875rem !important;
    background: white !important;
    box-shadow: var(--shadow-sm) !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(22,78,198,.08) !important;
    outline: none !important;
  }

  [data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-sm);
  }
  [data-testid="stMetricLabel"] { font-size: .72rem !important; font-weight: 600 !important; color: var(--muted) !important; text-transform: uppercase; letter-spacing: .06em; }
  [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700 !important; color: var(--text) !important; }

  [data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    background: white !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: .75rem !important;
  }
  [data-testid="stExpander"] summary { font-weight: 600 !important; font-size: .875rem !important; padding: .9rem 1.1rem !important; }

  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--surface);
    border-radius: var(--radius);
    padding: 4px;
    border: 1px solid var(--border);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    color: var(--muted) !important;
    padding: .4rem 1rem !important;
  }
  .stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--blue) !important;
    box-shadow: var(--shadow-sm) !important;
  }

  [data-testid="stInfo"]    { border-radius: var(--radius) !important; border: 1px solid #BFDBFE !important; background: #EFF6FF !important; font-size: .875rem !important; }
  [data-testid="stSuccess"] { border-radius: var(--radius) !important; font-size: .875rem !important; }
  [data-testid="stError"]   { border-radius: var(--radius) !important; font-size: .875rem !important; }
  [data-testid="stWarning"] { border-radius: var(--radius) !important; font-size: .875rem !important; }

  [data-testid="stFileUploader"] {
    border: 2px dashed var(--border-strong) !important;
    border-radius: var(--radius-lg) !important;
    background: white !important;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .07em;
    font-family: 'DM Mono', monospace;
  }
  .badge-lost     { background: var(--red-subtle);   color: #991B1B; border: 1px solid #FECACA; }
  .badge-found    { background: var(--blue-light);   color: #164EC6; border: 1px solid #BFDBFE; }
  .badge-claimed  { background: var(--green-subtle); color: #166534; border: 1px solid #BBF7D0; }
  .badge-pending  { background: var(--amber-subtle); color: #92400E; border: 1px solid #FCD34D; }
  .badge-approved { background: var(--green-subtle); color: #166534; border: 1px solid #BBF7D0; }
  .badge-rejected { background: var(--red-subtle);   color: #991B1B; border: 1px solid #FECACA; }

  .hero-banner {
    background: linear-gradient(135deg, #164EC6 0%, #0F3A96 100%);
    border-radius: 16px;
    padding: 2.75rem 2.5rem;
    color: white;
    margin-bottom: 1.75rem;
    position: relative;
    overflow: hidden;
  }
  .hero-banner::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,.04);
    pointer-events: none;
  }
  .hero-banner::before {
    content: '';
    position: absolute;
    bottom: -60px; right: 80px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(245,200,0,.06);
    pointer-events: none;
  }
  .hero-banner h1 {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0;
    letter-spacing: -.03em;
  }
  .hero-banner p { opacity: .78; margin-top: .65rem; font-size: .95rem; line-height: 1.6; }

  .item-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.1rem;
    margin-bottom: .6rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .15s ease, border-color .15s ease;
  }
  .item-card:hover { box-shadow: var(--shadow); border-color: var(--border-strong); }

  .home-item-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem;
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: .5rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .15s ease, border-color .15s ease;
  }
  .home-item-card:hover { box-shadow: var(--shadow); border-color: var(--border-strong); }
  .home-item-meta { flex: 1; min-width: 0; }
  .home-item-meta .title {
    font-weight: 600;
    font-size: .9rem;
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
  }
  .home-item-meta .note {
    font-size: .78rem;
    color: var(--text-secondary);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .home-item-meta .footer {
    font-size: .72rem;
    color: #9CA3AF;
    margin-top: 5px;
    font-family: 'DM Mono', monospace;
  }

  .grid-note {
    font-size: .78rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .step-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    height: 100%;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .15s ease;
  }
  .step-card:hover { box-shadow: var(--shadow); }
  .step-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #E5E7EB;
    font-family: 'DM Mono', monospace;
    letter-spacing: -.04em;
  }

  .tip-card {
    background: linear-gradient(135deg, #164EC6 0%, #0F3A96 100%);
    border-radius: var(--radius-lg);
    padding: 1.4rem;
    color: white;
  }

  .found-panel {
    background: var(--green-subtle);
    border: 1px solid #BBF7D0;
    border-radius: var(--radius-lg);
    padding: 1.4rem;
    margin-bottom: 1.5rem;
  }

  .live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    background: var(--yellow);
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 6px;
    animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

  .role-faculty {
    display: inline-block; padding: 2px 9px;
    background: var(--blue-light); color: var(--blue);
    border-radius: 6px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .06em;
    border: 1px solid #BFDBFE;
    font-family: 'DM Mono', monospace;
  }
  .role-student {
    display: inline-block; padding: 2px 9px;
    background: #FFFBEB; color: #92400E;
    border-radius: 6px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .06em;
    border: 1px solid #FCD34D;
    font-family: 'DM Mono', monospace;
  }

  .login-wrap {
    max-width: 460px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: var(--shadow-lg);
  }

  hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

  h1 { font-weight: 700 !important; letter-spacing: -.03em !important; }
  h2 { font-weight: 700 !important; letter-spacing: -.02em !important; }
  h3 { font-weight: 600 !important; letter-spacing: -.02em !important; }

  .stCaption { font-size: .78rem !important; color: var(--muted) !important; }

  code {
    font-family: 'DM Mono', monospace !important;
    font-size: .8em !important;
    background: #F1F3F5 !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    padding: 1px 5px !important;
    color: var(--text-secondary) !important;
  }

  .section-label {
    font-size: .68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    color: var(--blue);
    margin-bottom: 6px;
    display: block;
  }

  /* ── Pagination ── */
  .pg-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 1.5rem;
    padding: 1rem 0;
    border-top: 1px solid var(--border);
    gap: 12px;
  }
  .pg-pills {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }
  .pg-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 7px;
    font-size: .78rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    border: 1px solid var(--border);
    color: #6B7280;
    background: white;
  }
  .pg-pill.active {
    background: var(--blue);
    color: white;
    border-color: var(--blue);
    box-shadow: 0 1px 4px rgba(22,78,198,.25);
  }
  .pg-info {
    text-align: center;
    font-size: .7rem;
    color: #9CA3AF;
    margin-top: 4px;
    font-family: 'DM Mono', monospace;
  }
</style>
""", unsafe_allow_html=True)
