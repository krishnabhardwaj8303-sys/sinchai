from crop_table import CROPS

def decide(moisture, rain3, crop="rice_dsr", stage="sowing", sensor_ok=True, delay_days=0):
    """Features 1 + 2. Faisla sirf rules se hota hai, LLM se nahi."""
    c = CROPS[crop]
    st = c["stages"][stage]
    base = {"crop": crop, "crop_hi": c["name_hi"], "alt": c["alt"],
            "alt_hi": CROPS[c["alt"]]["name_hi"], "stage": stage,
            "critical": st["critical"], "kc": st["kc"], "service_flag": False}

    if not sensor_ok:
        base.update(code="CHECK_SENSOR", service_flag=True,
                    reason="Sensor atka ya kharab hai. Sensor check karein, aaj ke liye forecast par chalein")
        return base

    if stage == "sowing":
        if moisture >= c["sow_min"]:
            if rain3 >= 50:
                base.update(code="WAIT", reason="Bahut tez baarish aane wali hai, beej bah sakta hai")
            else:
                base.update(code="SOW", reason="Mitti mein nami theek hai")
        elif rain3 >= 5:
            base.update(code="WAIT", reason="Nami kam hai par baarish aane wali hai")
        elif delay_days >= 14:
            base.update(code="SWITCH", reason=f"Bowai mein {delay_days} din ki der, nami kam, baarish nahi. Kam paani wali fasal dekhein")
        else:
            base.update(code="WAIT", reason="Mitti mein nami kam, baarish kam")
        return base

    if rain3 >= st["rain_skip"]:
        base.update(code="WAIT", reason="Jald baarish ki sambhavna, sinchai rokein")
    elif moisture < st["low"]:
        tag = "Critical stage, " if st["critical"] else ""
        base.update(code="IRRIGATE", reason=f"{tag}nami {moisture:.0f}% hai, {st['low']}% se kam")
    else:
        base.update(code="WAIT", reason="Nami theek hai, abhi sinchai ki zaroorat nahi")
    return base

def alerts(tmin, tmax, rain3):
    """Feature 4: paala / garmi / baarish."""
    out = []
    if tmin <= 4:
        out.append(("PAALA", f"Paale ka khatra: minimum taapman {tmin:.1f} C"))
    if tmax >= 40:
        out.append(("GARMI", f"Loo/garmi ka khatra: maximum taapman {tmax:.1f} C"))
    if rain3 >= 50:
        out.append(("BAARISH", f"Bhaari baarish: 3 din mein {rain3:.0f} mm"))
    return out