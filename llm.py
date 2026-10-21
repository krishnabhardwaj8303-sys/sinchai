import os, json, base64, requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")  # naam badal gaya ho to AI Studio mein check karo

FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-flash-lite-latest")

def _call(parts, system=None, json_mode=False):
    import time
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("no key")
    body = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2}}
    if system:
        body["system_instruction"] = {"parts": [{"text": system}]}
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    last = None
    for model in [MODEL, FALLBACK_MODEL]:
        for attempt in range(4):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                              headers={"x-goog-api-key": key}, json=body, timeout=60)
            if r.ok:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            last = f"HTTP {r.status_code} ({model}): {r.text[:150]}"
            if r.status_code in (429, 500, 503):
                time.sleep(3 * (2 ** attempt))   # 3, 6, 12, 24 sec
                continue
            break   # 400/403/404 retry se theek nahi hote
    raise ValueError(last)

# ---------- Feature 13: AI Message Writer (fallback ke saath) ----------
TEMPLATES = {
    "SOW": "{day}: {crop} बोएं। मिट्टी में नमी ठीक है। -सिंचाई",
    "WAIT": "{day}: {crop} - अभी रुकें, बुवाई/सिंचाई न करें। -सिंचाई",
    "IRRIGATE": "{day}: {crop} की सिंचाई करें, नमी कम है। -सिंचाई",
    "SWITCH": "{day}: बुवाई में देर है। {alt} पर विचार करें, KVK से पूछें। -सिंचाई",
    "CHECK_SENSOR": "{day}: सेंसर जांचें। आज मौसम पूर्वानुमान के अनुसार चलें। -सिंचाई",
}

KEY = {"SOW": ["बो", "बुवाई"], "WAIT": ["रुक", "न करें", "इंतज"], "IRRIGATE": ["सिंचाई", "पानी"],
       "SWITCH": ["KVK", "विचार", "बदल"], "CHECK_SENSOR": ["सेंसर"]}
BAD = {"SOW": ["न बोएं", "मत बोएं", "रुकें", "बुवाई न", "बुवाई मत"],
       "WAIT": ["सिंचाई करें", "बोएं", "बोयें", "पानी दें"],
       "IRRIGATE": ["सिंचाई न", "सिंचाई मत", "रुकें"], "SWITCH": [], "CHECK_SENSOR": []}

def _consistent(code, s):
    """LLM ka SMS faisle se mel khata hai ya nahi. Nahi to template chalega."""
    return any(k in s for k in KEY[code]) and not any(b in s for b in BAD[code])

def write_sms(d, day):
    """Return (sms_text, source). LLM ko faisla badalne ki permission nahi."""
    fallback = TEMPLATES[d["code"]].format(day=day, crop=d["crop_hi"], alt=d["alt_hi"])
    try:
        prompt = (f"Faisla (badalna mat): {d['code']}\nFasal: {d['crop_hi']}\nDin: {day}\nWajah: {d['reason']}\n"
                  "Is faisle ko kisaan ke liye saral Hindi (Devanagari) SMS mein likho. Max 130 characters. "
                  "Sirf SMS text do. Naya salah mat jodo. Ant mein -सिंचाई.")
        out = _call([{"text": prompt}], system="Tum kisaan ke liye chhote Hindi SMS likhte ho.")
        if 0 < len(out) <= 134 and _consistent(d["code"], out):
            return out, "LLM"
    except Exception:
        pass
    return fallback, "Template (fallback)"

def segments(text):
    """Unicode SMS: 70 chars ka 1 segment, usse zyada ho to 67 chars per segment."""
    n = len(text)
    return 1 if n <= 70 else -(-n // 67)

# ---------- Feature 7: Soil Health Card Reader ----------
def read_card(img_bytes, mime="image/jpeg"):
    prompt = ("Ye Soil Health Card ki photo hai. Sirf JSON do: "
              '{"N":number|null,"P":number|null,"K":number|null,"pH":number|null,"OC":number|null,"EC":number|null,"crop":string|null}. '
              "Jo value saaf na dikhe use null rakho. Andaza mat lagao.")
    parts = [{"inline_data": {"mime_type": mime, "data": base64.b64encode(img_bytes).decode()}}, {"text": prompt}]
    try:
        card = json.loads(_call(parts, json_mode=True))
    except RuntimeError:
        return {"error": "Gemini API key nahi hai. Sidebar mein key daalo ya neeche sample card use karo."}
    except Exception as e:
        return {"error": f"Card nahi padha ja saka ({e}). Dobara photo lein."}
    if not isinstance(card, dict) or any(card.get(k) is None for k in ("N", "P", "K", "pH")):
        return {"error": "Card dhundhla hai ya values nahi dikh rahin. Dobara photo lein.", "partial": card}
    return card

def explain_card(card, rec):
    """LLM sirf table ke result ko saral Hindi mein samjhata hai."""
    L = rec["levels"]; D = rec["dose_kg_ha"]
    fb = (f"Aapki mitti mein Nitrogen {L['N']}, Phosphorus {L['P']}, Potash {L['K']} hai. "
          f"Khaad (kg/hectare): N {D['N']}, P2O5 {D['P']}, K2O {D['K']}. " + " ".join(rec["notes"]))
    try:
        p = ("Ye mitti ki jaanch aur khaad ki matra hai (table se nikali hui, badalna mat):\n"
             f"{json.dumps({'card': card, 'recommendation': rec}, ensure_ascii=False)}\n"
             "Kisaan ko 4-5 saral Hindi vaakyon mein samjhao. Koi nayi matra mat batao.")
        return _call([{"text": p}])
    except Exception:
        return fb

# ---------- Feature 12: Poochho Sinchai ----------
def chat(question, ctx):
    system = ("Tum Sinchai ho. Tumhara poora gyaan sirf neeche diye data se hai:\n"
              f"{json.dumps(ctx, ensure_ascii=False)}\n"
              "Niyam: 1) Sirf is data aur faisle ke aadhar par saral Hindi/Hinglish mein jawab do. "
              "2) Keetnashak, dawai ya bimari ke sawal par bolo 'KVK se confirm karein'. "
              "3) Data mein jawab na ho to bolo 'Mujhe pata nahi'. 4) Faisla khud mat badlo.")
    try:
        return _call([{"text": question}], system=system), "LLM"
    except Exception:
        q = question.lower()
        if any(w in q for w in ["keet", "dawai", "davai", "bimari", "rog", "spray", "pesticide", "disease"]):
            return "Is sawal ke liye KVK se confirm karein.", "Rules (fallback)"
        if any(w in q for w in ["paani", "pani", "sinchai", "irrigat", "bowai", "sow", "aaj", "kya karu", "kya karna"]):
            return f"Aaj ka faisla: {ctx['decision']['code']}. Wajah: {ctx['decision']['reason']}.", "Rules (fallback)"
        if any(w in q for w in ["nami", "moisture"]):
            return f"Mitti ki nami abhi {ctx['nami_pct']}% hai.", "Rules (fallback)"
        return "Mujhe pata nahi. (AI chat ke liye Gemini key daalo.)", "Rules (fallback)"