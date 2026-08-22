"""Farmer assistant service.

Two interchangeable response providers behind one chat contract:

* **rule-based** (default) — deterministic replies grounded in the actual
  database state (prices, seasons, weather)
* **external API** — when ``ASSISTANT_API_URL`` is configured, requests are
  forwarded to the external conversational API from the backend only

Both persist conversations and messages the same way.
"""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import HealthRecord
from app.models.crop import Crop
from app.models.user import AssistantConversation, AssistantMessage, User

logger = logging.getLogger("agrisense.assistant")

GREETING = (
    "Namaste! I am your AgriSense assistant. I can discuss crop diseases and pests, "
    "market prices, sell/hold decisions, weather and season planning. How can I help?"
)

CAPABILITIES = (
    "I can help you with:\n"
    "- **Crop health**: browse common diseases and pests on the Health page\n"
    "- **Market prices**: ask *\"wheat price today\"* for current mandi rates\n"
    "- **Sell or hold**: ask *\"should I sell my wheat\"* for the rule-based decision check\n"
    "- **Weather**: ask *\"weather this week\"* for the forecast\n"
    "- **Season planning**: ask *\"crops for rabi\"* for season suggestions\n\n"
    "Note: I provide educational support, not expert advice."
)


def _market_reply(db: Session, crop_hint: str | None) -> str:
    from app.services.market_service import latest_per_combo

    combos = latest_per_combo(db)
    if crop_hint:
        matching = [
            (p, c, m) for p, c, m in combos
            if crop_hint in c.name.lower() or crop_hint in c.id.lower()
        ]
        if matching:
            lines = [f"**Market prices for {matching[0][1].name}:**"]
            for price, crop, market in matching[:4]:
                lines.append(
                    f"- {market.name}: ₹{price.modal_price:,.0f}/quintal ({price.price_date:%d %b})"
                )
            lines.append("\n_Open the Market page for trends and history._")
            return "\n".join(lines)
    top = combos[:5]
    lines = ["**Market prices right now:**"]
    for price, crop, market in top:
        lines.append(f"- {crop.name} @ {market.name}: ₹{price.modal_price:,.0f}/quintal")
    lines.append("\n_Mention a crop name for specific rates._")
    return "\n".join(lines)


async def _weather_reply() -> str:
    from app.services.weather_service import get_weather

    weather = await get_weather()
    t = weather.today
    return (
        f"**Weather for {weather.location}:** {t.condition}, {t.temperature_c}°C, "
        f"humidity {t.humidity_pct:.0f}%, rain chance {t.rain_probability:.0f}%, "
        f"wind {t.wind_kph} km/h.\n\n"
        + (
            "⚠️ " + weather.alerts[0].title + " — " + weather.alerts[0].message + "\n\n"
            if weather.alerts else ""
        )
        + (f"_Source: {weather.source}._")
    )


async def _rule_based_reply(db: Session, user: User, message: str) -> str:
    from app.services.knowledge import CROP_DISEASES, CROP_PESTS

    text = message.lower()

    if any(w in text for w in ("hello", "hi ", "namaste", "hey")) and len(text) < 25:
        return GREETING
    if any(w in text for w in ("help", "what can you", "capabilities")):
        return CAPABILITIES
    if "weather" in text or "rain" in text:
        return await _weather_reply()
    if "sell" in text or "hold" in text:
        crop_hint = next(
            (c for c in ("wheat", "chickpea", "gram", "mustard", "potato",
                         "watermelon", "cucumber", "muskmelon", "moong") if c in text),
            None,
        )
        crop_id = crop_hint or "wheat"
        from app.services.market_service import latest_per_combo

        price_row = next(
            ((p, c, m) for p, c, m in latest_per_combo(db) if c.id == crop_id), None
        )
        if price_row:
            price, crop, market_obj = price_row
            return (
                f"For **{crop.name}** at {market_obj.name}: current price is "
                f"₹{price.modal_price:,.0f}/quintal. I can't make the final call for you, but open the "
                f"**Sell/Hold** page and enter your quantity and storage plans — the rule-based engine "
                f"will weigh the recorded trend against storage cost for you.\n\n"
                "_Decision-support rule, not financial advice._"
            )
        return "Tell me which crop you're considering, e.g. *\"should I sell my wheat?\"*"
    if "price" in text or "rate" in text or "mandi" in text or "market" in text:
        crop_hint = next(
            (c for c in ("wheat", "chickpea", "gram", "mustard", "potato",
                         "watermelon", "cucumber", "muskmelon", "moong") if c in text),
            None,
        )
        return _market_reply(db, crop_hint)
    if "rabi" in text or "zaid" in text or "season" in text or "sow" in text or "plant" in text:
        season = "RABI" if "zaid" not in text else "ZAID"
        crops = db.scalars(select(Crop).where(Crop.season == season)).all()
        names = ", ".join(c.name for c in crops)
        return (
            f"**{season.title()} season crops** supported in AgriSense: {names}.\n\n"
            f"{'Winter-sown (Oct–Mar), harvested in spring.' if season == 'RABI' else 'Summer-sown (Mar–Jun), short-season crops with irrigation.'}\n"
            "_Educational planning guidance._"
        )
    if "disease" in text or "pest" in text or "rust" in text or "blight" in text or "yellow" in text:
        latest_record = (
            db.scalars(
                select(HealthRecord)
                .where(HealthRecord.user_id == user.id)
                .order_by(HealthRecord.created_at.desc())
            )
            .first()
        )
        if latest_record:
            return (
                f"Your latest logged observation records **{latest_record.name}** "
                f"(severity {latest_record.severity.lower()}). Open the Health page to review symptoms "
                f"and educational treatment guidance.\n\n"
                "_Educational information — not verified agricultural advice._"
            )
        crop_hint = next((c for c in CROP_DISEASES if c in text), None)
        if crop_hint:
            diseases = ", ".join(CROP_DISEASES[crop_hint])
            pests = ", ".join(CROP_PESTS.get(crop_hint, []))
            return (
                f"Common concerns for **{crop_hint}** — diseases: {diseases}; pests: {pests}. "
                "Open the Health page for symptoms and educational management guidance."
            )
        return (
            "Browse common diseases and pests on the **Health page** — pick a crop to see what to "
            "watch for, with symptoms and educational management guidance."
        )
    return (
        "I answer best on: crop health, market prices, sell/hold timing, weather and season "
        "planning. Try asking *\"wheat price today\"* or *\"crops for rabi\"*."
    )


async def _external_reply(message: str, history: list[dict[str, str]]) -> str | None:
    from app.external.assistant_client import get_assistant_client

    client = get_assistant_client()
    if not client.configured:
        return None
    try:
        return await client.chat(message, history)
    except Exception as exc:  # noqa: BLE001 — provider failure falls back to rules
        logger.warning("external assistant failed, using rule-based reply: %s", exc)
        return None


async def chat(db: Session, user: User, message: str, conversation_id: str | None) -> tuple[str, str, AssistantMessage]:
    """Returns (conversation_id, status, reply_message).

    status: "RULE_BASED" | "EXTERNAL_API" | "EXTERNAL_API_FALLBACK"
    """
    if conversation_id:
        conversation = db.get(AssistantConversation, conversation_id)
        if conversation is None or conversation.user_id != user.id:
            conversation_id = None
    if not conversation_id:
        conversation = AssistantConversation(
            user_id=user.id, title=message[:60] + ("…" if len(message) > 60 else "")
        )
        db.add(conversation)
        db.commit()

    db.add(AssistantMessage(conversation_id=conversation.id, role="user", content=message))

    history = [
        {"role": m.role, "content": m.content}
        for m in db.scalars(
            select(AssistantMessage)
            .where(AssistantMessage.conversation_id == conversation.id)
            .order_by(AssistantMessage.id.desc())
            .limit(8)
        )
    ][::-1]

    status = "RULE_BASED"
    reply_text = await _external_reply(message, history)
    if reply_text:
        status = "EXTERNAL_API"
    else:
        reply_text = await _rule_based_reply(db, user, message)

    reply = AssistantMessage(conversation_id=conversation.id, role="assistant", content=reply_text)
    db.add(reply)
    db.commit()

    return conversation.id, status, reply
