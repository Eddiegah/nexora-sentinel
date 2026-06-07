🛡️ Nexora Sentinel

<div align="center">AI-Powered Disease Outbreak Prediction Platform for Africa

Predict outbreaks before they become emergencies.

"Every outbreak that kills thousands begins as a signal nobody acted on. Nexora Sentinel turns those signals into action."

<br>"Python" (https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
"FastAPI" (https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
"React" (https://img.shields.io/badge/React-Dashboard-61DAFB?style=for-the-badge&logo=react&logoColor=black)
"XGBoost" (https://img.shields.io/badge/XGBoost-96.36%25_Accuracy-FF6600?style=for-the-badge)
"Status" (https://img.shields.io/badge/Status-Live-22c55e?style=for-the-badge)

<br>Built with purpose. Trained on truth. Designed for Africa.

</div>---

🌍 Why Nexora Sentinel Exists

Every year, hundreds of thousands of lives are lost to preventable infectious disease outbreaks across Africa.

The challenge isn't always treatment.

The challenge is timing.

By the time outbreaks are officially recognized, communities are already affected, healthcare systems are under pressure, and response costs have multiplied.

Nexora Sentinel changes that.

Using machine learning and public health data, the platform predicts malaria outbreak risk across African nations, enabling earlier intervention and more informed decision-making.

---

⚡ Key Features

🤖 AI-Powered Prediction

Predicts malaria outbreak risk levels using an optimized XGBoost model.

🌍 Africa-Focused

Built specifically using African public health and demographic data.

📡 Real-Time API

Any application can request outbreak predictions through a REST API.

🖥️ Interactive Dashboard

Health officials and researchers can visualize predictions instantly.

📊 High Performance

Achieved 96.36% classification accuracy on unseen test data.

---

🎯 What the Platform Predicts

For any supported African country and year, Nexora Sentinel predicts:

- 🟢 Low Risk
- 🟡 Medium Risk
- 🔴 High Risk

Alongside:

- Confidence score
- Prediction explanation (coming soon)
- Regional comparison insights
- Historical outbreak context

---

🏗️ System Architecture

┌──────────────────────────────────────────────────────┐
│                    DATA SOURCES                       │
│                                                      │
│      WHO Global Health Observatory Dataset           │
│      Public African Malaria Datasets                 │
│                                                      │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│                 DATA PIPELINE                         │
│                                                      │
│ Ingestion → Cleaning → Validation → Features         │
│                                                      │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│                 MACHINE LEARNING                      │
│                                                      │
│        XGBoost Classifier (96.36% Accuracy)          │
│                                                      │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND                       │
│                                                      │
│   GET  /            → Health Check                   │
│   GET  /countries   → Available Countries            │
│   POST /predict     → AI Prediction                  │
│                                                      │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│                 REACT DASHBOARD                       │
│                                                      │
│ Country Selection → Prediction → Analytics           │
│                                                      │
└──────────────────────────────────────────────────────┘

---

🧠 Machine Learning Performance

Model Comparison

Model| Accuracy| Precision| Recall| F1 Score
Logistic Regression| 70.91%| 0.71| 0.71| 0.70
XGBoost (Production)| 96.36%| 0.96| 0.96| 0.96

---

Dataset Overview

Metric| Value
African Countries| 54
Original Records| 594
Cleaned Records| 550
Risk Classes| 3
Features Engineered| 19
Time Range| 2007–2017

Features Used

- Country
- Year
- Urban Population %
- Rural Population %
- Urban Growth Rate
- Rural Growth Rate
- Water Access %
- Sanitation Access %
- Geographic Coordinates

---

📡 API Reference

Base URL

http://127.0.0.1:8000

---

Health Check

GET /

Response

{
  "message": "Nexora Sentinel API is running",
  "status": "healthy",
  "version": "1.0.0"
}

---

Get Countries

GET /countries

Response

{
  "countries": ["Ghana", "Nigeria", "..."],
  "total": 54
}

---

Predict Outbreak Risk

POST /predict

Request

{
  "country": "Ghana",
  "year": 2024,
  "urban_population_pct": 58.0,
  "rural_population_pct": 42.0,
  "urban_growth": 3.2,
  "rural_growth": 1.8,
  "water_access_pct": 61.0
}

Response

{
  "country": "Ghana",
  "year": 2024,
  "risk_level": "Low",
  "confidence": 56.4,
  "color": "#22c55e",
  "message": "Low malaria outbreak risk predicted for Ghana in 2024"
}

---

🚀 Quick Start

1. Clone Repository

git clone https://github.com/Eddiegah/nexora-sentinel.git
cd nexora-sentinel

---

2. Create Virtual Environment

python -m venv venv

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate

---

3. Install Dependencies

pip install -r ml/requirements.txt
pip install fastapi uvicorn

---

4. Train the Model

python ml/data/clean.py
python ml/models/train.py

---

5. Launch API

uvicorn backend.main:app --reload

Visit:

http://127.0.0.1:8000

Swagger Docs:

http://127.0.0.1:8000/docs

---

6. Launch Dashboard

cd frontend
npm install
npm start

Dashboard:

http://localhost:3000

---

📂 Project Structure

nexora-sentinel
│
├── data
│   ├── raw
│   └── processed
│
├── ml
│   ├── data
│   │   ├── explore.py
│   │   └── clean.py
│   │
│   ├── models
│   │   └── train.py
│   │
│   └── artifacts
│       ├── best_model.pkl
│       ├── scaler.pkl
│       └── label_encoders.pkl
│
├── backend
│   └── main.py
│
├── frontend
│   └── src
│       └── App.js
│
├── docs
│
└── README.md

---

🛣️ Roadmap

✅ Phase 1 — MVP

- [x] Real-world malaria dataset
- [x] Feature engineering pipeline
- [x] XGBoost model training
- [x] FastAPI backend
- [x] React dashboard
- [x] Multi-country prediction support

---

🔄 Phase 2 — In Progress

- [ ] SHAP Explainability
- [ ] PostgreSQL Integration
- [ ] User Authentication
- [ ] Prediction History
- [ ] Dengue Fever Prediction
- [ ] Cholera Prediction
- [ ] Automated Reports

---

🔮 Phase 3 — Future Vision

- [ ] Docker Deployment
- [ ] AWS Infrastructure
- [ ] CI/CD Pipeline
- [ ] Real-Time WHO Data Feeds
- [ ] Interactive Africa Risk Map
- [ ] LLM-Powered Outbreak Reports
- [ ] Multi-Disease Surveillance Network

---

💡 Why This Project Matters

Most health AI projects are:

- Built using synthetic datasets
- Difficult to reproduce
- Designed for research papers rather than deployment

Nexora Sentinel is different.

✅ Built on real-world public health data

✅ Designed specifically for African contexts

✅ Fully reproducible and open source

✅ Focused on practical decision support

✅ Created to help save lives through earlier action

---

👨‍💻 Author

Edmund Eric Gah

AI/ML Engineer • Full-Stack Developer • HealthTech Builder

I build intelligent systems that solve real-world problems through machine learning, software engineering, and data science.

Nexora Sentinel represents my vision of using AI not merely to automate tasks, but to improve health outcomes across Africa.

Connect With Me

- GitHub: https://github.com/Eddiegah
- LinkedIn: www.linkedin.com/in/edmund-eric-gah-7432a7213
- Email: gahedmund146@gmail.com

Open To

- Research Collaborations
- Machine Learning Internships
- Open Source Partnerships
- Graduate Opportunities
- HealthTech Innovation Projects

---

📜 License

Distributed under the MIT License.

Feel free to use, modify, and build upon this project.

---

<div align="center">⭐ Support The Project

If you believe AI should help save lives, improve healthcare access, and strengthen disease surveillance systems across Africa:

Give this repository a star.

Your support helps increase visibility and encourages further development.

Together, we can build smarter public health systems.

🛡️ 🌍 🤖

</div>
