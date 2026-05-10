"""
NEURO-SHIELD v2.0 — Pure Python Flask Application
Single file server: API + Dashboard (HTML rendered by Jinja2)
Run: python app/main.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, Response, send_file
from app.services import (
    process_crash, get_recent_crashes, get_medical, create_medical, generate_qr,
    get_spots, add_near_miss, get_co2, tts_alert, sse_subscribe, sse_unsubscribe, push_sse
)

app = Flask(__name__, template_folder="templates", static_folder="static")

def _cors(r):
    r.headers["Access-Control-Allow-Origin"]  = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    r.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return r

@app.after_request
def cors(r): return _cors(r)

@app.route("/", defaults={"path":""}, methods=["OPTIONS"])
@app.route("/<path:path>", methods=["OPTIONS"])
def opt(**_): return _cors(jsonify({}))

# ── Dashboard pages ───────────────────────────────────────────────────────────
@app.get("/")
def index(): return render_template("index.html")

@app.get("/hospital")
def hospital(): return render_template("hospital.html", crashes=get_recent_crashes(10))

@app.get("/greyspot")
def greyspot(): return render_template("greyspot.html")

@app.get("/sentinel")
def sentinel(): return render_template("sentinel.html")

@app.get("/medical")
def medical(): return render_template("medical.html")

# ── SSE ───────────────────────────────────────────────────────────────────────
@app.get("/events")
def events():
    def stream():
        q = sse_subscribe()
        try:
            yield "event: connected\ndata: {\"status\":\"connected\"}\n\n"
            while True:
                try: yield q.get(timeout=25)
                except: yield ": heartbeat\n\n"
        finally: sse_unsubscribe(q)
    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

# ── API ───────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health(): return jsonify({"status":"ok","version":"2.0.0"})

@app.post("/api/crash")
def api_crash():
    return jsonify(process_crash(request.json or {}))

@app.get("/api/crashes")
def api_crashes():
    return jsonify(get_recent_crashes(int(request.args.get("limit",20))))

@app.post("/api/near-miss")
def api_near_miss():
    city = (request.json or {}).get("city","bengaluru")
    add_near_miss(city)
    return jsonify({"ok":True})

@app.get("/api/spots")
def api_spots():
    return jsonify(get_spots(request.args.get("city","bengaluru")))

@app.get("/api/co2")
def api_co2():
    return jsonify(get_co2(request.args.get("city","bengaluru")))

@app.get("/api/medical/<mid>")
def api_medical(mid):
    d = get_medical(mid)
    return jsonify(d) if d else (jsonify({"error":"Not found"}),404)

@app.get("/api/medical/<mid>/qr")
def api_qr(mid):
    return send_file(generate_qr(mid), mimetype="image/png")

@app.post("/api/medical/create")
def api_create_medical():
    data = request.json or {}
    mid = create_medical(data)
    return jsonify({"medical_id":mid})

@app.get("/api/tts")
def api_tts():
    lat = float(request.args.get("lat",12.93))
    lon = float(request.args.get("lon",77.62))
    return jsonify(tts_alert(lat,lon))

if __name__ == "__main__":
    print("\n  NEURO-SHIELD v2.0 — Pure Python")
    print("  Dashboard → http://localhost:8000")
    print("  API       → http://localhost:8000/api/health\n")
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)
