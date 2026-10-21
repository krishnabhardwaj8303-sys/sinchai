import os, re
import streamlit as st
import db, msgs, gateway, theme
from crop_table import CROPS
from rules import decide
from forecast import get_forecast
from sensor_health import check, simulate_history
from ui import T, LANGS

st.set_page_config(page_title="Sinchai Registration", page_icon="🌾", layout="wide")
theme.inject()
lang = st.sidebar.selectbox("🌐 भाषा / भाखा / Language", list(LANGS), format_func=lambda x: LANGS[x])
t = lambda k: T(k, lang)
theme.hero(t("reg_title"), t("reg_sub"), ["Free", "No internet needed", "Chhattisgarh"])
mode = st.sidebar.radio(t("mode"), ["farmer", "op"], format_func=lambda x: t("m_farmer") if x == "farmer" else t("m_op"))

soil_label = lambda x: msgs.SOIL[x][0][lang]
crop_label = lambda x: msgs.CROPN[x][lang]

def register(op):
    with st.form("reg_op" if op else "reg_farmer", clear_on_submit=True):
        name = st.text_input(t("name"))
        phone = st.text_input(t("phone"))
        village = st.text_input(t("village"))
        crop = st.selectbox(t("crop"), list(CROPS), format_func=crop_label)
        mlang = st.selectbox(t("msg_lang"), list(LANGS), index=list(LANGS).index(lang), format_func=lambda x: LANGS[x])
        photo = st.file_uploader(t("photo"), type=["jpg", "jpeg", "png"])
        soil, node = "dorsa", "NODE-01"
        if op:
            soil = st.selectbox(t("soil"), list(msgs.SOIL), format_func=soil_label)
            node = st.text_input(t("node"), "NODE-01")
        ok = st.form_submit_button(t("submit"))
    if ok:
        p = re.sub(r"\D", "", phone)[-10:]
        if not name.strip():
            st.error(t("bad_name"))
        elif not re.fullmatch(r"[6-9]\d{9}", p):
            st.error(t("bad_phone"))
        else:
            try:
                ext = os.path.splitext(photo.name)[1].lower() if photo else ".jpg"
                db.add_farmer(name.strip(), p, village.strip(), crop, mlang, photo.getvalue() if photo else None, ext,
                              soil, node.strip() or "NODE-01", "active" if op else "pending")
                st.success(t("ok_added") if op else t("ok_reg"))
            except ValueError:
                st.error(t("dup_phone"))

def get_fc():
    c1, c2 = st.columns(2)
    live = c1.checkbox(t("live"), value=False)
    fc = None
    if live:
        lat = c2.number_input("Latitude", value=21.25); lon = c2.number_input("Longitude", value=81.63)
        fc = get_forecast(lat, lon)
        if fc is None:
            st.warning("Forecast nahi mila, manual values use karo")
    if fc is None:
        cc = st.columns(5)
        r = [cc[i].number_input(f"{t('rain_day')} {i + 1} (mm)", 0.0, 200.0, 0.0) for i in range(3)]
        tmin = cc[3].number_input(t("tmin"), -5.0, 35.0, 15.0)
        tmax = cc[4].number_input(t("tmax"), 10.0, 50.0, 32.0)
        fc = {"rain3": sum(r), "daily": r, "tmin": tmin, "tmax": tmax}
    return fc

def plan(node, fc):
    hist = db.history(node)
    if not hist:
        return None
    health = check(hist)
    rows = []
    for f in db.farmers(status="active", node=node):
        fac = msgs.SOIL.get(f["soil"], (None, 1.0))[1]
        d = decide(hist[-1] / fac, fc["rain3"], f["crop"], f["stage"], sensor_ok=(health["status"] == "OK"))
        text = msgs.compose(d, f["lang"], fc["rain3"], fc["daily"], hist[-1])
        al = msgs.alert_texts(fc["tmin"], fc["tmax"], fc["rain3"], f["lang"])
        rows.append((f, d, text, al))
    return health, hist, rows

if mode == "farmer":
    register(False)
    st.stop()

# ---------- operator ----------
if not st.session_state.get("op"):
    pin = st.text_input(t("pin"), type="password")
    if st.button("OK"):
        if pin == os.getenv("SINCHAI_PIN", "1234"):
            st.session_state.op = True
            st.rerun()
        else:
            st.error(t("wrong_pin"))
    st.stop()

try:
    a, b, c = st.columns(3)
    a.metric("👥 " + t("t_farmers"), len(db.farmers(status="active")))
    b.metric("⏳ " + t("t_pending"), len(db.farmers(status="pending")))
    c.metric("📨 " + t("t_out"), len(db.outbox(1000)))
except Exception:
    pass

tn, tp, tf, th, to = st.tabs([t("t_new"), t("t_pending"), t("t_farmers"), t("t_hw"), t("t_out")])

with tn:
    register(True)

with tp:
    pend = db.farmers(status="pending")
    if not pend:
        st.info(t("none"))
    for f in pend:
        with st.expander(f"{f['name']} · {f['phone']} · {f['village']} · {crop_label(f['crop'])}"):
            c1, c2 = st.columns([1, 2])
            if f["photo"] and os.path.exists(f["photo"]):
                c1.image(f["photo"], width=220)
            soil = c2.selectbox(t("soil"), list(msgs.SOIL), format_func=soil_label, key=f"s{f['id']}")
            node = c2.text_input(t("node"), "NODE-01", key=f"n{f['id']}")
            if c2.button(t("activate"), key=f"a{f['id']}"):
                db.update_farmer(f["id"], soil=soil, node_id=node.strip() or "NODE-01", status="active")
                st.rerun()

with tf:
    act = db.farmers(status="active")
    if not act:
        st.info(t("none"))
    else:
        st.dataframe([{"ID": f["id"], t("name"): f["name"], t("phone"): f["phone"], t("village"): f["village"],
                       t("crop"): crop_label(f["crop"]), t("stage"): f["stage"], t("soil"): soil_label(f["soil"]),
                       t("node"): f["node_id"], "SMS": LANGS[f["lang"]]} for f in act], use_container_width=True)
        by = {f["id"]: f for f in act}
        fid = st.selectbox(t("name"), list(by), format_func=lambda i: f"{by[i]['name']} ({by[i]['phone']})")
        stages = list(CROPS[by[fid]["crop"]]["stages"])
        cur = stages.index(by[fid]["stage"]) if by[fid]["stage"] in stages else 0
        ns = st.selectbox(t("stage"), stages, index=cur)
        if st.button(t("save")):
            db.update_farmer(fid, stage=ns)
            st.rerun()

with th:
    nodes = db.nodes()
    if not nodes:
        st.info(t("none"))
    else:
        node = st.selectbox(t("node"), nodes)
        c1, c2, c3 = st.columns(3)
        m = c1.slider(t("moisture"), 0, 100, 30)
        fault = c2.selectbox(t("fault"), ["none", "flatline", "jump", "out_of_range"])
        if c3.button(t("send_sim")):
            db.replace_history(node, simulate_history(m, fault))
            st.rerun()
        fc = get_fc()
        res = plan(node, fc)
        if res is None:
            st.info(t("no_data"))
        else:
            health, hist, rows = res
            (st.success if health["status"] == "OK" else st.error)(f"Sensor {health['status']}: {health['reason']}")
            st.line_chart(hist, color="#0F766E")
            st.dataframe([{"Kisaan": f["name"], "Mitti": soil_label(f["soil"]),
                           "Fasal/Stage": f"{crop_label(f['crop'])} / {f['stage']}", "Faisla": d["code"],
                           "SMS": text, "Seg": msgs.seg(text)} for f, d, text, al in rows], use_container_width=True)
            if st.button(t("queue_all")):
                n = 0
                for f, d, text, al in rows:
                    db.queue_sms(f["id"], f["phone"], f["lang"], d["code"], text, gateway.send(f["phone"], text)); n += 1
                    for a in al:
                        db.queue_sms(f["id"], f["phone"], f["lang"], "ALERT", a, gateway.send(f["phone"], a)); n += 1
                st.success(f"{t('queued')} {n}")

with to:
    ob = db.outbox()
    if not ob:
        st.info(t("none"))
    else:
        st.dataframe(ob, use_container_width=True)