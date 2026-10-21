import numpy as np
from sklearn.ensemble import IsolationForest

def simulate_history(end, fault="none", n=30, seed=1):
    """Nakli sensor history: nami dheere dheere ghat ke 'end' par aati hai."""
    rng = np.random.default_rng(seed)
    h = end + np.linspace(8, 0, n) + rng.normal(0, 0.3, n)
    h = np.clip(h, 0, 100)
    if fault == "flatline":
        h[-15:] = h[-15]
    elif fault == "jump":
        h[-1] = h[-2] + (40 if h[-2] < 50 else -40)
    elif fault == "out_of_range":
        h[-1] = -5
    return [round(float(x), 1) for x in h]

def _feat(w):
    w = np.asarray(w, float)
    return [w[-1] - w[-2], float(np.std(w)), float(w[-1] - w[0])]

def _train():
    # Training data NAKLI hai: normal sukhne wali curves, har level par (0-100%). Level ko feature nahi rakha.
    rng = np.random.default_rng(0)
    X = []
    for _ in range(400):
        start = rng.uniform(10, 100); slope = rng.uniform(0.0, 1.6)
        s = start - slope * np.arange(40) + rng.normal(0, rng.uniform(0.1, 0.5), 40)
        s = np.clip(s, 0, 100)
        for i in range(5, 40):
            X.append(_feat(s[i-5:i+1]))
    return IsolationForest(n_estimators=100, contamination=0.005, random_state=0).fit(X)

_MODEL = None

def check(hist, node_age_s=0):
    """Layer 1: rules. Layer 2: Isolation Forest. Return status + reason."""
    global _MODEL
    if node_age_s > 900:
        return {"status": "FAULT", "layer": "rules", "reason": "Node offline, data nahi aa raha"}
    h = [float(x) for x in hist]
    if len(h) < 6:
        return {"status": "OK", "layer": "-", "reason": "Data kam hai, check abhi nahi"}
    last = h[-1]
    if last < 0 or last > 100:
        return {"status": "FAULT", "layer": "rules", "reason": "Reading 0-100% ke bahar hai"}
    if len(h) >= 12 and max(h[-12:]) - min(h[-12:]) < 0.05:
        return {"status": "FAULT", "layer": "rules", "reason": "Reading atki hui hai (flat-line)"}
    if abs(last - h[-2]) > 30:
        return {"status": "FAULT", "layer": "rules", "reason": "Achanak bada jump"}
    if _MODEL is None:
        _MODEL = _train()
    if _MODEL.predict([_feat(h[-6:])])[0] == -1:
        return {"status": "FAULT", "layer": "ML", "reason": "Anomaly (Isolation Forest)"}
    return {"status": "OK", "layer": "-", "reason": "Sensor theek hai"}

def evaluate(trials=200):
    """Nakli faults par test: slide ke liye asli numbers."""
    rng = np.random.default_rng(42)
    res = {}
    for f in ["none", "flatline", "jump", "out_of_range", "drift_spike", "noise"]:
        hit = 0
        for i in range(trials):
            end = float(rng.uniform(5, 95))
            if f == "drift_spike":
                h = np.array(simulate_history(end, "none", seed=i), float); h[-1] += rng.choice([-1, 1]) * rng.uniform(12, 25)
                h = [round(float(x), 1) for x in h]
            elif f == "noise":
                h = np.array(simulate_history(end, "none", seed=i), float) + rng.normal(0, 6, 30)
                h = [round(float(x), 1) for x in h]
            else:
                h = simulate_history(end, f, seed=i)
            flagged = check(h)["status"] == "FAULT"
            hit += flagged
        res[f] = hit / trials
    return res