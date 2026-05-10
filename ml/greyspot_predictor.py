"""
NEURO-SHIELD — Grey-Spot AI Predictor
Pipeline:
  1. Load anonymised near-miss events
  2. K-Means clustering on (lat, lon) + near-miss density
  3. Random Forest: "Will grey-spot become blackspot in 6 months?"
  4. Export GeoJSON heatmap for Leaflet.js map

Run:
    python greyspot_predictor.py
"""
import numpy as np, json, os
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

np.random.seed(42)

# ── Seed data: Bengaluru known spots ─────────────────────────────────────────
# (lat, lon, near_miss_count, risk_score, became_blackspot)
RAW = [
    (12.9182,77.6271, 47,0.82,1),
    (12.8474,77.6632, 31,0.68,0),
    (12.9716,77.5946, 89,0.95,1),
    (12.9591,77.6974, 38,0.74,1),
    (13.0358,77.5970, 29,0.61,0),
    (12.8956,77.5967,112,0.97,1),
    (12.9082,77.6476, 14,0.41,0),
    (13.0200,77.6500, 55,0.79,1),
    (12.8800,77.5800, 18,0.38,0),
    (12.9300,77.6100, 63,0.85,1),
    (12.9900,77.5600, 22,0.52,0),
    (12.8600,77.6900, 70,0.88,1),
]

# Augment with 40 synthetic samples per seed point
rows = []
for lat,lon,count,risk,label in RAW:
    for _ in range(40):
        rows.append([
            lat  + np.random.normal(0,0.005),
            lon  + np.random.normal(0,0.005),
            count + np.random.randint(-5,6),
            risk  + np.random.normal(0,0.04),
            label,
        ])

data  = np.array(rows)
X_raw = data[:,:4]
y     = data[:,4].astype(int)

# ── Feature engineering ───────────────────────────────────────────────────────
scaler = StandardScaler()
X = scaler.fit_transform(X_raw)

# ── Step 1: K-Means clustering ────────────────────────────────────────────────
print("Running K-Means clustering (k=8)...")
kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X_raw[:,:2])
X_full = np.hstack([X, cluster_labels.reshape(-1,1)])

# ── Step 2: Random Forest classifier ─────────────────────────────────────────
print("Training Random Forest blackspot predictor...")
X_train,X_test,y_train,y_test = train_test_split(X_full, y, test_size=0.2, random_state=42, stratify=y)
rf = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=3,
                             random_state=42, class_weight="balanced")
rf.fit(X_train, y_train)

acc = accuracy_score(y_test, rf.predict(X_test))
print(f"\nGrey-Spot predictor accuracy: {acc*100:.1f}%")
print(classification_report(y_test, rf.predict(X_test), target_names=["stays grey","becomes black"]))

# ── Save models ───────────────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
joblib.dump(rf,     "models/greyspot_rf.joblib")
joblib.dump(kmeans, "models/greyspot_kmeans.joblib")
joblib.dump(scaler, "models/greyspot_scaler.joblib")
print("Saved: greyspot_rf.joblib · greyspot_kmeans.joblib · greyspot_scaler.joblib")

# ── Export GeoJSON heatmap ────────────────────────────────────────────────────
SPOT_NAMES = {
    (12.9182,77.6271):"Silk Board Junction",
    (12.8474,77.6632):"Electronic City Flyover",
    (12.9716,77.5946):"Outer Ring Road km 24",
    (12.9591,77.6974):"Marathahalli Bridge",
    (13.0358,77.5970):"Hebbal Flyover",
    (12.8956,77.5967):"Bannerghatta Road km 8",
    (12.9082,77.6476):"HSR 27th Main",
}

features = []
for lat,lon,count,risk,label in RAW:
    sample = scaler.transform([[lat,lon,count,risk]])
    cluster = int(kmeans.predict([[lat,lon]])[0])
    sample_full = np.hstack([sample,[[cluster]]])
    pred  = int(rf.predict(sample_full)[0])
    proba = float(rf.predict_proba(sample_full)[0][1])
    spot_type = "black" if count>80 else ("grey" if risk>0.55 else "blue")
    name = SPOT_NAMES.get((lat,lon), f"Zone {round(lat,2)}°N {round(lon,2)}°E")
    features.append({
        "type":"Feature",
        "geometry":{"type":"Point","coordinates":[lon,lat]},
        "properties":{
            "name":name, "near_miss_count":int(count), "risk_score":round(float(risk),3),
            "spot_type":spot_type, "predicted_blackspot":bool(pred),
            "confidence":round(proba,3), "cluster":cluster,
        }
    })

geojson = {"type":"FeatureCollection","features":features}
os.makedirs("data", exist_ok=True)
with open("data/bengaluru_heatmap.geojson","w") as f:
    json.dump(geojson, f, indent=2)
print(f"\nExported {len(features)} grey-spots → data/bengaluru_heatmap.geojson")
