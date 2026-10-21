import os, datetime
import streamlit as st
from crop_table import CROPS
from rules import decide
from forecast import get_forecast
from sensor_health import check, simulate_history, evaluate
from fertiliser_table import recommend
from llm import read_card, explain_card, chat
import msgs, db, theme
from ui import T, LANGS

st.set_page_config(page_title="Sinchai AI", page_icon="💧", layout="wide")
theme.inject()

def _secret():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""

lang = st.sidebar.selectbox("🌐 भाषा / भाखा / Language", list(LANGS), format_func=lambda x: LANGS[x])
t = lambda k: T(k, lang)
LNAME = {"hi": "Hindi", "cg": "Chhattisgarhi", "en": "English"}
theme.hero(t("app_title"), t("caption"), ["Smart Irrigation", "Hindi · छत्तीसगढ़ी · English", "SMS-first"])

with st.sidebar:
    st.header(t("settings"))
    k = st.text_input("Gemini API key (optional)", type="password", value=os.getenv("GEMINI_API_KEY", "") or _secret())
    if k:
        os.environ["GEMINI_API_KEY"] = k
    if st.button(t("gemini_test")):
        from llm import _call
        try:
            st.success("OK: " + _call([{"text": "Sirf ek shabd bolo: ok"}])[:30])
        except Exception as e:
            st.error(str(e)[:200])
    crop = st.selectbox(t("crop"), list(CROPS), format_func=lambda x: msgs.CROPN[x][lang])
    stage = st.selectbox(t("stage"), list(CROPS[crop]["stages"]))
    moisture = st.slider(t("moisture"), 0, 100, 30)
    fault = st.selectbox(t("fault"), ["none", "flatline", "jump", "out_of_range"])
    delay = st.slider(t("delay"), 0, 30, 0)
    st.divider()
    live = st.checkbox(t("live"), value=False)
    fc = None
    if live:
        lat = st.number_input("Latitude", value=21.25); lon = st.number_input("Longitude", value=81.63)
        fc = get_forecast(lat, lon)
        if fc is None:
            st.warning("Forecast nahi mila, manual sliders use ho rahe hain")
    if fc is None:
        rain3 = st.slider(t("rain3"), 0, 100, 0)
        tmin = st.slider(t("tmin"), -2, 30, 15)
        tmax = st.slider(t("tmax"), 15, 48, 32)
        daily = [rain3 / 3.0] * 3
    else:
        rain3, tmin, tmax, daily = fc["rain3"], fc["tmin"], fc["tmax"], fc["daily"]
        st.info(f"{rain3:.0f} mm, min {tmin:.1f} C, max {tmax:.1f} C")
    try:
        st.divider()
        st.caption(f"👥 {len(db.farmers())} registered | 📨 {len(db.outbox(1000))} SMS")
    except Exception:
        pass

hist = simulate_history(moisture, fault)
health = check(hist)
d = decide(hist[-1], rain3, crop, stage, sensor_ok=(health["status"] == "OK"), delay_days=delay)
text = msgs.compose(d, lang, rain3, daily, hist[-1])
al = msgs.alert_texts(tmin, tmax, rain3, lang)

t1, t2, t3, t4, t5, t6 = st.tabs([t("tab_decision"), t("tab_sms"), t("tab_card"), t("tab_chat"), t("tab_health"), t("tab_sim")])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric(t("decision"), d["code"])
    c2.metric(t("moist_now"), f"{hist[-1]}%")
    c3.metric("Kc / " + t("critical"), f"{d['kc']} / {t('yes') if d['critical'] else t('no')}")
    theme.decision(d["code"], text, d["code"] in ("SOW", "IRRIGATE"), hist[-1])
    for a in al:
        st.error(f"⚠️ {a}")
    st.line_chart(hist, color="#0F766E")

with t2:
    st.write(t("msg_in"))
    cols = st.columns(3)
    for col, lg in zip(cols, ["hi", "cg", "en"]):
        s = msgs.compose(d, lg, rain3, daily, hist[-1])
        col.markdown(theme.phone(LANGS[lg], s, f"{len(s)} chars | {msgs.seg(s)} SMS"), unsafe_allow_html=True)
    st.write("")
    for lg in ["hi", "cg", "en"]:
        for a in msgs.alert_texts(tmin, tmax, rain3, lg):
            st.warning(f"[{LANGS[lg]}] {a}")

with t3:
    up = st.file_uploader(t("upload_card"), type=["jpg", "jpeg", "png"])
    if up and st.button(t("read_card")):
        card = read_card(up.getvalue(), up.type or "image/jpeg")
        if "error" in card:
            st.error(card["error"])
        else:
            st.json(card)
            rec = recommend(card, crop)
            st.write("kg/hectare:", rec["dose_kg_ha"])
            st.info(explain_card(card, rec))
    with st.expander("Sample card", expanded=not up):
        s = {"N": 250, "P": 8, "K": 150, "pH": 5.8, "OC": 0.45}
        rec = recommend(s, crop)
        st.json({"card": s, "recommendation": rec})
        st.info(explain_card(s, rec))

with t4:
    ctx = {"fasal": msgs.CROPN[crop]["en"], "stage": stage, "nami_pct": hist[-1], "baarish_3din_mm": rain3,
           "min_temp": tmin, "max_temp": tmax, "decision": {"code": d["code"], "reason": d["reason"]},
           "sensor": health, "alerts": al}
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    for m in st.session_state.msgs:
        st.chat_message(m["r"]).write(m["t"])
    q = st.chat_input(t("ask_ph"))
    if q:
        a, src = chat(f"[Reply in {LNAME[lang]}] {q}", ctx)
        st.session_state.msgs.append({"r": "user", "t": q})
        st.session_state.msgs.append({"r": "assistant", "t": f"{a}\n\n*({src})*"})
        st.rerun()

with t5:
    (st.success if health["status"] == "OK" else st.error)(f"{health['status']}: {health['reason']} (layer: {health['layer']})")
    st.line_chart(hist, color="#0F766E")
    if st.button(t("test_btn")):
        r = evaluate(200)
        st.table({"Case": list(r.keys()), "%": [round(v * 100, 1) for v in r.values()]})
        st.caption("200 simulated trials per case.")

with t6:
    st.write(t("sim_note"))
    rate = st.slider(t("drop"), 1.0, 6.0, 3.0)
    rows = []
    m = float(moisture)
    for i in range(1, 8):
        dd = decide(m, rain3, crop, stage)
        rows.append({"Din": i, "Nami %": round(m, 1), "Faisla": dd["code"], "SMS": msgs.compose(dd, lang, rain3, daily, m)})
        m = max(0.0, m - rate) if dd["code"] != "IRRIGATE" else min(100.0, m + 20)
    st.table(rows)