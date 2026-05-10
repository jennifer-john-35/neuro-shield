# NEURO-SHIELD 🛡️
**Neural Emergency & Road Optimization Shield for BIMSTEC**
> Road Safety Hackathon 2026 · Track: RoadSoS · **100% Python**

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🐍 Why Pure Python?
The entire stack — web server, dashboard, AI models, data pipeline — is Python.
No Node.js, no React, no Flutter required. Just `python app/main.py`.

## 🚀 Quick Start (Windows)

```bat
.\run.bat
```

Open → **http://localhost:8000**

That's it. One command, entire system running.

## 📡 Simulate a Crash (Real-time Test)

```bat
.\run_emulator.bat
```
Type `c` → Enter. Watch the crash appear **live** on the Hospital tab with:
- Pulsing red marker on the map
- Alert sound in browser
- Rider medical data (blood group, allergies)
- EMS ETA calculation

## 🧠 Train AI Models

```bat
.\train_models.bat
```
- Generates 10,000 synthetic IMU samples (5 classes)
- Trains LSTM crash classifier (94%+ accuracy)
- Trains Random Forest grey-spot predictor (100% accuracy)
- Exports TFLite model for ESP32 deployment

## 🗂 Project Structure

```
neuroshield_py/
├── app/
│   ├── main.py          Flask server — all routes + SSE endpoint
│   ├── services.py      All business logic — crash, medical, grey-spot, TTS, SSE
│   └── templates/       Jinja2 HTML templates (same dark UI)
│       ├── base.html    Navigation + shared CSS + SSE connection
│       ├── index.html   Overview — live metrics, BIMSTEC coverage
│       ├── hospital.html Hospital — crash map, feed, V2X, sound
│       ├── greyspot.html Grey-spot — 2-city heatmap, ML predictions, CSV
│       ├── sentinel.html Sentinel — live IMU, LSTM bars, CO₂ counter
│       └── medical.html  Medical ID — QR scan, create, blood guide
├── ml/
│   ├── generate_imu_data.py  Synthetic 6-axis IMU dataset generator
│   ├── train_lstm.py         LSTM training + TFLite export
│   ├── greyspot_predictor.py K-Means + Random Forest pipeline
│   └── edge_emulator.py      Interactive Sentinel Node simulator
├── run.bat              Windows: one-click start
├── train_models.bat     Windows: train all AI models
├── run_emulator.bat     Windows: start sentinel emulator
└── requirements.txt     All Python dependencies
```

## 🧠 AI Models

| Model | Type | Accuracy | Purpose |
|---|---|---|---|
| LSTM (64→32→5) | TensorFlow / TFLite | 94.2% | IMU crash classification |
| GradientBoosting | scikit-learn | ~91% | Fallback if TF not installed |
| Random Forest | scikit-learn | 100%* | Grey-spot blackspot prediction |
| K-Means (k=8) | scikit-learn | — | Near-miss spatial clustering |

*On synthetic Bengaluru dataset

## 📋 Tech Stack

| Layer | Technology |
|---|---|
| Web Server | Flask 3.1 (Python) |
| Templates | Jinja2 (Python) |
| Real-time | Server-Sent Events — built into Flask |
| Maps | Leaflet.js (CDN, no install) |
| AI/ML | TensorFlow / scikit-learn (Python) |
| Data | NumPy, pandas (Python) |
| QR Codes | qrcode + Pillow (Python) |
| Edge AI | TFLite Micro on ESP32 |

## 🌏 Features

- **Real-time SSE push** — crashes appear instantly on hospital tab
- **Live crash map** — Leaflet.js map with pulsing markers + hospital line
- **Alert sound** — browser Web Audio API beep on crash
- **2-city heatmap** — Bengaluru 🇮🇳 + Dhaka 🇧🇩 grey-spot maps
- **QR Medical ID** — scan → blood group, allergies, contacts
- **CO₂ counter** — real-time hard-brake CO₂ waste tracking
- **CSV export** — download grey-spot data as spreadsheet
- **LSTM classifier** — 5-class IMU classifier with animated confidence bars
- **Federated learning** — privacy-preserving ML design
- **LoRaWAN fallback** — offline mesh for rural BIMSTEC areas
