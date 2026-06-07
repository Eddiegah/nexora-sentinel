
```markdown
# 🛡️ Nexora Sentinel

> AI-powered disease outbreak prediction and health intelligence platform for Africa.



![Python](https://img.shields.io/badge/Python-3.14-blue)




![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)




![React](https://img.shields.io/badge/React-18-61dafb)




![XGBoost](https://img.shields.io/badge/XGBoost-96.36%25_Accuracy-orange)




![License](https://img.shields.io/badge/License-MIT-yellow)



---

## 📌 Overview

Nexora Sentinel uses machine learning to predict malaria outbreak risk across
African nations — giving health officials early warning before outbreaks escalate.

Every year, hundreds of thousands of people die from malaria — not because 
we lack medicine, but because we lack **warning**. Nexora Sentinel addresses 
this by turning historical disease data and health indicators into actionable 
risk predictions.

**Live Demo:** Run locally following the setup guide below.

---

## 🖥️ Dashboard Preview

### Prediction Panel
- Select any African country and year
- Get instant AI-powered outbreak risk classification
- Color-coded results: 🟢 Low | 🟡 Medium | 🔴 High

### Regional Overview
- Load risk predictions for 15 major African nations simultaneously
- Risk distribution summary (High / Medium / Low counts)
- Confidence scores for every prediction

---

## 🏗️ Architecture

```

Data Sources (WHO/Kaggle)
        ↓
Data Pipeline (Python + Pandas)
        ↓
PostgreSQL / CSV Storage
        ↓
XGBoost ML Model (96.36% accuracy)
        ↓
FastAPI Backend (/predict, /countries)
        ↓
React Frontend Dashboard
```

---

## 🧠 Machine Learning

| Model | Accuracy | Notes |
|---|---|---|
| Logistic Regression | 70.91% | Baseline |
| **XGBoost** | **96.36%** | **Production model** |

**Training Data:**
- 550 records across 54 African countries (2007–2017)
- Features: population metrics, water access, sanitation,
  urban/rural growth rates
- Target: Malaria outbreak risk (Low / Medium / High)

**Evaluation Metrics:**
- Accuracy: 96.36%
- Macro F1: 0.96
- Precision: 0.96
- Recall: 0.96

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| ML | Python, XGBoost, scikit-learn | Model training and inference |
| Explainability | SHAP | Feature importance (Stage 2) |
| Experiment Tracking | MLflow | Model versioning (Stage 2) |
| Backend | FastAPI, Uvicorn | REST API |
| Data | Pandas, NumPy | Data processing |
| Frontend | React | Dashboard UI |
| Version Control | Git, GitHub | Source control |
| Containerization | Docker | Deployment (Stage 2) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Eddiegah/nexora-sentinel.git
cd nexora-sentinel
```

### 2. Set Up Python Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux
pip install -r ml/requirements.txt
pip install fastapi uvicorn
```

### 3. Train the Model
```bash
python ml/data/clean.py
python ml/models/train.py
```

### 4. Start the API
```bash
uvicorn backend.main:app --reload
```
API runs at: http://127.0.0.1:8000
API docs at: http://127.0.0.1:8000/docs

### 5. Start the Dashboard
```bash
cd frontend
npm install
npm start
```
Dashboard runs at: http://localhost:3000

---

## 📡 API Reference

### GET /
Health check endpoint.
```json
{
  "message": "Nexora Sentinel API is running",
  "status": "healthy"
}
```

### GET /countries
Returns all 54 supported African countries.

### POST /predict
Predicts malaria outbreak risk for a given country and year.

**Request:**
```json
{
  "country": "Ghana",
  "year": 2024,
  "urban_population_pct": 58.0,
  "rural_population_pct": 42.0,
  "urban_growth": 3.2,
  "rural_growth": 1.8,
  "water_access_pct": 61.0
}
```

**Response:**
```json
{
  "country": "Ghana",
  "year": 2024,
  "risk_level": "Low",
  "confidence": 56.4,
  "color": "#22c55e",
  "message": "Low malaria outbreak risk predicted for Ghana in 2024"
}
```

---

## 📁 Project Structure

```
nexora-sentinel/
├── data/
│   ├── raw/                    # Original datasets
│   └── processed/              # Cleaned, ML-ready data
├── ml/
│   ├── data/
│   │   ├── explore.py          # EDA script
│   │   └── clean.py            # Data cleaning pipeline
│   ├── models/
│   │   └── train.py            # Model training (LR + XGBoost)
│   └── artifacts/              # Saved model files
├── backend/
│   └── main.py                 # FastAPI application
├── frontend/
│   └── src/
│       └── App.js              # React dashboard
└── docs/                       # Documentation
```

---

## 🗺️ Roadmap

### ✅ Stage 1 — MVP (Complete)
- [x] Data acquisition and cleaning pipeline
- [x] XGBoost model with 96.36% accuracy
- [x] FastAPI REST API with prediction endpoint
- [x] React dashboard with live predictions
- [x] Regional risk overview for 15 countries

### 🔄 Stage 2 — Enhanced Intelligence
- [ ] SHAP explainability (why did the model predict this?)
- [ ] MLflow experiment tracking
- [ ] PostgreSQL database integration
- [ ] Additional diseases (dengue, cholera)
- [ ] Monthly granularity predictions

### 🔮 Stage 3 — Production Scale
- [ ] Docker containerization
- [ ] AWS deployment (EC2 + RDS + S3)
- [ ] GitHub Actions CI/CD pipeline
- [ ] LLM-powered outbreak reports
- [ ] Real-time data ingestion

---

## 👤 Author

**Edmund Eric Gah**  
AI/ML Engineer & Full-Stack Developer

Building AI systems that solve real-world health challenges in Africa.

- GitHub: [@Eddiegah](https://github.com/Eddiegah)
- LinkedIn: [Your LinkedIn URL]

---

## 📄 License

MIT License — feel free to use this project for learning and portfolio purposes.

---

*Built as a portfolio project demonstrating end-to-end AI/ML engineering,
data science, backend development, and frontend engineering.*
```

Save with `Ctrl+S`.

---

# THEN COMMIT IT

```bash
git add README.md
git commit -m "Add professional README with architecture and setup guide"
git push origin main
```
