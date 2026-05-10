"""
NEURO-SHIELD — All business logic in one Python file.
"""
import uuid, math, random, io, json, queue, threading
from datetime import datetime

_crash_events = []
_medical_db = {
    "QR-NS-2847": {
        "rider_id":"demo-001","name":"Rohan Mehta","blood_group":"B+",
        "allergies":["Penicillin","Aspirin"],"conditions":["Mild asthma"],
        "emergency_contact_name":"Priya Mehta",
        "emergency_contact_phone":"+91 98765 43210",
        "nearest_hospital":"Manipal Hospital",
    }
}
_near_misses = []
_subs = []; _subs_lock = threading.Lock()

HOSPITALS = [
    {"name":"Manipal Hospital","lat":12.9399,"lon":77.6177},
    {"name":"Fortis Hospital", "lat":12.9716,"lon":77.5946},
    {"name":"Apollo Hospital", "lat":12.8456,"lon":77.6603},
    {"name":"Narayana Health", "lat":12.9010,"lon":77.6410},
]

GREY_SPOTS = {
    "bengaluru": [
        {"id":"gs-001","name":"Silk Board Junction",    "lat":12.9182,"lon":77.6271,"near":47, "risk":0.82,"type":"grey", "pred":True, "conf":0.87},
        {"id":"gs-002","name":"Electronic City Flyover","lat":12.8474,"lon":77.6632,"near":31, "risk":0.68,"type":"grey", "pred":False,"conf":0.62},
        {"id":"gs-003","name":"Outer Ring Road km 24",  "lat":12.9716,"lon":77.5946,"near":89, "risk":0.95,"type":"black","pred":True, "conf":0.97},
        {"id":"gs-004","name":"Marathahalli Bridge",    "lat":12.9591,"lon":77.6974,"near":38, "risk":0.74,"type":"grey", "pred":True, "conf":0.78},
        {"id":"gs-005","name":"Hebbal Flyover",         "lat":13.0358,"lon":77.5970,"near":29, "risk":0.61,"type":"grey", "pred":False,"conf":0.55},
        {"id":"gs-006","name":"Bannerghatta Road km 8", "lat":12.8956,"lon":77.5967,"near":112,"risk":0.97,"type":"black","pred":True, "conf":0.99},
        {"id":"gs-007","name":"HSR 27th Main",          "lat":12.9082,"lon":77.6476,"near":14, "risk":0.41,"type":"blue", "pred":False,"conf":0.31},
    ],
    "dhaka": [
        {"id":"dh-001","name":"Mirpur Road km 5",  "lat":23.8041,"lon":90.3683,"near":38,"risk":0.71,"type":"grey", "pred":True, "conf":0.74},
        {"id":"dh-002","name":"Gulshan Circle 2",  "lat":23.7805,"lon":90.4144,"near":22,"risk":0.54,"type":"grey", "pred":False,"conf":0.51},
        {"id":"dh-003","name":"Mohakhali Flyover", "lat":23.7765,"lon":90.4003,"near":61,"risk":0.88,"type":"black","pred":True, "conf":0.91},
        {"id":"dh-004","name":"Farmgate Junction", "lat":23.7564,"lon":90.3861,"near":17,"risk":0.43,"type":"blue", "pred":False,"conf":0.38},
    ],
}

RIDERS = [
    {"name":"Rohan Mehta",    "blood":"B+",  "allergy":"Penicillin",  "medical":"QR-NS-2847"},
    {"name":"Priya Sharma",   "blood":"O+",  "allergy":"None",        "medical":"QR-NS-1923"},
    {"name":"Arjun Nair",     "blood":"A+",  "allergy":"Aspirin",     "medical":"QR-NS-3841"},
    {"name":"Divya Krishnan", "blood":"AB-", "allergy":"Sulfa drugs", "medical":"QR-NS-5512"},
    {"name":"Karthik Raja",   "blood":"B-",  "allergy":"None",        "medical":"QR-NS-7734"},
]

LOCATIONS = [
    "Koramangala · 12.9351°N 77.6245°E",
    "Silk Board · 12.9182°N 77.6271°E",
    "Marathahalli · 12.9591°N 77.6974°E",
    "Hebbal · 13.0358°N 77.5970°E",
    "Bannerghatta · 12.8956°N 77.5967°E",
]

TTS_TEMPLATES = {
    "hi":"ध्यान दें! एक सवार {dist} आगे गिरा है। कृपया धीमे हों।",
    "bn":"মনোযোগ! একজন রাইডার {dist} সামনে পড়ে গেছে।",
    "en":"Attention! A rider has fallen {dist} ahead. Please slow down.",
    "si":"අවධානය! රයිඩර් කෙනෙකු {dist} ඉදිරිපස වැටී ඇත.",
    "ne":"ध्यान दिनुहोस्! एक राइडर {dist} अगाडि ढले।",
}

REGION_LANGS = [
    {"lat":(6.0,37.0),"lon":(68.0,97.0),"lang":"hi"},
    {"lat":(20.0,26.7),"lon":(88.0,92.7),"lang":"bn"},
    {"lat":(5.9,9.9),"lon":(79.6,81.9),"lang":"si"},
    {"lat":(26.3,30.5),"lon":(80.0,88.2),"lang":"ne"},
]

def _haversine(lat1,lon1,lat2,lon2):
    R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

def process_crash(data=None):
    if data is None: data={}
    eid="NS-"+str(len(_crash_events)+1).zfill(4)
    lat=data.get("lat",12.9351+random.uniform(-0.05,0.05))
    lon=data.get("lon",77.6245+random.uniform(-0.05,0.05))
    hosp=min(HOSPITALS,key=lambda h:_haversine(lat,lon,h["lat"],h["lon"]))
    dist=_haversine(lat,lon,hosp["lat"],hosp["lon"])
    eta=round((dist/40)*60*0.8,1)
    rider=random.choice(RIDERS)
    rec={
        "event_id":eid,"event_type":data.get("event_type","CRASH"),
        "severity":data.get("severity","HIGH"),
        "lat":lat,"lon":lon,"location_str":random.choice(LOCATIONS),
        "hospital":hosp["name"],"ems_eta":eta,
        "rider_name":rider["name"],"blood_group":rider["blood"],
        "allergy":rider["allergy"],"medical_id":rider["medical"],
        "timestamp":datetime.utcnow().isoformat(),
    }
    _crash_events.insert(0,rec)
    push_sse("crash",rec)
    return rec

def get_recent_crashes(limit=20): return _crash_events[:limit]
def get_medical(mid): return _medical_db.get(mid)

def create_medical(data):
    mid=f"QR-NS-{str(uuid.uuid4())[:4].upper()}"
    _medical_db[mid]=data; return mid

def generate_qr(mid):
    try:
        import qrcode
        url=f"http://localhost:8000/medical/qr/{mid}"
        qr=qrcode.QRCode(version=1,box_size=8,border=2)
        qr.add_data(url); qr.make(fit=True)
        img=qr.make_image(fill_color="black",back_color="white")
        buf=io.BytesIO(); img.save(buf,format="PNG"); buf.seek(0); return buf
    except: return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd5J\x00\x00\x00\x00IEND\xaeB`\x82')

def get_spots(city="bengaluru"): return GREY_SPOTS.get(city,[])

def add_near_miss(city="bengaluru"):
    spots=GREY_SPOTS.get(city,[])
    if not spots: return
    idx=random.randint(0,min(3,len(spots)-1))
    spots[idx]["near"]+=1
    spots[idx]["risk"]=min(1.0,spots[idx]["risk"]+0.005)
    if spots[idx]["near"]>80: spots[idx]["type"]="black"
    # Also log to crash_events so overview can count near-misses
    rec={"event_id":"NM-"+str(len(_near_misses)+1).zfill(4),
         "event_type":"NEAR_MISS","severity":"LOW",
         "lat":spots[idx]["lat"]+random.uniform(-0.002,0.002),
         "lon":spots[idx]["lon"]+random.uniform(-0.002,0.002),
         "location_str":spots[idx]["name"],"hospital":"","ems_eta":0,
         "rider_name":"","blood_group":"","allergy":"","medical_id":"",
         "timestamp":datetime.utcnow().isoformat()}
    _crash_events.insert(0,rec)
    _near_misses.append({"city":city,"timestamp":datetime.utcnow().isoformat()})
    push_sse("near_miss",{"city":city,"spot":spots[idx]["name"]})

def get_co2(city="bengaluru"):
    b=random.randint(300,500); t=b*0.043
    return {"city":city,"hard_brake_events_today":b,"co2_wasted_today_kg":round(t,2),"co2_annual_projection_tons":round(t*365/1000,2)}

def detect_lang(lat,lon):
    for r in REGION_LANGS:
        if r["lat"][0]<=lat<=r["lat"][1] and r["lon"][0]<=lon<=r["lon"][1]: return r["lang"]
    return "en"

def tts_alert(lat,lon):
    lang=detect_lang(lat,lon)
    msg=TTS_TEMPLATES.get(lang,TTS_TEMPLATES["en"]).format(dist="50 metres")
    return {"language":lang,"message":msg}

def push_sse(event_type,data):
    msg=f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _subs_lock:
        dead=[]
        for q in _subs:
            try: q.put_nowait(msg)
            except: dead.append(q)
        for q in dead: _subs.remove(q)

def sse_subscribe():
    q=queue.Queue(maxsize=50)
    with _subs_lock: _subs.append(q)
    return q

def sse_unsubscribe(q):
    with _subs_lock:
        if q in _subs: _subs.remove(q)
