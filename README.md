# RePlate — Smart Campus Mess Surplus Router 🍲🌱

> **Built for Arbiter Hacks V1 Hackathon**  
> *Closing the loop on campus dining waste: Source Reduction (Kitchen Prep Forecasting) + Real-time Surplus Rescue (NGO Routing).*

---

## 🌟 Overview & Problem Statement
Campus dining halls often overcook food by predicting fixed meal attendances, and when leftovers remain at shift closing, safe redistribution fails due to lack of real-time cold-chain/ambient shelf-life tracking and trusted handover protocols.

**RePlate** tackles this with a two-phase closed-loop system:
1. **Source Reduction (Kitchen Predictor):** Allows hostellers to flag meal opt-outs in advance. RePlate recalculates exact raw grain, dairy, and produce requirements—preventing food from ever being over-cooked (**0.45 kg raw food saved per skipped meal**).
2. **Dynamic Rescue Routing (NGO Rescue Portal):** For unavoidable leftover trays, mess supervisors log batches in under 15 seconds. RePlate assigns strict microbiological shelf-life countdowns (2h for Dairy/Curry, 4h for Grains, 6h for Dry Rotis) and generates a tamper-proof 4-digit handover OTP for arriving NGOs.

---

## 🚀 Key Features

### 1. 🍳 Kitchen Predictor (Prevention)
- Interactive student opt-out slider (0 to 350 capacity) & quick scenario buttons ("Simulate 25 Students Skipping", "+10 Diners", "Weekend Out").
- Dynamic calculation of expected diners, recommended batch weight, and raw pantry food prevented from cooking.
- Real-time Chef Prep Directive generated for kitchen staff.

### 2. 🍲 Surplus Logger (Triage)
- Fast 2-tap logging form for closing mess staff (Dish Description, Category, Weight in kg).
- Automatic shelf life calculation:
  - **Dairy / Curry:** 2 Hours (high spoilage risk)
  - **Rice & Grains:** 4 Hours (medium perishability)
  - **Rotis & Dry:** 6 Hours (low moisture)
- One-click **"⚡ Simulate Demo Surplus"** button for instant live presentation testing.
- Optional Discord Webhook broadcast embed trigger.

### 3. 🚚 NGO Rescue Portal (Redistribution)
- Real-time cards for active surplus batches with **live ticking countdown timers (`HH:MM:SS` remaining)**.
- Spoilage warning indicators (green -> amber -> pulsing red alert).
- "Claim Pickup" workflow with partner NGOs (Robin Hood Army, Feeding India, Roti Bank).
- Tamper-proof **4-Digit Handover OTP** badge displayed upon claiming.

### 4. 📊 Impact Metrics (Judges' View)
- 4 Primary Hero KPI cards:
  - **Total Kg Diverted** (Pre-production saved + Claimed rescued)
  - **Nutritious Meals Served** (@ 400g/meal)
  - **Surplus Recovery Rate %**
  - **Pre-Meal Waste Cut %**
- Financial & ESG co-benefits: Direct campus budget savings (₹) and CO₂e emissions avoided.
- **Chart.js Visualizations:**
  - 7-Day Pre-RePlate Historical Baseline vs Post-RePlate Reduction.
  - Surplus Category Perishability Mix (Doughnut Chart).
- **1-Click Pitch Telemetry Export:** Instant clipboard copy of ESG impact stats for judges.

---

## 🛠️ Tech Stack
- **Backend:** Python 3, Flask, Requests, Pandas
- **Frontend:** Single-page dashboard, Tailwind CSS (via CDN), Chart.js (via CDN), Vanilla JavaScript
- **Persistence:** Local JSON store (`replate_data.json`) with automatic default demo data initialization

---

## 🏃 Quick Start

### 1. Activate Environment
```bash
cd replate-campus
source venv/bin/activate
```

### 2. Run Flask App
```bash
python app.py
```
Open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves single-page dashboard (`templates/index.html`) |
| `GET` | `/api/state` | Returns full system state, headcount forecast, active batches, and metrics |
| `POST` | `/api/student-rsvp` | Updates student opt-out count & recalculates prep target |
| `POST` | `/api/log-surplus` | Logs leftover tray, computes `expires_at`, generates 4-digit OTP |
| `POST` | `/api/claim-surplus` | Assigns batch to NGO, transitions status to "Claimed", returns OTP |
| `POST` | `/api/simulate-surplus`| Injects a realistic demo surplus tray for live demos |
| `POST` | `/api/update-config` | Configures optional Discord webhook alert URL |
| `POST` | `/api/reset-demo` | Resets state to clean initial presentation state |


