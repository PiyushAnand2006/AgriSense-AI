"""Idempotent reference + demo data seeding.

Market prices are deterministic *per calendar date*, so the same day always
produces the same price no matter when the database was seeded. On every
startup the series is simply extended up to today.
"""

import math
import os
import random
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.analysis import HealthRecord
from app.models.crop import Crop, FarmerCrop
from app.models.listing import CropListing
from app.models.market import Market, MarketPrice
from app.models.user import FarmerProfile, Notification, User

EPOCH = date(2026, 1, 1)  # fixed origin so date -> price is deterministic
PRICE_HISTORY_DAYS = 120

CROPS: list[dict] = [
    # --- RABI CROPS (Winter / Spring) ---
    {
        "id": "wheat", "name": "Wheat", "season": "RABI",
        "scientific_name": "Triticum aestivum",
        "description": "The staple winter cereal of the Rabi season, sown October–November and harvested March–April.",
        "growing_period_days": 150, "sowing_window": "Oct–Nov", "harvest_window": "Mar–Apr",
    },
    {
        "id": "chickpea", "name": "Chickpea / Gram", "season": "RABI",
        "scientific_name": "Cicer arietinum",
        "description": "Primary winter pulse crop; gram is valued for protein and commands steady mandi demand.",
        "growing_period_days": 120, "sowing_window": "Oct–Nov", "harvest_window": "Feb–Mar",
    },
    {
        "id": "mustard", "name": "Mustard", "season": "RABI",
        "scientific_name": "Brassica juncea",
        "description": "Winter oilseed crop; seeds are crushed for edible oil and demand rises before festivals.",
        "growing_period_days": 135, "sowing_window": "Oct–Nov", "harvest_window": "Feb–Mar",
    },
    {
        "id": "potato", "name": "Potato", "season": "RABI",
        "scientific_name": "Solanum tuberosum",
        "description": "High-yield Rabi vegetable; cold storage decisions make it very price-sensitive.",
        "growing_period_days": 100, "sowing_window": "Oct–Nov", "harvest_window": "Jan–Feb",
    },
    {
        "id": "lentil", "name": "Lentil / Masoor", "season": "RABI",
        "scientific_name": "Lens culinaris",
        "description": "Valuable Rabi pulse grown across northern and central plains; thrives in cool weather with low moisture.",
        "growing_period_days": 120, "sowing_window": "Oct–Nov", "harvest_window": "Feb–Mar",
    },
    {
        "id": "apple", "name": "Apple", "season": "RABI",
        "scientific_name": "Malus domestica",
        "description": "Temperate fruit crop requiring winter chilling; primary fruit cash crop in hill regions.",
        "growing_period_days": 165, "sowing_window": "Dec–Feb", "harvest_window": "Jul–Sep",
    },
    # --- KHARIF CROPS (Monsoon / Autumn) ---
    {
        "id": "rice", "name": "Rice / Paddy", "season": "KHARIF",
        "scientific_name": "Oryza sativa",
        "description": "The primary staple kharif grain in India, requiring abundant water, warm temperatures, and humid monsoon climate.",
        "growing_period_days": 135, "sowing_window": "Jun–Jul", "harvest_window": "Oct–Nov",
    },
    {
        "id": "maize", "name": "Maize / Makka", "season": "KHARIF",
        "scientific_name": "Zea mays",
        "description": "High-yield kharif cereal and feed crop; highly responsive to nitrogen and warm monsoon sunshine.",
        "growing_period_days": 100, "sowing_window": "Jun–Jul", "harvest_window": "Sep–Oct",
    },
    {
        "id": "cotton", "name": "Cotton / Kapas", "season": "KHARIF",
        "scientific_name": "Gossypium hirsutum",
        "description": "Leading commercial fiber crop grown extensively in black cotton soils during monsoon.",
        "growing_period_days": 165, "sowing_window": "May–Jun", "harvest_window": "Nov–Jan",
    },
    {
        "id": "jute", "name": "Jute / Patson", "season": "KHARIF",
        "scientific_name": "Corchorus olitorius",
        "description": "Golden natural fiber crop thriving in humid monsoon alluvial river plains.",
        "growing_period_days": 135, "sowing_window": "Mar–May", "harvest_window": "Jul–Sep",
    },
    {
        "id": "pigeonpeas", "name": "Pigeonpeas / Arhar / Tur", "season": "KHARIF",
        "scientific_name": "Cajanus cajan",
        "description": "Major monsoon legume providing protein-rich dal; deep taproots offer high drought resilience.",
        "growing_period_days": 165, "sowing_window": "Jun–Jul", "harvest_window": "Nov–Dec",
    },
    {
        "id": "blackgram", "name": "Black Gram / Urad", "season": "KHARIF",
        "scientific_name": "Vigna mungo",
        "description": "Short-duration kharif pulse; excellent for soil fertility restoration and intercropping.",
        "growing_period_days": 80, "sowing_window": "Jun–Jul", "harvest_window": "Sep–Oct",
    },
    {
        "id": "mothbeans", "name": "Moth Beans / Matki", "season": "KHARIF",
        "scientific_name": "Vigna aconitifolia",
        "description": "Exceptionally drought-hardy arid legume grown in low rainfall arid tracts during monsoon.",
        "growing_period_days": 70, "sowing_window": "Jul–Aug", "harvest_window": "Sep–Oct",
    },
    # --- ZAID CROPS (Summer) ---
    {
        "id": "watermelon", "name": "Watermelon", "season": "ZAID",
        "scientific_name": "Citrullus lanatus",
        "description": "Classic Zaid summer crop with high water demand and quick market turnover.",
        "growing_period_days": 90, "sowing_window": "Feb–Mar", "harvest_window": "May–Jun",
    },
    {
        "id": "cucumber", "name": "Cucumber", "season": "ZAID",
        "scientific_name": "Cucumis sativus",
        "description": "Short-duration summer vegetable suited to Zaid season irrigation.",
        "growing_period_days": 70, "sowing_window": "Feb–Mar", "harvest_window": "Apr–May",
    },
    {
        "id": "muskmelon", "name": "Muskmelon", "season": "ZAID",
        "scientific_name": "Cucumis melo",
        "description": "Sweet summer melon; quality grading strongly affects its market price.",
        "growing_period_days": 90, "sowing_window": "Feb–Mar", "harvest_window": "May–Jun",
    },
    {
        "id": "moong", "name": "Moong / Green Gram", "season": "ZAID",
        "scientific_name": "Vigna radiata",
        "description": "Summer pulse that fixes nitrogen and fits the short Zaid window.",
        "growing_period_days": 75, "sowing_window": "Mar–Apr", "harvest_window": "Jun",
    },
    {
        "id": "banana", "name": "Banana", "season": "ZAID",
        "scientific_name": "Musa acuminata",
        "description": "Year-round commercial fruit crop requiring abundant irrigation and rich nutrients.",
        "growing_period_days": 330, "sowing_window": "Feb–May", "harvest_window": "Year-round",
    },
    {
        "id": "mango", "name": "Mango", "season": "ZAID",
        "scientific_name": "Mangifera indica",
        "description": "The king of Indian fruits; summer harvest with high commercial and export value.",
        "growing_period_days": 120, "sowing_window": "Jul–Aug", "harvest_window": "Apr–Jul",
    },
    {
        "id": "papaya", "name": "Papaya", "season": "ZAID",
        "scientific_name": "Carica papaya",
        "description": "Fast-growing tropical fruit with year-round continuous fruiting after 9 months.",
        "growing_period_days": 270, "sowing_window": "Feb–Apr", "harvest_window": "Nov–Mar",
    },
    {
        "id": "pomegranate", "name": "Pomegranate / Anar", "season": "ZAID",
        "scientific_name": "Punica granatum",
        "description": "High-value semi-arid fruit with excellent drought tolerance and steady market demand.",
        "growing_period_days": 180, "sowing_window": "Jan–Feb", "harvest_window": "Jul–Sep",
    },
    {
        "id": "orange", "name": "Orange / Citrus", "season": "ZAID",
        "scientific_name": "Citrus sinensis",
        "description": "Commercial citrus fruit popular in central and western sub-tropical tracts.",
        "growing_period_days": 240, "sowing_window": "Jun–Aug", "harvest_window": "Dec–Feb",
    },
    {
        "id": "grapes", "name": "Grapes", "season": "ZAID",
        "scientific_name": "Vitis vinifera",
        "description": "High-return commercial horticultural crop grown on trellis systems in semi-arid zones.",
        "growing_period_days": 135, "sowing_window": "Oct–Nov", "harvest_window": "Mar–Apr",
    },
    {
        "id": "coconut", "name": "Coconut", "season": "ZAID",
        "scientific_name": "Cocos nucifera",
        "description": "Coastal plantation crop yielding nuts, oil, and copra year-round.",
        "growing_period_days": 365, "sowing_window": "May–Jun", "harvest_window": "Year-round",
    },
    {
        "id": "coffee", "name": "Coffee", "season": "ZAID",
        "scientific_name": "Coffea arabica",
        "description": "Shade-grown plantation crop in southern hill tracts with high export value.",
        "growing_period_days": 240, "sowing_window": "Jun–Aug", "harvest_window": "Nov–Jan",
    },
]

MARKETS: list[dict] = [
    {"id": "delhi-azadpur", "name": "Azadpur Mandi", "city": "Delhi", "state": "Delhi"},
    {"id": "mumbai-vasai", "name": "Vasai Market", "city": "Mumbai", "state": "Maharashtra"},
    {"id": "pune-yard", "name": "Market Yard", "city": "Pune", "state": "Maharashtra"},
    {"id": "kanpur-mandi", "name": "Kanpur Mandi", "city": "Kanpur", "state": "Uttar Pradesh"},
    {"id": "jaipur-mandi", "name": "Jaipur Grain Market", "city": "Jaipur", "state": "Rajasthan"},
    {"id": "lucknow-mandi", "name": "Lucknow Mandi", "city": "Lucknow", "state": "Uttar Pradesh"},
    {"id": "indore-mandi", "name": "Indore Mandi", "city": "Indore", "state": "Madhya Pradesh"},
    {"id": "ahmedabad-mandi", "name": "Ahmedabad Market", "city": "Ahmedabad", "state": "Gujarat"},
]

BASE_PRICES = {
    "wheat": 2400, "chickpea": 5200, "mustard": 5400, "potato": 1250,
    "lentil": 6200, "apple": 8500,
    "rice": 2300, "maize": 2150, "cotton": 6800, "jute": 5100,
    "pigeonpeas": 7100, "blackgram": 6900, "mothbeans": 5800,
    "watermelon": 1500, "cucumber": 2000, "muskmelon": 2500, "moong": 7400,
    "banana": 2800, "mango": 4500, "papaya": 2200, "pomegranate": 7500,
    "orange": 4200, "grapes": 5500, "coconut": 3200, "coffee": 18500,
}

DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@agrisense.ai")
# Demo account credential is public by design (documented in README);
# deployments can override or unset it to disable the demo user.
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Demo@1234")


def _market_factor(crop_id: str, market_id: str) -> float:
    rng = random.Random(f"factor:{crop_id}:{market_id}")
    return 0.94 + rng.random() * 0.14


def _price_for(crop_id: str, market_id: str, day: date) -> tuple[float, float, float]:
    """Deterministic (min, modal, max) prices in INR/quintal for one day."""
    base = BASE_PRICES[crop_id] * _market_factor(crop_id, market_id)
    i = (day - EPOCH).days
    rng = random.Random(f"price:{crop_id}:{market_id}:{day}")
    trend = 0.00012 * i * math.sin(i / 97.0)          # slow channel drift
    seasonal = 0.035 * math.sin((i / 365) * 2 * math.pi * 6)  # ~2 month cycle
    noise = rng.gauss(0, 0.012)
    factor = 1.0 + trend + seasonal + noise
    factor = max(0.82, min(1.22, factor))
    modal = round(base * factor, 1)
    rng = random.Random(f"range:{crop_id}:{market_id}:{day}")
    low = round(modal * (0.94 + rng.random() * 0.03), 1)
    high = round(modal * (1.03 + rng.random() * 0.03), 1)
    return low, modal, high


def _seed_prices(db: Session, crop_ids: list[str], market_ids: list[str]) -> None:
    today = date.today()
    start = today - timedelta(days=PRICE_HISTORY_DAYS - 1)

    for crop_id in crop_ids:
        for market_id in market_ids:
            latest = db.scalar(
                select(func.max(MarketPrice.price_date)).where(
                    MarketPrice.crop_id == crop_id, MarketPrice.market_id == market_id
                )
            )
            first_day = max(start, (latest + timedelta(days=1)) if latest else start)
            if first_day > today:
                continue
            rows = []
            for offset in range((today - first_day).days + 1):
                day = first_day + timedelta(days=offset)
                low, modal, high = _price_for(crop_id, market_id, day)
                rows.append(
                    MarketPrice(
                        crop_id=crop_id,
                        market_id=market_id,
                        price_date=day,
                        min_price=low,
                        modal_price=modal,
                        max_price=high,
                    )
                )
            db.add_all(rows)
    db.commit()


def _seed_demo_user(db: Session) -> None:
    existing = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if existing:
        return

    demo = User(
        email=DEMO_EMAIL,
        name="Demo Farmer",
        hashed_password=hash_password(DEMO_PASSWORD),
        profile=FarmerProfile(
            village="Baragaon", district="Varanasi", state="Uttar Pradesh",
            language="en", farm_size_acres=4.5,
        ),
    )
    db.add(demo)
    db.flush()

    today = date.today()
    db.add_all(
        [
            FarmerCrop(
                user_id=demo.id, crop_id="wheat", season="RABI",
                planting_date=today - timedelta(days=45),
                expected_harvest_date=today + timedelta(days=55),
                farm_size=2.5, location="Baragaon, Varanasi", status="ACTIVE",
            ),
            FarmerCrop(
                user_id=demo.id, crop_id="rice", season="KHARIF",
                planting_date=today - timedelta(days=35),
                expected_harvest_date=today + timedelta(days=80),
                farm_size=2.0, location="Baragaon, Varanasi", status="ACTIVE",
            ),
            FarmerCrop(
                user_id=demo.id, crop_id="potato", season="RABI",
                planting_date=today - timedelta(days=60),
                expected_harvest_date=today + timedelta(days=20),
                farm_size=1.5, location="Baragaon, Varanasi", status="ACTIVE",
            ),
            HealthRecord(
                user_id=demo.id, crop_id="wheat", record_type="DISEASE",
                name="Leaf Rust", severity="MODERATE",
                notes="Orange-brown pustules on lower leaves, logged during scouting.",
                created_at=datetime.combine(today - timedelta(days=8), datetime.min.time()),
            ),
            HealthRecord(
                user_id=demo.id, crop_id="wheat", record_type="PEST",
                name="Aphid", severity="LOW",
                notes="Small clusters on young shoots; monitoring.",
                created_at=datetime.combine(today - timedelta(days=3), datetime.min.time()),
            ),
        ]
    )

    db.add_all(
        [
            Notification(
                user_id=demo.id, type="SYSTEM",
                title="Welcome to AgriSense AI",
                message="Your demo account is ready. Explore crop analysis, market intelligence and sell/hold advice.",
            ),
            Notification(
                user_id=demo.id, type="MARKET",
                title="Wheat price moved",
                message="Wheat at Azadpur Mandi changed noticeably this week — review the Market page.",
            ),
            Notification(
                user_id=demo.id, type="WEATHER",
                title="Weather watch",
                message="Rain probability is elevated in the next few days. Plan spraying accordingly.",
            ),
        ]
    )

    other_listings = [
        ("f1000a", "Ramesh Patel", "mustard", 40, 5350, "A", "Jaipur, Rajasthan"),
        ("f1000b", "Sunita Devi", "chickpea", 25, 5150, "B", "Kanpur, Uttar Pradesh"),
        ("f1000c", "Vijay Kumar", "moong", 30, 7300, "A", "Indore, Madhya Pradesh"),
        ("f1000d", "Meera Singh", "watermelon", 120, 1450, "B", "Lucknow, Uttar Pradesh"),
        ("f1000e", "Arjun Reddy", "muskmelon", 80, 2600, "A", "Pune, Maharashtra"),
        ("f1000f", "Kisan Yadav", "potato", 200, 1200, "C", "Agra, Uttar Pradesh"),
        ("f1000g", "Gurpreet Singh", "rice", 150, 2350, "A", "Karnal, Haryana"),
        ("f1000h", "Balwinder Kaur", "maize", 90, 2180, "B", "Ludhiana, Punjab"),
        ("f1000i", "Devendra Sharma", "cotton", 45, 6950, "A", "Rajkot, Gujarat"),
    ]
    for farmer_id, farmer_name, crop_id, qty, price, grade, location in other_listings:
        db.add(
            CropListing(
                farmer_id=farmer_id, farmer_name=farmer_name, crop_id=crop_id,
                quantity=qty, unit="quintal", asking_price=price,
                quality_grade=grade, location=location, status="ACTIVE",
            )
        )
    db.add(
        CropListing(
            farmer_id=demo.id, farmer_name=demo.name, crop_id="wheat",
            quantity=60, unit="quintal", asking_price=2480,
            quality_grade="A", location="Baragaon, Varanasi", status="ACTIVE",
        )
    )
    db.commit()


def seed(db: Session) -> None:
    existing_crop_ids = set(db.scalars(select(Crop.id)).all())
    new_crops = [Crop(**crop) for crop in CROPS if crop["id"] not in existing_crop_ids]
    if new_crops:
        db.add_all(new_crops)
        db.commit()

    existing_market_ids = set(db.scalars(select(Market.id)).all())
    new_markets = [Market(**market) for market in MARKETS if market["id"] not in existing_market_ids]
    if new_markets:
        db.add_all(new_markets)
        db.commit()

    crop_ids = [c.id for c in db.scalars(select(Crop))]
    market_ids = [m.id for m in db.scalars(select(Market))]
    _seed_prices(db, crop_ids, market_ids)
    _seed_demo_user(db)
