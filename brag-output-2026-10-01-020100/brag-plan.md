# Brag Plan: AgriSense AI (Extended Feature Tour)

## What is this app?
AgriSense AI is a production-grade agricultural intelligence and economic decision-support platform engineered for Indian farmers — combining an ML crop recommender (tuned SVM, 22 crops, 98.68% accuracy), a two-stage partitioned fertilizer advisor (rule guidance + 39-feature XGBoost classifier), live APMC mandi price intelligence with a mathematical sell-or-hold decision engine, crop health diagnostics with field scouting logs, real-time agro-weather alerts, community marketplace, and a bilingual AI farming assistant.

## The angle
This isn't a prototype or conceptual pitch deck. It is an end-to-end, live-deployed platform engineered with real agricultural data science. The video walks through every single core subsystem step-by-step with enough screen time for farmers, judges, and developers to absorb the UI, verify the ML benchmark metrics, see the mathematical sell/hold logic in action, and explore the bilingual capability.

## Hook (first 4.5 seconds)
A warm earth-toned canvas (#292420 to #faf9f7) reveals the bold, confident project headline:
"Crop knowledge. Market intelligence. Sell smarter."
Below it, the platform badge "Agricultural intelligence for every season" glows softly alongside the dynamic season context switcher: **Rabi · Kharif · Zaid**.

## Key moments (scenes 2–7)
- **1. Seasonal Context & Unified Dashboard:** Real telemetry cards appear (Current Crop: Wheat, Health: 90/Excellent, Mandi Price: ₹2,394, Weather: 29.2°C) with live 120-day historical sparkline trends.
- **2. ML Crop Recommendation Engine:** 7 agronomic and meteorological inputs (N, P, K, pH, Temp, Humidity, Rain) feed into the tuned SVM classifier, returning "🌾 Wheat" at 98% calibrated confidence with benchmark proof (98.68% accuracy across 50,000 stress-tested samples).
- **3. Two-Stage Partitioned Fertilizer Advisor:** Demonstrating the dual architecture: Stage-aware rule guidance + 39-feature XGBoost ML classifier predicting commercial formulations (Urea 46-0-0 at 94% confidence).
- **4. Mandi Price Intelligence & Sell/Hold Decision Engine:** Tracking 8 major APMC markets and running the cold storage cost vs. price velocity calculation to recommend: "HOLD — Expected Return: +₹240/quintal · Low Risk".
- **5. Crop Health, Field Scouting & Weather Intelligence:** 22-crop agronomic knowledge catalog (diseases, organic alternatives, prevention protocols) plus photographic field observation logs and live Open-Meteo alerts.
- **6. Community Marketplace & Bilingual AI Assistant:** Direct farmer-to-buyer crop listing board paired with an instant agronomic assistant answering in both English and Hindi.

## Outro / punchline (Scene 8)
AgriSense AI brand lockup with complete technical and bilingual credentials:
"22 Indian Crops · 8 APMC Markets · 100% Bilingual (English & हिंदी)"
"FastAPI · React · Scikit-Learn · XGBoost · Supabase RLS"
Live at `agri-sense-ai-nine.vercel.app`

## Tone
- Preset: polished
- Creative direction: earnest agricultural tech — production-grade, authoritative, and data-driven
- Interpretation: confidence through clarity and breathing room. Each feature receives a full 6–7 seconds with real UI captures, clear typography, and subtle micro-animations.

## Format: landscape — 1920x1080
## Duration: 50 seconds (8 scenes)

## Visual identity (from the project)
- Background: #faf9f7 (soil-50, warm cream) & #292420 (soil-950, deep dark earth)
- Primary Accent: #247b4c (primary-700, deep forest green) / #339961 (primary-500)
- Secondary Accent: #fcb424 (harvest amber, accent-400) / #f5930b (accent-500)
- Display Font: Manrope (extrabold, 700-800 weight)
- Body Font: Inter (400-600 weight)
- Card Architecture: rounded-2xl, subtle borders (#e8e5df), layered drop-shadows, authentic dashboard screenshot integrations

## Audio direction
- Role: warm corporate bed — steady, clean, confidence-building
- Music: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` (1:58 track duration; perfect for 50s)
- Music treatment: fade in from 0.0s at 0.35 volume, steady driving pulse, gentle swell on ML and decision engine reveals, soft fade out under the final logo hold (47s - 50s)
- SFX posture: subtle accents on card entrances and button clicks (drop_001.ogg, click_003.ogg)

## Storyboard

### Scene 1 — Hook & Seasonal Context (0.0s – 5.5s)
Deep soil background with soft ambient vignette.
- Top: AgriSense AI logo emblem.
- Center: Three-line hero headline reveals sequentially:
  "Crop knowledge."
  "Market intelligence."
  "Sell smarter."
- Bottom: Dynamic Season Context Switcher:
  [ ❄️ Rabi ]  [ 🌧 Kharif ]  [ ☀️ Zaid ]
  Badge pulses: "Agricultural intelligence for every season"
- Audio: Music enters smoothly; gentle sound accent on each phrase.
- Transition: Smooth slide & scale into the dashboard.

### Scene 2 — Unified Farmer Dashboard (5.5s – 12.0s)
The farmer dashboard view with RABI season badge.
- Left/Center: Actual dashboard screenshot in a sleek browser frame.
- Right overlay cards animate in:
  1. CURRENT CROP: Wheat (Sowing: Oct–Nov)
  2. CROP HEALTH: 90 · Excellent
  3. MANDI PRICE: ₹2,394 / quintal (Azadpur Mandi)
  4. LIVE WEATHER: 29.2°C · Rain (💧 89% · 🌧 88%)
- Bottom: 120-Day Mandi Price Sparkline draws with upward green trend.
- Transition: Clean pan to Crop Recommendation.

### Scene 3 — ML Crop Recommendation Engine (12.0s – 18.5s)
Machine Learning in action:
- Left: 7 Soil & Climate parameters highlight:
  N: 90 | P: 42 | K: 43 | pH: 6.5 | Temp: 20.8°C | Humidity: 82% | Rain: 202mm
- Simulated "Predict Crop" button click.
- Right: Prediction card expands:
  "🌾 Recommended Crop: Wheat"
  Confidence bar animates from 0% to 98% in vibrant forest green.
- Architecture badge: "Tuned SVM (RBF Kernel, C=10.0) · 98.68% Accuracy · 50,000-Sample Stress Test · 22 Crops".
- Transition: Dissolve to Fertilizer Advisor.

### Scene 4 — Two-Stage Partitioned Fertilizer Advisor (18.5s – 25.0s)
Dual-architecture advisor:
- Dual-mode selector cards:
  - **Mode 1: API-Based Rule Guidance** (Crop Stage: Vegetative → Split NPK Application Schedule).
  - **Mode 2: ML-Based Prediction** (39-Feature XGBoost Multi-Class Classifier).
- Live result highlight:
  "Commercial Formulation: Urea (46-0-0)"
  "Confidence: 94% · Soil Type: Clayey · Target: High Vegetative Vigour"
- Transition: Slide to Market Intelligence.

### Scene 5 — Mandi Price Intelligence & Sell/Hold Engine (25.0s – 32.0s)
Market analytics & economic decision support:
- Normalized APMC market prices across 8 major Indian mandis (Azadpur, Vashi, Khanna, etc.).
- 120-day historical trend graph with 7/14/30-day velocity indicators.
- Cold Storage Cost Simulator: 30 days @ ₹40/month.
- Decision Engine Output Card:
  Large green badge: "HOLD"
  "Expected Net Return: +₹240 / quintal"
  "Risk Level: Low · Rationale: Upward price momentum exceeds carrying costs"
- Transition: Pan to Crop Health & Diagnostics.

### Scene 6 — Crop Health Diagnostics & Field Scouting (32.0s – 38.5s)
Agronomic protection and live weather:
- 22-Crop Agronomic Catalog: Disease symptoms, chemical treatments, and organic bio-alternatives (Trichoderma & Neem extract).
- Scouting Observation Card: In-field photo record logged with severity "Moderate" and date badge.
- Open-Meteo Weather Card: Agro-meteorological spraying and irrigation hazard alerts.
- Transition: Slide to Community Marketplace & Assistant.

### Scene 7 — Community Marketplace & Bilingual Assistant (38.5s – 45.0s)
Community trade and AI assistance:
- Direct Farmer Marketplace: Verified crop trade listing: "Sharbati Wheat Grade-A · 50 Quintals @ ₹2,450/q".
- Bilingual AI Assistant: Chat dialog answering farmer queries in English and Hindi (हिंदी) with real agronomic context.
- Language Switcher Pill: [ English ] | [ हिंदी ]
- Transition: Elegant zoom to Outro.

### Scene 8 — Outro & Live Production Deployment (45.0s – 50.0s)
AgriSense AI brand resolution:
- AgriSense AI emblem & glowing typography.
- Platform Credentials:
  "22 Indian Crops · 8 APMC Markets · 100% Bilingual"
  "FastAPI · Scikit-Learn · XGBoost · Supabase RLS · React & Tailwind"
- Primary CTA:
  `agri-sense-ai-nine.vercel.app`
- Music fades out softly.

## Voiceover script
- **Scene 1 (0.0s – 5.5s):** "Crop knowledge. Market intelligence. Sell smarter. This is AgriSense AI, an intelligent agricultural platform built for Indian farmers across Rabi, Kharif, and Zaid seasons."
- **Scene 2 (5.5s – 12.0s):** "The dashboard adapts dynamically to the growing season, delivering live telemetry on crop health, local weather conditions, and real-time mandi prices."
- **Scene 3 (12.0s – 18.5s):** "Our tuned Support Vector Machine analyzes seven soil and climatic parameters, achieving ninety-eight point six percent accuracy across twenty-two Indian crops."
- **Scene 4 (18.5s – 25.0s):** "A dual-stage advisor pairs growth-stage agronomic rules with an XGBoost classifier predicting commercial fertilizer formulations like Urea and DAP."
- **Scene 5 (25.0s – 32.0s):** "Tracking eight major APMC markets, the mathematical Sell or Hold engine factors cold storage costs against price velocity to maximize farmer profit."
- **Scene 6 (32.0s – 38.5s):** "Farmers get disease diagnostics with biological alternatives, photo-verified field scouting, and live weather hazard warnings for spraying."
- **Scene 7 (38.5s – 45.0s):** "Cut out middlemen with a direct community marketplace, and get instant answers from our AI assistant in both English and Hindi."
- **Scene 8 (45.0s – 50.0s):** "Live, bilingual, and deployed for Indian agriculture. Explore the live platform today at AgriSense AI."

