"""
NEURO-SHIELD — Synthetic IMU Training Data Generator
5 classes: NORMAL, HARD_BRAKE, POTHOLE, SWERVE, CRASH
Produces X_imu.npy (10000, 50, 6) and y_imu.npy (10000,)
"""
import numpy as np, os

CLASSES = ["NORMAL","HARD_BRAKE","POTHOLE","SWERVE","CRASH"]
WINDOW  = 50    # 50 timesteps @ 100Hz = 0.5s
SAMPLES = 2000  # per class
np.random.seed(42)

def _normal():
    return np.stack([
        np.random.normal(0,0.5,WINDOW),   # ax
        np.random.normal(0,0.5,WINDOW),   # ay
        np.random.normal(9.8,0.15,WINDOW),# az
        np.random.normal(0,3,WINDOW),     # gx
        np.random.normal(0,3,WINDOW),     # gy
        np.random.normal(0,2,WINDOW),     # gz
    ], axis=-1)

def _hard_brake():
    t = np.linspace(0,1,WINDOW)
    return np.stack([
        -12*np.exp(-3*t)+np.random.normal(0,0.8,WINDOW),
        np.random.normal(-2,1,WINDOW),
        np.random.normal(9.8,0.3,WINDOW),
        np.random.normal(0,10,WINDOW),
        np.random.normal(0,20,WINDOW),
        np.random.normal(-8,5,WINDOW),
    ], axis=-1)

def _pothole():
    az = np.random.normal(9.8,0.2,WINDOW)
    az[WINDOW//2-3:WINDOW//2+3] = np.random.normal(2,0.5,6)
    return np.stack([
        np.random.normal(0,0.5,WINDOW),
        np.random.normal(0,0.5,WINDOW),
        az,
        np.random.normal(0,12,WINDOW),
        np.random.normal(0,8,WINDOW),
        np.random.normal(0,6,WINDOW),
    ], axis=-1)

def _swerve():
    t = np.linspace(0,2*np.pi,WINDOW)
    return np.stack([
        np.random.normal(0,0.5,WINDOW),
        8*np.sin(t)+np.random.normal(0,0.5,WINDOW),
        np.random.normal(9.8,0.2,WINDOW),
        np.random.normal(0,5,WINDOW),
        np.random.normal(0,5,WINDOW),
        40*np.sin(t)+np.random.normal(0,2,WINDOW),
    ], axis=-1)

def _crash():
    t = np.linspace(0,1,WINDOW)
    return np.stack([
        np.random.normal(-22,4,WINDOW)*np.exp(-2*t),
        np.random.normal(18,4,WINDOW)*np.exp(-2*t),
        np.random.normal(-3,2,WINDOW),
        np.random.normal(120,30,WINDOW)*np.exp(-3*t),
        np.random.normal(80,25,WINDOW)*np.exp(-3*t),
        np.random.normal(60,20,WINDOW)*np.exp(-3*t),
    ], axis=-1)

GENERATORS = [_normal,_hard_brake,_pothole,_swerve,_crash]
X, y = [], []
for label, gen in enumerate(GENERATORS):
    for _ in range(SAMPLES):
        X.append(gen()); y.append(label)

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)
idx = np.random.permutation(len(X))
X, y = X[idx], y[idx]

os.makedirs("data", exist_ok=True)
np.save("data/X_imu.npy", X)
np.save("data/y_imu.npy", y)
print(f"Generated {len(X)} samples — shape {X.shape}")
print(f"Class distribution: { {c:(y==i).sum() for i,c in enumerate(CLASSES)} }")
