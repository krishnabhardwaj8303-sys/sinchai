# Khaad ki matra (kg/ha). Har fasal ke saath source aur verified flag.
# LLM kabhi dose nahi nikalta, sirf yahan se lookup hota hai.
# Soil level cutoffs: ICAR Soil Health Card (HARIT DHARA 4(1), 2021): N 280/560, P 10/25, K 120/280 kg/ha.
RDF = {
    "wheat":   {"N": 120, "P": 60, "K": 40, "verified": True,
                "source": "Wheat general RDF 120:60:40 (MPKV/ICAR package)"},
    "chana":   {"N": 20, "P": 50, "K": 20, "verified": True,
                "source": "Chickpea RDF 20:50:20 (IGKV Raipur, Indian J. Agronomy 2019)"},
    "rice_dsr": {"N": 100, "P": 60, "K": 40, "verified": False,
                 "source": "UNVERIFIED demo value. IGKV/KVK se confirm karo"},
    "soybean": {"N": 20, "P": 60, "K": 40, "verified": False,
                "source": "UNVERIFIED demo value. IGKV/KVK se confirm karo"},
}

def level(nutrient, v):
    cuts = {"N": (280, 560), "P": (10, 25), "K": (120, 280)}  # ICAR SHC: <lo low, lo-hi medium, >hi high
    lo, hi = cuts[nutrient]
    return "low" if v < lo else ("med" if v <= hi else "high")

def recommend(card, crop):
    r = RDF[crop]
    res = {"levels": {}, "dose_kg_ha": {n: r[n] for n in ("N", "P", "K")},
           "verified": r["verified"], "source": r["source"], "notes": []}
    for n in ("N", "P", "K"):
        res["levels"][n] = level(n, float(card[n]))
    ph = float(card["pH"])
    if ph < 6.0:
        res["notes"].append("Mitti khatti hai: chuna (lime) ke baare mein KVK se poochhein.")
    elif ph > 8.5:
        res["notes"].append("Mitti kshariya hai: gypsum ke baare mein KVK se poochhein.")
    oc = card.get("OC")
    if oc is not None and float(oc) < 0.5:
        res["notes"].append("Jaivik kaarbon kam hai: gobar/compost khaad daalein.")
    if "low" in res["levels"].values() or "high" in res["levels"].values():
        res["notes"].append("Ye general matra hai. Mitti ke star ke hisaab se adjust karne ke liye KVK se poochhein.")
    return res