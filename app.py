import os
import json
import random
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replate_data.json")

# Category shelf life configuration in hours
SHELF_LIFE_HOURS = {
    "Dairy/Curry": 2,
    "Rice/Grains": 4,
    "Rotis/Dry": 6
}

SAMPLE_DISHES = [
    {"name": "Paneer Butter Masala & Gravy", "category": "Dairy/Curry", "weight": 14.5},
    {"name": "Dal Tadka & Steamed Jeera Rice", "category": "Rice/Grains", "weight": 22.0},
    {"name": "Tawa Roti & Methi Thepla", "category": "Rotis/Dry", "weight": 12.0},
    {"name": "Rajma Masala Curry", "category": "Dairy/Curry", "weight": 18.0},
    {"name": "Vegetable Pulao & Raita", "category": "Rice/Grains", "weight": 15.5},
    {"name": "Aloo Parathas & Mixed Pickle", "category": "Rotis/Dry", "weight": 10.5},
    {"name": "Chole Masala Gravy", "category": "Dairy/Curry", "weight": 16.0}
]

def generate_default_data():
    now = datetime.now()
    
    # 7-day historical baseline before RePlate vs post-RePlate
    historical_baseline = [
        {"day": "Mon", "cooked_kg": 157.5, "pre_replate_waste_kg": 28.5, "post_replate_waste_kg": 6.0},
        {"day": "Tue", "cooked_kg": 155.0, "pre_replate_waste_kg": 25.0, "post_replate_waste_kg": 5.2},
        {"day": "Wed", "cooked_kg": 160.0, "pre_replate_waste_kg": 32.5, "post_replate_waste_kg": 7.1},
        {"day": "Thu", "cooked_kg": 152.0, "pre_replate_waste_kg": 26.0, "post_replate_waste_kg": 4.9},
        {"day": "Fri", "cooked_kg": 158.5, "pre_replate_waste_kg": 31.0, "post_replate_waste_kg": 8.2},
        {"day": "Sat", "cooked_kg": 148.0, "pre_replate_waste_kg": 23.5, "post_replate_waste_kg": 4.5},
        {"day": "Sun", "cooked_kg": 156.0, "pre_replate_waste_kg": 29.5, "post_replate_waste_kg": 5.8}
    ]

    # Pre-populate realistic active surplus batches relative to now
    batch_1_logged = now - timedelta(minutes=35)
    batch_1_expires = batch_1_logged + timedelta(hours=SHELF_LIFE_HOURS["Dairy/Curry"])

    batch_2_logged = now - timedelta(minutes=50)
    batch_2_expires = batch_2_logged + timedelta(hours=SHELF_LIFE_HOURS["Rice/Grains"])

    batch_3_logged = now - timedelta(hours=1, minutes=10)
    batch_3_expires = batch_3_logged + timedelta(hours=SHELF_LIFE_HOURS["Rotis/Dry"])

    # Batch 4 (Claimed demo batch)
    batch_4_logged = now - timedelta(hours=1, minutes=45)
    batch_4_expires = batch_4_logged + timedelta(hours=SHELF_LIFE_HOURS["Rice/Grains"])

    batches = [
        {
            "id": "SUR-101",
            "food_items": "Paneer Lababdar & Rich Gravy",
            "category": "Dairy/Curry",
            "weight_kg": 14.5,
            "logged_at": batch_1_logged.isoformat(),
            "expires_at": batch_1_expires.isoformat(),
            "status": "Available",
            "claimed_by": None,
            "handover_otp": str(random.randint(1000, 9999))
        },
        {
            "id": "SUR-102",
            "food_items": "Jeera Rice & Moong Dal Khichdi",
            "category": "Rice/Grains",
            "weight_kg": 21.0,
            "logged_at": batch_2_logged.isoformat(),
            "expires_at": batch_2_expires.isoformat(),
            "status": "Available",
            "claimed_by": None,
            "handover_otp": str(random.randint(1000, 9999))
        },
        {
            "id": "SUR-103",
            "food_items": "Fresh Whole Wheat Phulkas (120 pcs)",
            "category": "Rotis/Dry",
            "weight_kg": 12.0,
            "logged_at": batch_3_logged.isoformat(),
            "expires_at": batch_3_expires.isoformat(),
            "status": "Available",
            "claimed_by": None,
            "handover_otp": str(random.randint(1000, 9999))
        },
        {
            "id": "SUR-100",
            "food_items": "Veg Pulao & Tomato Dal",
            "category": "Rice/Grains",
            "weight_kg": 18.0,
            "logged_at": batch_4_logged.isoformat(),
            "expires_at": batch_4_expires.isoformat(),
            "status": "Claimed",
            "claimed_by": "Robin Hood Army Pune",
            "handover_otp": "7429"
        }
    ]

    return {
        "hostel_name": "Robin Hood Hostel Mess",
        "capacity": 350,
        "portion_kg": 0.45,  # raw food cooked per student meal
        "meal_portion_serve_kg": 0.40,  # 400g/meal diverted
        "co2_factor_per_kg": 2.5,  # kg CO2e saved per kg food prevented/diverted
        "cost_per_kg_inr": 85,  # INR saved per kg
        "discord_webhook_url": os.getenv("DISCORD_WEBHOOK_URL", ""),
        "current_rsvp": {
            "meal_name": "Dinner",
            "opt_outs": 45,
            "last_updated": now.isoformat()
        },
        "historical_baseline": historical_baseline,
        "batches": batches
    }

def load_data():
    if not os.path.exists(DATA_FILE):
        data = generate_default_data()
        save_data(data)
        return data
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Auto update batch expiry status based on current time
            now = datetime.now()
            modified = False
            for batch in data.get("batches", []):
                if batch["status"] == "Available":
                    try:
                        exp = datetime.fromisoformat(batch["expires_at"])
                        if now > exp:
                            batch["status"] = "Expired"
                            modified = True
                    except Exception:
                        pass
            if modified:
                save_data(data)
            return data
    except Exception as e:
        print(f"Error loading {DATA_FILE}: {e}. Reinitializing.")
        data = generate_default_data()
        save_data(data)
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def calculate_metrics(data):
    capacity = data.get("capacity", 350)
    portion_kg = data.get("portion_kg", 0.45)
    meal_serve_kg = data.get("meal_portion_serve_kg", 0.40)
    co2_factor = data.get("co2_factor_per_kg", 2.5)
    cost_per_kg = data.get("cost_per_kg_inr", 85)

    opt_outs = data.get("current_rsvp", {}).get("opt_outs", 0)
    expected_diners = max(0, capacity - opt_outs)

    std_cook_target_kg = round(capacity * portion_kg, 2)
    optimized_cook_target_kg = round(expected_diners * portion_kg, 2)
    pre_production_saved_kg = round(opt_outs * portion_kg, 2)

    batches = data.get("batches", [])
    
    claimed_surplus_kg = sum(b["weight_kg"] for b in batches if b["status"] == "Claimed")
    available_surplus_kg = sum(b["weight_kg"] for b in batches if b["status"] == "Available")
    expired_surplus_kg = sum(b["weight_kg"] for b in batches if b["status"] == "Expired")
    total_surplus_logged_kg = sum(b["weight_kg"] for b in batches)

    total_diverted_kg = round(claimed_surplus_kg + pre_production_saved_kg, 2)
    meals_diverted = int(round(total_diverted_kg / meal_serve_kg)) if meal_serve_kg > 0 else 0

    surplus_recovery_rate_pct = round((claimed_surplus_kg / total_surplus_logged_kg) * 100, 1) if total_surplus_logged_kg > 0 else 0.0
    pre_meal_waste_cut_pct = round((pre_production_saved_kg / std_cook_target_kg) * 100, 1) if std_cook_target_kg > 0 else 0.0

    co2_saved_kg = round(total_diverted_kg * co2_factor, 1)
    money_saved_inr = round(total_diverted_kg * cost_per_kg)

    # Category breakdown
    category_weights = {"Dairy/Curry": 0.0, "Rice/Grains": 0.0, "Rotis/Dry": 0.0}
    for b in batches:
        cat = b.get("category", "Rice/Grains")
        category_weights[cat] = round(category_weights.get(cat, 0.0) + b.get("weight_kg", 0), 1)

    return {
        "capacity": capacity,
        "opt_outs": opt_outs,
        "expected_diners": expected_diners,
        "std_cook_target_kg": std_cook_target_kg,
        "optimized_cook_target_kg": optimized_cook_target_kg,
        "pre_production_saved_kg": pre_production_saved_kg,
        "claimed_surplus_kg": round(claimed_surplus_kg, 2),
        "available_surplus_kg": round(available_surplus_kg, 2),
        "expired_surplus_kg": round(expired_surplus_kg, 2),
        "total_surplus_logged_kg": round(total_surplus_logged_kg, 2),
        "total_diverted_kg": total_diverted_kg,
        "meals_diverted": meals_diverted,
        "surplus_recovery_rate_pct": surplus_recovery_rate_pct,
        "pre_meal_waste_cut_pct": pre_meal_waste_cut_pct,
        "co2_saved_kg": co2_saved_kg,
        "money_saved_inr": money_saved_inr,
        "category_weights": category_weights
    }

def send_discord_alert(batch, webhook_url):
    if not webhook_url:
        return
    try:
        color = 0x10b981  # Emerald green
        if batch["category"] == "Dairy/Curry":
            color = 0xf59e0b  # Amber
        elif batch["category"] == "Rice/Grains":
            color = 0x06b6d4  # Cyan

        payload = {
            "username": "RePlate Food Rescue Bot",
            "avatar_url": "https://img.icons8.com/fluency/96/vegetarian-food.png",
            "embeds": [
                {
                    "title": f"🚨 NEW SURPLUS BATCH: {batch['food_items']}",
                    "description": f"Fresh surplus logged from **Robin Hood Hostel Mess**. Immediate pickup available for registered NGOs.",
                    "color": color,
                    "fields": [
                        {"name": "Batch ID", "value": f"`{batch['id']}`", "inline": True},
                        {"name": "Category", "value": f"**{batch['category']}**", "inline": True},
                        {"name": "Net Weight", "value": f"**{batch['weight_kg']} kg** (~{int(batch['weight_kg']/0.4)} meals)", "inline": True},
                        {"name": "Shelf Life Safe Until", "value": f"{batch['expires_at'][:19].replace('T', ' ')}", "inline": False},
                        {"name": "Pickup Location", "value": "Robin Hood Hostel Mess Backgate (Loading Bay 2)", "inline": False}
                    ],
                    "footer": {
                        "text": "RePlate — Smart Campus Mess Surplus Router"
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        }
        requests.post(webhook_url, json=payload, timeout=3)
    except Exception as e:
        print(f"Discord webhook trigger notice: {e}")

# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state", methods=["GET"])
def get_state():
    data = load_data()
    metrics = calculate_metrics(data)
    return jsonify({
        "status": "success",
        "hostel_name": data.get("hostel_name", "Robin Hood Hostel Mess"),
        "capacity": data.get("capacity", 350),
        "current_rsvp": data.get("current_rsvp", {}),
        "batches": data.get("batches", []),
        "historical_baseline": data.get("historical_baseline", []),
        "metrics": metrics,
        "discord_configured": bool(data.get("discord_webhook_url"))
    })

@app.route("/api/student-rsvp", methods=["POST"])
def update_student_rsvp():
    data = load_data()
    req_json = request.get_json(silent=True) or {}
    
    if "opt_outs" in req_json:
        opt_outs = int(req_json.get("opt_outs", 0))
    elif "delta" in req_json:
        current = data.get("current_rsvp", {}).get("opt_outs", 0)
        opt_outs = current + int(req_json.get("delta", 0))
    else:
        return jsonify({"status": "error", "message": "Missing opt_outs or delta parameter"}), 400

    capacity = data.get("capacity", 350)
    opt_outs = max(0, min(capacity, opt_outs))

    data["current_rsvp"]["opt_outs"] = opt_outs
    data["current_rsvp"]["last_updated"] = datetime.now().isoformat()
    save_data(data)

    metrics = calculate_metrics(data)
    return jsonify({
        "status": "success",
        "message": f"Updated RSVP: {opt_outs} students opting out",
        "current_rsvp": data["current_rsvp"],
        "metrics": metrics
    })

@app.route("/api/log-surplus", methods=["POST"])
def log_surplus():
    data = load_data()
    req_json = request.get_json(silent=True) or {}

    food_items = req_json.get("food_items", "").strip()
    category = req_json.get("category", "Rice/Grains").strip()
    try:
        weight_kg = round(float(req_json.get("weight_kg", 0)), 1)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid weight_kg"}), 400

    if not food_items:
        return jsonify({"status": "error", "message": "Food items description is required"}), 400
    if weight_kg <= 0:
        return jsonify({"status": "error", "message": "Weight must be greater than 0 kg"}), 400
    if category not in SHELF_LIFE_HOURS:
        category = "Rice/Grains"

    shelf_life = SHELF_LIFE_HOURS[category]
    now = datetime.now()
    expires_at = now + timedelta(hours=shelf_life)
    batch_id = f"SUR-{random.randint(100, 999)}"
    otp = str(random.randint(1000, 9999))

    new_batch = {
        "id": batch_id,
        "food_items": food_items,
        "category": category,
        "weight_kg": weight_kg,
        "logged_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "Available",
        "claimed_by": None,
        "handover_otp": otp
    }

    data.setdefault("batches", []).insert(0, new_batch)
    save_data(data)

    # Optional Discord notification
    webhook_url = data.get("discord_webhook_url") or os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        send_discord_alert(new_batch, webhook_url)

    metrics = calculate_metrics(data)
    return jsonify({
        "status": "success",
        "message": f"Logged batch {batch_id} successfully",
        "batch": new_batch,
        "batches": data["batches"],
        "metrics": metrics
    })

@app.route("/api/simulate-surplus", methods=["POST"])
def simulate_surplus():
    sample = random.choice(SAMPLE_DISHES)
    data = load_data()

    category = sample["category"]
    shelf_life = SHELF_LIFE_HOURS[category]
    now = datetime.now()
    expires_at = now + timedelta(hours=shelf_life)
    batch_id = f"SUR-{random.randint(100, 999)}"
    otp = str(random.randint(1000, 9999))
    weight = round(sample["weight"] + random.uniform(-2.5, 3.5), 1)

    new_batch = {
        "id": batch_id,
        "food_items": sample["name"],
        "category": category,
        "weight_kg": max(5.0, weight),
        "logged_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status": "Available",
        "claimed_by": None,
        "handover_otp": otp
    }

    data.setdefault("batches", []).insert(0, new_batch)
    save_data(data)

    metrics = calculate_metrics(data)
    return jsonify({
        "status": "success",
        "message": f"Simulated surplus tray: {new_batch['food_items']} ({new_batch['weight_kg']} kg)",
        "batch": new_batch,
        "batches": data["batches"],
        "metrics": metrics
    })

@app.route("/api/claim-surplus", methods=["POST"])
def claim_surplus():
    data = load_data()
    req_json = request.get_json(silent=True) or {}

    batch_id = req_json.get("id")
    ngo_name = req_json.get("ngo_name", "Robin Hood Army Pune").strip()

    if not batch_id:
        return jsonify({"status": "error", "message": "Batch id is required"}), 400

    target = None
    for batch in data.get("batches", []):
        if batch["id"] == batch_id:
            target = batch
            break

    if not target:
        return jsonify({"status": "error", "message": f"Batch {batch_id} not found"}), 404

    if target["status"] == "Claimed":
        return jsonify({
            "status": "info",
            "message": f"Batch already claimed by {target['claimed_by']}",
            "handover_otp": target["handover_otp"],
            "batch": target
        })

    if target["status"] == "Expired":
        return jsonify({"status": "error", "message": "Batch has expired and cannot be safely claimed"}), 400

    target["status"] = "Claimed"
    target["claimed_by"] = ngo_name or "Robin Hood Army Pune"
    save_data(data)

    metrics = calculate_metrics(data)
    return jsonify({
        "status": "success",
        "message": f"Batch {batch_id} successfully claimed by {target['claimed_by']}",
        "handover_otp": target["handover_otp"],
        "batch": target,
        "batches": data["batches"],
        "metrics": metrics
    })

@app.route("/api/update-config", methods=["POST"])
def update_config():
    data = load_data()
    req_json = request.get_json(silent=True) or {}
    webhook_url = req_json.get("discord_webhook_url", "").strip()
    data["discord_webhook_url"] = webhook_url
    save_data(data)
    return jsonify({"status": "success", "message": "Config updated successfully", "discord_configured": bool(webhook_url)})

@app.route("/api/reset-demo", methods=["POST"])
def reset_demo():
    data = generate_default_data()
    save_data(data)
    metrics = calculate_metrics(data)
    return jsonify({
        "status": "success",
        "message": "Demo data reset to clean initial state",
        "batches": data["batches"],
        "current_rsvp": data["current_rsvp"],
        "historical_baseline": data["historical_baseline"],
        "metrics": metrics
    })

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 RePlate — Smart Campus Mess Surplus Router")
    print("   Serving on http://127.0.0.1:5001")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5001)
