# 🌾 AgriSense AI — Agricultural Intelligence & Decision Support

[![LIVE DEMO](https://img.shields.io/badge/LIVE_DEMO-VERCEL-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://agri-sense-ai-nine.vercel.app/)
[![BACKEND API](https://img.shields.io/badge/BACKEND_API-RENDER-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://agrisense-api-0p24.onrender.com/docs)
[![DATABASE](https://img.shields.io/badge/DATABASE-SUPABASE-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![PYTHON](https://img.shields.io/badge/PYTHON-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FASTAPI](https://img.shields.io/badge/FASTAPI-0.112-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![REACT](https://img.shields.io/badge/REACT-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TYPESCRIPT](https://img.shields.io/badge/TYPESCRIPT-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![TAILWIND CSS](https://img.shields.io/badge/TAILWIND_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

🚀 **Live Web Application:** [https://agri-sense-ai-nine.vercel.app/](https://agri-sense-ai-nine.vercel.app/)  
⚡ **Interactive Swagger API Docs:** [https://agrisense-api-0p24.onrender.com/docs](https://agrisense-api-0p24.onrender.com/docs)  
🔑 **Demo Account:** `demo@agrisense.ai` | `Demo@1234`

---

## 📖 About The Project

**AgriSense AI** is a production-grade agricultural intelligence and decision-support platform engineered for Indian farmers. It combines **Machine Learning crop recommendation** across 22 distinct crops, normalized mandi (market) price intelligence with historical price trends, live real-time weather forecasts with agro-advisories, interactive place search and GPS geolocation, educational disease/pest management, fertilizer guidance, a farmer marketplace, and transparent sell-or-hold decision support.

The backend acts as the central API orchestration layer, owning the database (PostgreSQL on Supabase with Row Level Security), running Scikit-Learn ML inference pipelines, integrating external APIs (Open-Meteo ECMWF/GFS weather, mandi prices, assistant), and serving a standardized REST contract to the bilingual (English & Hindi) React frontend.

![Landing page](docs/screenshots/landing.png)

---

## 📑 Table of Contents

- [📖 About The Project](#-about-the-project)
- [🌟 Key Features](#-key-features)
- [🤖 Machine Learning Architecture](#-machine-learning-architecture)
- [📸 Interface Tour](#-interface-tour)
- [🏛️ System Architecture](#-system-architecture)
- [🛠️ Technology Stack](#-technology-stack)
- [📂 Repository Structure](#-repository-structure)
- [🚀 How to Run Locally](#-how-to-run-locally)
- [⚙️ Environment Variables](#-environment-variables)
- [📡 API Overview](#-api-overview)
- [🧠 Key Workflows](#-key-workflows)
- [🗄️ Database Schema & Security](#-database-schema--security)
- [🧪 Testing](#-testing)
- [⚠️ Disclaimers](#-disclaimers)

---

## 🌟 Key Features

| Capability | Description |
|---|---|
| **🤖 ML Crop Recommendation** | Tuned **Support Vector Machine (SVM)** model predicting the most suitable crop out of **22 Indian crops** based on 7 soil & environmental parameters with confidence scoring and optimal growing requirements. |
| **🌾 Season & Crop Catalog** | Database-driven catalog covering **Rabi** (wheat, chickpea, mustard, potato) and **Zaid/summer** (watermelon, cucumber, muskmelon, moong) crops with growing calendars. |
| **📈 Mandi Price Intelligence** | Normalized mandi price board (min / max / modal per quintal), 90-day history, and rule-computed 7/14/30-day trends across major Indian markets. |
| **⚖️ Sell or Hold Decision Engine** | Transparent rule engine comparing market trends against warehouse storage costs to output clearly reasoned recommendations. |
| **🌦️ Live Weather & Geocoding Search** | Real-time weather via Open-Meteo (ECMWF/GFS models), interactive city search bar with autocomplete, GPS one-click location detection, and agricultural risk alerts. |
| **🩺 Crop Health & Field Records** | Educational disease & pest database with symptoms, organic alternatives, and prevention. Farmers can log and delete field observations with severity and photos. |
| **🧪 Fertilizer Guidance** | Rule-based, stage- and soil-aware nutrient recommendations for balanced NPK application. |
| **🛒 Farmer Marketplace** | Community trade board with crop listings, unit pricing, search, location filters, and ownership controls. |
| **💬 Farmer Assistant** | Chat interface backed by an agricultural knowledge engine with conversational fallback support. |
| **📊 Aggregated Dashboard** | Unified dashboard combining crop records, market movements, weather forecasts, and notification feeds with graceful degradation. |
| **🌐 Bilingual Support** | Native, full-interface localization in both **English** and **Hindi (हिंदी)**. |

---

## 🤖 Machine Learning Architecture

The **Crop Recommendation Engine** helps farmers determine the optimal crop to cultivate by analyzing 7 agronomic and meteorological factors:

$$\vec{x} = \big[ N, P, K, \text{Temperature (°C)}, \text{Humidity (\%), pH, Rainfall (mm)} \big]$$

```
                        [ N, P, K, Temp, Humidity, pH, Rainfall ]
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    Tuned Support Vector Classifier    │
                      │         (RBF Kernel, C=10.0)          │
                      └───────────────────┬───────────────────┘
                                          │
                        Decision Margins: f(x) ∈ ℝ²²
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │      Stable Softmax Normalization     │
                      │  P(Crop_i | x) = exp(z_i) / Σ exp(z_j)│
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                   Top-1 Primary Crop Recommendation + Confidence Score
                   + Agricultural Ideal Range Diagnostics (N, P, K, pH)
```

### 🏆 Model Selection & Benchmark Evaluation

5 machine learning algorithms were benchmarked across standard validation data and a **50,000-sample unseen stress-test suite** (containing simulated noisy sensor inputs and severe boundary overlap):

| Model | Standard Accuracy (2,200 rows) | Unseen Stress Test (50k rows) | Noisy Sensor Accuracy | Decision Overlap Accuracy |
|---|:---:|:---:|:---:|:---:|
| **Tuned SVM (Selected)** 🥇 | **98.68%** | **89.20%** | **90.05%** | **53.52%** |
| Random Forest | 99.09% | 88.08% | 89.14% | 47.96% |
| XGBoost Classifier | 98.64% | 88.35% | 89.26% | 48.96% |
| Gaussian Naive Bayes | 99.09% | 87.87% | 89.18% | 48.33% |
| K-Nearest Neighbors | 98.18% | 85.12% | 86.20% | 44.48% |

### 🌾 Supported Crop Classes (All 22 Crops)
* **Cereals & Grains:** Rice, Maize
* **Pulses & Legumes:** Chickpea, Kidney Beans, Pigeon Peas, Moth Beans, Mung Bean, Black Gram, Lentil
* **Fruits:** Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut
* **Cash Crops & Fibers:** Cotton, Jute, Coffee

### 💡 Production Engineering Highlights
- **Numerically Stable Softmax:** Computes calibrated probabilities over one-vs-rest hyperplanes using $z_i = \text{decision\_function}(\vec{x})_i$ with $z_{\max}$ offset subtraction to prevent floating-point overflow.
- **Lazy Loading Singleton:** Packaged within `backend/app/ml_models/SVM_tunned_model.pkl` and loaded on-demand to ensure fast Docker container cold-starts and low memory footprints.
- **Agronomic Requirements Mapping:** Enriches predictions with standard N-P-K nutrient targets, climate tolerances, growing seasons, and soil requirements.

---

## 📸 Interface Tour

| Sign In | Create Account |
| :---: | :---: |
| ![Sign In](docs/screenshots/login.png) | ![Create Account](docs/screenshots/register.png) |

| Farmer Dashboard | Crop Recommendation (ML) |
| :---: | :---: |
| ![Dashboard](docs/screenshots/dashboard.png) | ![Crop Recommendation](docs/screenshots/crops.png) |

| Market Price Intelligence | Live Weather & City Search |
| :---: | :---: |
| ![Market Prices](docs/screenshots/market.png) | ![Weather Forecast](docs/screenshots/weather.png) |

| Crop Health & Disease Catalog | Sell vs. Hold Recommendation Engine |
| :---: | :---: |
| ![Crop Health](docs/screenshots/health.png) | ![Sell or Hold](docs/screenshots/recommendation.png) |

| Farmer Marketplace | Farmer Assistant |
| :---: | :---: |
| ![Marketplace](docs/screenshots/marketplace.png) | ![Farmer Assistant](docs/screenshots/assistant.png) |

---

## 🏛️ System Architecture

The frontend communicates with the backend's versioned REST API (`/api/v1`, JSON over HTTP with JWT bearer authentication). The backend acts as the single source of truth, validating all inputs, managing database transactions, caching responses, and orchestrating ML models and external APIs.

```mermaid
flowchart TD
    subgraph Frontend["Frontend Client (React + Vite + Tailwind)"]
        UI[UI Components & Autocomplete Search]
        Store[Context Store: Auth, Crop, Theme, I18n]
        APIService[Typed API Client]
        UI --> Store
        Store --> APIService
    end

    subgraph Backend["Backend Layer (FastAPI)"]
        MW[Middleware: Correlation ID, Structured Logging, Rate Limiting]
        Routers["Versioned Routers (/api/v1)"]
        MLService["ML Inference Engine (Tuned SVM - 22 Crops)"]
        Services["Service Layer: Market, Weather, Recommendations, Health"]
        ExtClients["External Clients (Shared httpx with Retry & Backoff)"]
        Cache["Cache Layer (Redis / In-Memory TTL)"]
        DBLayer["ORM & Database Layer (SQLAlchemy 2.0)"]

        APIService -->|HTTP / JSON + JWT Bearer| MW
        MW --> Routers
        Routers --> MLService
        Routers --> Services
        Services <--> Cache
        Services --> ExtClients
        Services --> DBLayer
    end

    subgraph External["Data Sources & Persistence"]
        DB[(PostgreSQL on Supabase with RLS)]
        WeatherAPI[Open-Meteo Weather API ECMWF/GFS]
        GeocodingAPI[Open-Meteo Geocoding API]
        MandiAPI[Agmarknet / Mandi Price Feed]

        DBLayer <--> DB
        ExtClients --> WeatherAPI
        ExtClients --> GeocodingAPI
        ExtClients --> MandiAPI
    end
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript 5.5, Vite 5.4, Tailwind CSS 3.4, React Router 6, Recharts, Marked, DOMPurify |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn, httpx (async HTTP client) |
| **Machine Learning** | Scikit-Learn (SVM RBF), NumPy, Joblib |
| **Database** | PostgreSQL 16 on Supabase (with Row Level Security) / SQLite fallback |
| **Caching** | Redis 7 / In-memory process-local TTL cache fallback |
| **Security & Auth** | JWT (HS256) with Passlib & Bcrypt, Supabase RLS, rate limiting, magic-byte upload validation |
| **Localization** | Lightweight custom I18n provider supporting English and Hindi (हिंदी) |
| **Deployment** | Vercel (Frontend), Render (Backend), Supabase (Database), Docker Compose |

---

## 📂 Repository Structure

```text
AgriSense-AI/
|-- frontend/
|   |-- src/
|   |   |-- api/               auth provider
|   |   |-- assets/            logos, crop illustrations
|   |   |-- components/        layout, UI primitives, modal, shared states
|   |   |-- config/            API base URL, backend origin
|   |   |-- hooks/             data fetching, debounce, online status
|   |   |-- i18n/              English + Hindi dictionaries
|   |   |-- pages/             13 application pages (Crop Recommendation, Weather, Health, etc.)
|   |   |-- services/          typed API service modules (single fetch client)
|   |   |-- store/             crop selection, notifications, theme contexts
|   |   |-- types/             API contract types mirroring backend schemas
|   |   `-- utils/             formatting, image resolution, markdown
|-- backend/
|   |-- app/
|   |   |-- api/v1/            REST routers (versioned: crops, weather, recommendation, etc.)
|   |   |-- core/              config, security, cache, errors
|   |   |-- db/                engine, session, idempotent seeding
|   |   |-- external/          weather, mandi and assistant clients
|   |   |-- middleware/        request context, rate limiting
|   |   |-- ml_models/         packaged trained SVM model binary (SVM_tunned_model.pkl)
|   |   |-- models/            SQLAlchemy ORM models
|   |   |-- schemas/           Pydantic request/response schemas
|   |   `-- services/          ML crop service, weather service, market service
|   |-- tests/                 83 automated pytest test cases (100% pass)
|   |-- Dockerfile             production container configuration
|   `-- requirements.txt       backend dependencies
|-- datasets/
|   `-- crop recommendation/   evaluation notebooks and datasets (2.2k and 50k stress-test)
|-- render.yaml                Render deployment blueprint
|-- docker-compose.yml         postgres + redis + backend + frontend
|-- .env.example               environment variable template
`-- README.md
```

---

## 🚀 How to Run Locally

### Option 1: Docker Compose (Recommended)

Starts PostgreSQL, Redis, the FastAPI backend, and the React frontend:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| **Frontend** | [http://localhost:5173](http://localhost:5173) |
| **Backend API** | [http://localhost:8000/api/v1](http://localhost:8000/api/v1) |
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) |

---

### Option 2: Local Development (Zero Infrastructure)

The backend defaults to a local SQLite database and automatically seeds initial reference data on startup.

**1. Backend:**
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Frontend:**
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` (backend reads `backend/.env`). Every external integration is optional; when unconfigured, database fallbacks apply.

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string; SQLite when unset | SQLite file |
| `JWT_SECRET` | JWT signing secret | development value, must be changed in production |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Access token lifetime | `7` |
| `CORS_ORIGINS` | Comma-separated allowed browser origins | `http://localhost:5173,...` |
| `UPLOAD_DIR` / `MAX_UPLOAD_MB` | Crop image upload storage and size cap | `uploads` / `8` |
| `WEATHER_API_URL` | Open-Meteo-compatible weather endpoint | `https://api.open-meteo.com/v1` |
| `REDIS_URL` | Shared cache backend; empty uses process-local TTL cache | empty |
| `VITE_API_BASE_URL` | API base URL used by the frontend | `http://localhost:8000/api/v1` |

---

## 📡 API Overview

All endpoints are versioned under `/api/v1`. Interactive OpenAPI documentation is served at `/docs`.

| Area | Endpoints |
|---|---|
| **Crop Recommendation (ML)** | `POST /api/v1/crop-recommendation/predict` (22 crops, SVM RBF model) |
| **System & Health** | `GET /api/v1/system`; `GET /health`, `GET /health/live`, `GET /health/ready` |
| **Authentication** | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `PATCH /auth/me` |
| **Seasons & Crops** | `GET /seasons`, `GET/POST /crops`, `GET/PATCH/DELETE /crops/{id}`, `GET/POST/DELETE /crops/{crop_id}/records` |
| **Knowledge Base** | `GET /diseases`, `GET /pests`, `GET /treatments`, `GET /fertilizers` |
| **Fertilizer Guidance** | `POST /fertilizer-guidance` (soil & stage-aware) |
| **Market Intelligence** | `GET /market/markets`, `GET /market/prices`, `GET /market/trends/{cropId}` |
| **Weather** | `GET /weather/current`, `GET /weather/forecast`, `GET /weather/location` |
| **Decisions** | `POST /recommendations/sell-hold`, `GET /recommendations/history` |
| **Dashboard** | `GET /dashboard` (single aggregated response) |
| **Marketplace** | `GET/POST /listings`, `GET/PATCH/DELETE /listings/{id}` |
| **Assistant** | `POST /assistant/chat`, `GET /assistant/conversations[/{id}]` |
| **Notifications** | `GET /notifications`, `PATCH /notifications/{id}/read`, `PATCH /notifications/read-all` |
| **Uploads** | `POST /uploads` (multipart, images only, magic-byte sniffed) |

---

## 🗄️ Database Schema & Security

All 13 public tables are protected with **Supabase Row Level Security (RLS)**, ensuring zero unauthorized direct public access via client keys, while the backend maintains full transactional access via PostgreSQL superuser connections.

| Entity | Purpose | Security & Ownership |
|---|---|---|
| `users` | User accounts with bcrypt-hashed credentials | Protected with RLS |
| `farmer_profiles` | Village, district, state, farm size in acres | One-to-one with `users` |
| `crops` | Catalog: season, growing period, sowing and harvest windows | Reference catalog |
| `farmer_crops` | User-planted crops and harvest dates | Scoped to authenticated user |
| `health_records` | Field observations: disease/pest, severity, photo URL | User-owned with delete support |
| `markets` & `market_prices` | Mandi reference data and daily price records | Reference data |
| `sell_hold_recommendations` | Decision outputs with storage cost and expected return | Scoped to user and crop |
| `crop_listings` | Marketplace trade listings with contact info | User-owned trade listings |
| `assistant_conversations` & `messages`| Farmer assistant conversational history | Scoped to authenticated user |
| `notifications` | In-app alerts for weather, market, and field records | User-scoped notification feed |

---

## 🧪 Testing

```bash
# Run backend pytest suite (83 tests, 100% pass)
cd backend
pytest tests/ -v

# Run frontend TypeScript check & production build
cd frontend
npm run build
```

---

## ⚠️ Disclaimers

- **Educational Guidance**: Agricultural content (diseases, pests, treatments, fertilizer guidance) is educational information. Always consult local Krishi Vigyan Kendras (KVK) or certified agricultural extension officers before taking action.
- **Decision Support**: The sell or hold engine provides mathematical decision-support rules based on recorded mandi trends and storage costs. It does not constitute financial advice.
