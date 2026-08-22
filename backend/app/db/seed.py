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
    "watermelon": 1500, "cucumber": 2000, "muskmelon": 2500, "moong": 7400,
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
    if db.scalar(select(Crop).limit(1)) is None:
        db.add_all([Crop(**crop) for crop in CROPS])
        db.commit()
    if db.scalar(select(Market).limit(1)) is None:
        db.add_all([Market(**market) for market in MARKETS])
        db.commit()

    crop_ids = [c.id for c in db.scalars(select(Crop))]
    market_ids = [m.id for m in db.scalars(select(Market))]
    _seed_prices(db, crop_ids, market_ids)
    _seed_demo_user(db)
