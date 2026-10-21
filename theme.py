import html
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

:root {
  --g900:#052E26; --g800:#064E3B; --g700:#0F766E; --g500:#16A34A; --g300:#86EFAC;
  --ink:#0B2B26; --mute:#5B6F68; --line:#DCEBE3; --card:#FFFFFF;
  --sh1:0 2px 10px rgba(6,78,59,.06); --sh2:0 14px 34px rgba(6,78,59,.12);
}
html, body, .stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp button, .stApp input, .stApp textarea, .stApp th, .stApp td, [data-testid="stMarkdownContainer"] {
  font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
}
.stApp {
  background:
    radial-gradient(900px 420px at 8% -5%, rgba(34,197,94,.14), transparent 60%),
    radial-gradient(800px 400px at 100% 0%, rgba(15,118,110,.14), transparent 55%),
    linear-gradient(180deg, #F2F9F5 0%, #FFFFFF 60%);
}
.block-container { padding-top: 1rem; max-width: 1220px; animation: fadeUp .6s ease both; }
.block-container::after {
  content: "💧 Sinchai AI  ·  Made with ❤ in Chhattisgarh"; display: block; text-align: center;
  color: var(--mute); font-size: .78rem; margin-top: 48px; padding: 18px 0 6px; border-top: 1px solid var(--line);
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #BFDCCF; border-radius: 8px; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes flow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes floaty { 0%,100% { transform: translateY(0) rotate(-6deg); } 50% { transform: translateY(-12px) rotate(6deg); } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(134,239,172,.8); } 100% { box-shadow: 0 0 0 10px rgba(134,239,172,0); } }

/* sidebar */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #E9F5EE 0%, #F6FBF8 100%); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: var(--g800); font-weight: 700; }

/* hero */
.hero { position: relative; overflow: hidden; border-radius: 26px; padding: 34px 38px; color: #fff; margin-bottom: 22px;
  background: linear-gradient(120deg, #052E26, #0F766E, #15803D, #0F766E, #052E26); background-size: 300% 300%;
  animation: flow 14s ease infinite; box-shadow: 0 22px 48px rgba(6,78,59,.34); border: 1px solid rgba(255,255,255,.12); }
.hero:before { content:""; position:absolute; inset:0;
  background: radial-gradient(circle at 85% 20%, rgba(255,255,255,.22), transparent 38%),
              radial-gradient(circle at 10% 110%, rgba(134,239,172,.25), transparent 45%); }
.hero:after { content:"💧"; position:absolute; right: 42px; top: 20px; font-size: 5.2rem; opacity: .22;
  animation: floaty 6s ease-in-out infinite; filter: blur(.4px); }
.hero > * { position: relative; z-index: 1; }
.hero-t { font-size: 2.5rem; font-weight: 800; letter-spacing: -1px; line-height: 1.12;
  text-shadow: 0 2px 18px rgba(0,0,0,.25); }
.hero-s { opacity: .9; margin-top: 10px; font-size: 1rem; max-width: 720px; line-height: 1.55; }
.chip { display: inline-flex; align-items: center; gap: 6px; background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.28); backdrop-filter: blur(8px); padding: 5px 14px;
  border-radius: 999px; font-size: .76rem; font-weight: 500; margin: 16px 8px 0 0; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--g300); animation: pulse 1.6s infinite; }

/* metrics */
[data-testid="stMetric"] { position: relative; overflow: hidden; background: var(--card); border: 1px solid var(--line);
  border-radius: 18px; padding: 16px 20px; box-shadow: var(--sh1); transition: transform .2s ease, box-shadow .2s ease; }
[data-testid="stMetric"]:before { content:""; position:absolute; left:0; top:0; right:0; height:4px;
  background: linear-gradient(90deg, var(--g700), var(--g500)); }
[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: var(--sh2); }
[data-testid="stMetricLabel"] { color: var(--mute); font-weight: 500; font-size: .85rem; }
[data-testid="stMetricValue"] { color: var(--g800); font-weight: 800; letter-spacing: -.5px; }

/* tabs */
[data-baseweb="tab-list"] { gap: 4px; background: rgba(15,118,110,.08); padding: 5px; border-radius: 16px; border: 1px solid var(--line); }
button[data-baseweb="tab"] { border-radius: 12px; padding: 9px 18px; height: auto; font-weight: 500; color: var(--mute); transition: all .2s; }
button[data-baseweb="tab"]:hover { color: var(--g700); background: rgba(255,255,255,.6); }
button[data-baseweb="tab"][aria-selected="true"] { background: #fff; color: var(--g700); font-weight: 700; box-shadow: 0 4px 12px rgba(6,78,59,.12); }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }

/* buttons */
.stButton > button, .stFormSubmitButton > button {
  background: linear-gradient(135deg, #0F766E 0%, #16A34A 100%); color: #fff; border: 0; border-radius: 14px;
  padding: .6rem 1.5rem; font-weight: 600; letter-spacing: .2px; box-shadow: 0 8px 20px rgba(15,118,110,.28);
  transition: transform .15s ease, box-shadow .15s ease, filter .15s; }
.stButton > button:hover, .stFormSubmitButton > button:hover { transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(15,118,110,.36); filter: brightness(1.05); color: #fff; border: 0; }
.stButton > button:active { transform: translateY(0); }

/* inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea { border-radius: 12px; border: 1px solid var(--line); background: #fff; }
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { border-color: var(--g700); box-shadow: 0 0 0 3px rgba(15,118,110,.15); }
[data-baseweb="select"] > div { border-radius: 12px; border-color: var(--line); background: #fff; }
[data-testid="stFileUploader"] section { border-radius: 16px; border: 2px dashed #A7D3C0; background: rgba(255,255,255,.7); }

/* containers */
[data-testid="stForm"] { background: rgba(255,255,255,.85); backdrop-filter: blur(10px); border: 1px solid var(--line);
  border-radius: 22px; padding: 26px; box-shadow: var(--sh2); }
[data-testid="stExpander"] { background: #fff; border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--sh1); }
[data-testid="stAlert"] { border-radius: 16px; border: 0; box-shadow: var(--sh1); }
[data-testid="stDataFrame"], [data-testid="stTable"] { border-radius: 16px; overflow: hidden; border: 1px solid var(--line); box-shadow: var(--sh1); }
[data-testid="stChatMessage"] { background: #fff; border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--sh1); }
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 12px; box-shadow: var(--sh1); }

/* decision card */
.dec { display: flex; gap: 20px; align-items: center; background: #fff; border-radius: 24px; padding: 24px 26px;
  border: 1px solid var(--line); box-shadow: var(--sh2); margin: 18px 0; position: relative; overflow: hidden; animation: fadeUp .5s ease both; }
.dec:before { content:""; position:absolute; left:0; top:0; bottom:0; width:7px; }
.dec.good:before { background: linear-gradient(180deg, #22C55E, #0F766E); }
.dec.warn:before { background: linear-gradient(180deg, #FBBF24, #F97316); }
.dec-ic { flex: 0 0 auto; width: 68px; height: 68px; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2rem; }
.good .dec-ic { background: linear-gradient(135deg, #DCFCE7, #BBF7D0); }
.warn .dec-ic { background: linear-gradient(135deg, #FEF3C7, #FDE68A); }
.dec-body { flex: 1; min-width: 0; }
.dec-pill { display: inline-block; padding: 5px 14px; border-radius: 999px; font-weight: 800; font-size: .78rem; letter-spacing: 1px; }
.good .dec-pill { background: #166534; color: #fff; }
.warn .dec-pill { background: #B45309; color: #fff; }
.dec-txt { font-size: 1.15rem; color: var(--ink); line-height: 1.6; margin-top: 10px; font-weight: 500; }
.gauge { margin-top: 16px; }
.gauge-top { display: flex; justify-content: space-between; font-size: .8rem; color: var(--mute); margin-bottom: 6px; }
.gauge-top b { color: var(--g800); }
.gauge-bar { height: 10px; background: #E3EFE9; border-radius: 999px; overflow: hidden; }
.gauge-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #F59E0B, #22C55E 50%, #0EA5E9); transition: width 1s ease; }

/* phone */
.ph { background: linear-gradient(160deg, #10241F, #0B1613); border-radius: 36px; padding: 11px;
  box-shadow: 0 22px 44px rgba(0,0,0,.3), inset 0 0 0 1px rgba(255,255,255,.08); transition: transform .25s; }
.ph:hover { transform: translateY(-6px) rotate(-.6deg); }
.ph-notch { width: 84px; height: 7px; background: #26413A; border-radius: 8px; margin: 3px auto 9px; }
.ph-in { background: linear-gradient(180deg, #ECF3EF, #F7FAF8); border-radius: 26px; padding: 14px; min-height: 230px; }
.ph-h { display: flex; align-items: center; gap: 10px; padding-bottom: 10px; border-bottom: 1px solid #DDE8E2; }
.ph-av { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #0F766E, #22C55E); display: flex; align-items: center; justify-content: center; font-size: .95rem; }
.ph-n { font-size: .82rem; font-weight: 700; color: var(--g800); line-height: 1.2; }
.ph-n small { display: block; font-weight: 400; color: var(--mute); font-size: .68rem; }
.bub { background: #fff; border-radius: 4px 18px 18px 18px; padding: 11px 13px; margin-top: 14px; font-size: .93rem;
  color: #111; line-height: 1.55; box-shadow: 0 2px 8px rgba(0,0,0,.08); animation: fadeUp .5s ease both; }
.ph-m { font-size: .7rem; color: var(--mute); margin-top: 10px; text-align: right; }
</style>
"""

ICON = {"SOW": "🌱", "IRRIGATE": "💧", "WAIT": "⏳", "SWITCH": "🔄", "CHECK_SENSOR": "🛠"}

def inject():
    st.markdown(CSS, unsafe_allow_html=True)

def hero(title, sub, chips=()):
    ch = '<span class="chip"><span class="dot"></span>Live</span>'
    ch += "".join('<span class="chip">' + html.escape(c) + '</span>' for c in chips)
    st.markdown('<div class="hero"><div class="hero-t">' + html.escape(title) + '</div><div class="hero-s">'
                + html.escape(sub) + '</div><div>' + ch + '</div></div>', unsafe_allow_html=True)

def decision(code, text, good, moisture=None):
    cls = "good" if good else "warn"
    bar = ""
    if moisture is not None:
        m = max(0, min(100, float(moisture)))
        bar = ('<div class="gauge"><div class="gauge-top"><span>Soil moisture</span><b>' + f"{m:.0f}%"
               + '</b></div><div class="gauge-bar"><div class="gauge-fill" style="width:' + f"{m:.0f}" + '%"></div></div></div>')
    st.markdown('<div class="dec ' + cls + '"><div class="dec-ic">' + ICON.get(code, "💧") + '</div><div class="dec-body">'
                '<span class="dec-pill">' + html.escape(code) + '</span><div class="dec-txt">' + html.escape(text)
                + '</div>' + bar + '</div></div>', unsafe_allow_html=True)

def phone(label, text, meta):
    return ('<div class="ph"><div class="ph-notch"></div><div class="ph-in"><div class="ph-h"><div class="ph-av">💧</div>'
            '<div class="ph-n">Sinchai<small>' + html.escape(label) + ' · SMS</small></div></div>'
            '<div class="bub">' + html.escape(text) + '</div><div class="ph-m">' + html.escape(meta) + '</div></div></div>')