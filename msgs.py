# CHHATTISGARHI WALE TEXT KISI NATIVE SPEAKER SE CHECK KARWAO. SOIL FACTORS PLACEHOLDER HAIN (KVK se verify karo).
CROPN = {
 "rice_dsr": {"hi": "धान", "cg": "धान", "en": "paddy"},
 "wheat":    {"hi": "गेहूं", "cg": "गहूं", "en": "wheat"},
 "chana":    {"hi": "चना", "cg": "चना", "en": "chana"},
 "soybean":  {"hi": "सोयाबीन", "cg": "सोयाबीन", "en": "soybean"},
}
# soil key: (naam, factor). factor >1 = jaldi sookhti hai, to jaldi sinchai ka signal.
SOIL = {
 "bhata":  ({"hi": "भाटा (हल्की, कंकरीली)", "cg": "भाठा (हल्का, कंकरीला)", "en": "Bhata (light, gravelly)"}, 1.15),
 "matasi": ({"hi": "मटासी (हल्की पीली-भूरी)", "cg": "मटासी (हल्का पीला-भूरा)", "en": "Matasi (light yellow-brown)"}, 1.05),
 "dorsa":  ({"hi": "डोरसा (दोमट)", "cg": "डोरसा (दोमट)", "en": "Dorsa (loamy)"}, 1.0),
 "kanhar": ({"hi": "कन्हार (भारी, काली)", "cg": "कन्हार (भारी, करिया)", "en": "Kanhar (heavy, black)"}, 0.85),
}
ACT = {
 "sow": {"hi": "बुवाई", "cg": "बोनी", "en": "sow"},
 "irr": {"hi": "सिंचाई", "cg": "सिंचाई", "en": "irrigate"},
}
TPL = {
 "SOW": {"hi": "{crop} की बुवाई करें। मिट्टी में नमी ठीक है।",
         "cg": "{crop} के बोनी करव। माटी म नमी बने हे।",
         "en": "Sow {crop} now. Soil moisture is good."},
 "WAIT_RAIN": {"hi": "अगले 3 दिन में {n} दिन बारिश ({mm} मिमी) होगी, नमी बढ़ेगी। अभी {act} न करें।",
               "cg": "अवइया 3 दिन म {n} दिन पानी गिरही ({mm} मिमी), नमी बढ़ही। अभी {act} झन करव।",
               "en": "Rain on {n} of the next 3 days ({mm} mm), moisture will rise. Do not {act} now."},
 "WAIT_STORM": {"hi": "बहुत तेज़ बारिश ({mm} मिमी) आने वाली है। बीज बह सकता है, बुवाई रोकें।",
                "cg": "बहुत जोर के पानी ({mm} मिमी) आवत हे। बीज बह सकथे, बोनी झन करव।",
                "en": "Heavy rain ({mm} mm) is coming. Seeds may wash away; hold sowing."},
 "WAIT_DRY": {"hi": "अभी बुवाई रोकें। नमी कम है और बारिश भी कम है।",
              "cg": "अभी बोनी झन करव। नमी कम हे अउ पानी घलो कम हे।",
              "en": "Hold sowing. Soil is dry and little rain is expected."},
 "WAIT_OK": {"hi": "अभी सिंचाई की जरूरत नहीं, नमी ठीक है।",
             "cg": "अभी सिंचाई के जरूरत नइ हे, नमी बने हे।",
             "en": "No irrigation needed now. Moisture is fine."},
 "IRRIGATE": {"hi": "{crop} में सिंचाई करें। नमी {m}% है, कम है।",
              "cg": "{crop} म सिंचाई करव। नमी {m}% हे, कम हे।",
              "en": "Irrigate {crop}. Moisture is {m}%, which is low."},
 "SWITCH": {"hi": "बुवाई में देर हो गई। {alt} पर विचार करें, KVK से पूछें।",
            "cg": "बोनी म देरी होगे हे। {alt} बर सोचव, KVK ले पूछव।",
            "en": "Sowing is late. Consider {alt}; ask your KVK."},
 "CHECK_SENSOR": {"hi": "सेंसर जांचें। आज मौसम पूर्वानुमान के अनुसार चलें।",
                  "cg": "सेंसर ला जांचव। आज मौसम के अनुमान देख के चलव।",
                  "en": "Check the sensor. Follow the weather forecast today."},
}
AL = {
 "PAALA": {"hi": "पाले का खतरा: न्यूनतम तापमान {t}°C। बचाव के लिए KVK से पूछें।",
           "cg": "पाला के खतरा: कम से कम तापमान {t}°C। बचाव बर KVK ले पूछव।",
           "en": "Frost risk: minimum temperature {t} C. Ask KVK how to protect crops."},
 "GARMI": {"hi": "लू/गर्मी का खतरा: अधिकतम तापमान {t}°C।",
           "cg": "लू/गर्मी के खतरा: जादा ले जादा तापमान {t}°C।",
           "en": "Heat risk: maximum temperature {t} C."},
 "BAARISH": {"hi": "भारी बारिश: 3 दिन में {mm} मिमी।",
             "cg": "भारी पानी: 3 दिन म {mm} मिमी।",
             "en": "Heavy rain: {mm} mm in 3 days."},
}
FOOT = {"hi": " -सिंचाई", "cg": " -सिंचाई", "en": " -Sinchai"}

def compose(d, lang, rain3, daily, moisture):
    """d = rules.decide() ka result. Faisla badalta nahi, sirf bhasha mein likhta hai."""
    code, stage = d["code"], d["stage"]
    key = code
    if code == "WAIT":
        if stage == "sowing" and rain3 >= 50: key = "WAIT_STORM"
        elif rain3 >= 5: key = "WAIT_RAIN"
        elif stage == "sowing": key = "WAIT_DRY"
        else: key = "WAIT_OK"
    n = max(1, sum(1 for x in daily if x >= 2))
    act = ACT["sow" if stage == "sowing" else "irr"][lang]
    txt = TPL[key][lang].format(crop=CROPN[d["crop"]][lang], alt=CROPN[d["alt"]][lang],
                                n=n, mm=round(rain3), act=act, m=round(moisture))
    return txt + FOOT[lang]

def alert_texts(tmin, tmax, rain3, lang):
    out = []
    if tmin <= 4: out.append(AL["PAALA"][lang].format(t=round(tmin, 1)))
    if tmax >= 40: out.append(AL["GARMI"][lang].format(t=round(tmax, 1)))
    if rain3 >= 50: out.append(AL["BAARISH"][lang].format(mm=round(rain3)))
    return out

def seg(t):
    n = len(t)
    if t.isascii(): return 1 if n <= 160 else -(-n // 153)
    return 1 if n <= 70 else -(-n // 67)