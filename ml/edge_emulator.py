"""
NEURO-SHIELD — Sentinel Node Edge Emulator (Pure Python)
Simulates the ESP32 device running the LSTM crash classifier.
Reads synthetic IMU → classifies → POSTs crash events to Flask API.

Usage:
    python edge_emulator.py --mode interactive
    python edge_emulator.py --mode crash
    python edge_emulator.py --mode ride
"""
import argparse, math, time, random, json
import numpy as np

try:
    import requests; HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

API = "http://localhost:8000"
CLASSES = ["NORMAL","HARD_BRAKE","POTHOLE","SWERVE","CRASH"]
LOCATION = {"lat":12.9351, "lon":77.6245}

# ── Rule-based edge classifier (replace body with TFLite in production) ───────
def classify_imu(window: np.ndarray):
    """
    window shape: (50, 6) — [ax,ay,az,gx,gy,gz]
    Returns: (class_index, confidence)
    """
    ax,ay,az = window[:,0], window[:,1], window[:,2]
    gx,gy,gz = window[:,3], window[:,4], window[:,5]
    max_g   = np.sqrt(ax**2+ay**2+az**2).max()
    max_rot = np.sqrt(gx**2+gy**2+gz**2).max()
    az_range= az.max()-az.min()

    if max_g>18 and max_rot>80:   return 4, 0.96   # CRASH
    if max_g>10 and az_range<5:   return 1, 0.90   # HARD_BRAKE
    if az_range>8 and max_rot<30: return 2, 0.83   # POTHOLE
    if max_rot>40 and max_g<12:   return 3, 0.80   # SWERVE
    return 0, 0.97                                  # NORMAL

# ── Synthetic IMU generators per mode ────────────────────────────────────────
def gen_window(mode: str) -> np.ndarray:
    t = np.linspace(0,1,50)
    if mode=="crash":
        return np.stack([
            np.random.normal(-22,4,50)*np.exp(-2*t),
            np.random.normal(18,4,50)*np.exp(-2*t),
            np.random.normal(-3,2,50),
            np.random.normal(120,30,50)*np.exp(-3*t),
            np.random.normal(80,25,50)*np.exp(-3*t),
            np.random.normal(60,20,50)*np.exp(-3*t),
        ], axis=-1)
    if mode=="brake":
        return np.stack([
            -12*np.exp(-3*t)+np.random.normal(0,0.8,50),
            np.random.normal(-2,1,50),
            np.random.normal(9.8,0.3,50),
            np.random.normal(0,10,50),
            np.random.normal(0,20,50),
            np.random.normal(-8,5,50),
        ], axis=-1)
    if mode=="pothole":
        az=np.random.normal(9.8,0.2,50); az[22:28]=np.random.normal(2,0.5,6)
        return np.stack([np.random.normal(0,.5,50),np.random.normal(0,.5,50),az,
                         np.random.normal(0,12,50),np.random.normal(0,8,50),np.random.normal(0,6,50)],axis=-1)
    if mode=="swerve":
        ts=np.linspace(0,2*math.pi,50)
        return np.stack([np.random.normal(0,.5,50),8*np.sin(ts)+np.random.normal(0,.5,50),
                         np.random.normal(9.8,.2,50),np.random.normal(0,5,50),
                         np.random.normal(0,5,50),40*np.sin(ts)+np.random.normal(0,2,50)],axis=-1)
    # normal
    return np.stack([np.random.normal(0,.5,50),np.random.normal(0,.5,50),
                     np.random.normal(9.8,.15,50),np.random.normal(0,3,50),
                     np.random.normal(0,3,50),np.random.normal(0,2,50)],axis=-1)

# ── Print + POST ──────────────────────────────────────────────────────────────
COLORS = {0:"\033[92m",1:"\033[93m",2:"\033[94m",3:"\033[96m",4:"\033[91m"}
RESET  = "\033[0m"

def print_imu(w, cls, conf):
    row = w[-1]
    bar = "█" * int(conf*20)
    c   = COLORS.get(cls,"")
    print(f"\r  ax={row[0]:+6.1f} ay={row[1]:+6.1f} az={row[2]:+5.1f} | "
          f"gx={row[3]:+7.1f} gy={row[4]:+7.1f} gz={row[5]:+7.1f} | "
          f"  {c}{CLASSES[cls]:<12}{RESET} {bar} {conf*100:.1f}%", end="", flush=True)

def post_crash(cls, w):
    if not HAS_REQUESTS:
        print(f"\n  [WOULD POST {CLASSES[cls]} to API — install requests]"); return
    payload = {
        "event_type": CLASSES[cls],
        "severity":   "HIGH" if cls==4 else "MEDIUM",
        "lat": LOCATION["lat"] + random.uniform(-0.05,0.05),
        "lon": LOCATION["lon"] + random.uniform(-0.05,0.05),
        "medical_id": "QR-NS-2847",
    }
    try:
        r = requests.post(f"{API}/api/crash", json=payload, timeout=3)
        print(f"\n  🚨 API response: {r.json()}")
    except Exception as e:
        print(f"\n  API error: {e}")

def run(mode: str, loops: int=1):
    print(f"\n  NEURO-SHIELD Sentinel Emulator  |  mode={mode}\n")
    for _ in range(loops):
        w = gen_window(mode)
        cls, conf = classify_imu(w)
        print_imu(w, cls, conf)
        if cls != 0:
            print()
            post_crash(cls, w)
        time.sleep(0.1)
    print()

def interactive():
    print("\n  NEURO-SHIELD Sentinel — Interactive Mode")
    print("  Commands:  n=normal  b=brake  p=pothole  s=swerve  c=crash  q=quit\n")
    while True:
        cmd = input("  > ").strip().lower()
        if cmd == "q": break
        modes = {"n":"normal","b":"brake","p":"pothole","s":"swerve","c":"crash"}
        if cmd in modes:
            run(modes[cmd], loops=1 if cmd=="c" else 5)
        else:
            print("  Unknown command")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEURO-SHIELD Sentinel Node Emulator")
    parser.add_argument("--mode", choices=["crash","brake","pothole","swerve","ride","interactive"], default="interactive")
    args = parser.parse_args()
    if   args.mode=="interactive": interactive()
    elif args.mode=="ride":
        print("  Normal ride simulation — Ctrl+C to stop")
        while True: run("normal",loops=1)
    else: run(args.mode, loops=10)
