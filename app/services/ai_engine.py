import os
import json
import logging
import httpx

log = logging.getLogger(__name__)

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"

# Central TX turf calendar context for AI prompts
TURF_CALENDAR = """Central Texas (Austin/Lakeway area) turf care calendar:
- Pre-emergent Round 1: Late Jan-Feb (Barricade, Dimension)
- Pre-emergent Round 2: Late Mar-Apr
- Fertilization: Mar-May, Sep-Oct
- Post-emergent weed control: Mar-Nov (Celsius, MSM Turf, Certainty, Tribute Total)
- Grub preventive: May-Jun (Merit/Imidacloprid)
- Pest control: Year-round, peak Apr-Oct (Bifenthrin)
- Winterizer: Nov-Dec
- Irrigation: Year-round, critical Jun-Sep
Common turf: Bermuda, St. Augustine, Zoysia. Soil: limestone/alkaline clay."""


async def generate_content(prompt: str, system: str = None, max_tokens: int = 1024) -> str | None:
    """Call Claude API to generate content. Returns text or None on failure."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None

    messages = [{"role": "user", "content": prompt}]
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        body["system"] = system

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                CLAUDE_API_URL,
                json=body,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                timeout=30.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["content"][0]["text"]
            log.error("Claude API %s: %s", resp.status_code, resp.text[:300])
    except Exception as exc:
        log.error("Claude API request failed: %s", exc)
    return None


async def generate_post_service_instructions(products: list[str]) -> str:
    """Generate care instructions based on products applied."""
    prompt = f"""Generate brief post-service lawn care instructions for a customer whose lawn was just treated with: {', '.join(products)}.

Include: watering schedule, when it's safe to mow, pet/child safety wait time, and what to expect over the next 1-2 weeks. Keep it friendly and under 150 words."""

    system = f"You are a lawn care expert in the Lakeway, TX area. {TURF_CALENDAR}"
    result = await generate_content(prompt, system, max_tokens=300)
    return result or _default_instructions(products)


async def generate_seasonal_campaign(month: str, customer_name: str, services_missing: list[str]) -> str:
    """Generate a personalized seasonal marketing email."""
    prompt = f"""Write a short, personalized email for a lawn care customer.
Customer: {customer_name}
Month: {month}
Services they haven't scheduled yet: {', '.join(services_missing)}

Be specific about WHY these services matter this month in Central TX. Be friendly but professional. Under 200 words. Include a call to action."""

    system = f"You are Cory from TX TURF PROS, a lawn care professional in Lakeway, TX. {TURF_CALENDAR}"
    return await generate_content(prompt, system, max_tokens=400)


async def generate_business_insight(stats: dict) -> str:
    """Generate an AI business insight based on current stats."""
    prompt = f"""Based on these business stats for TX TURF PROS (lawn care, Lakeway TX):
{json.dumps(stats, indent=2)}

Give one specific, actionable business insight or suggestion. Be concrete with numbers. One paragraph, under 100 words."""

    system = "You are a business advisor for a solo lawn care operator. Focus on revenue growth, efficiency, and customer retention."
    result = await generate_content(prompt, system, max_tokens=200)
    return result or ""


async def generate_weekly_summary(stats: dict) -> str:
    """Generate a weekly business summary."""
    prompt = f"""Write a brief weekly business summary for TX TURF PROS:
{json.dumps(stats, indent=2)}

Include: performance highlights, areas needing attention, and one specific recommendation. Professional but conversational. Under 200 words."""

    system = f"You are a business intelligence assistant for a solo lawn care operation in Lakeway, TX. {TURF_CALENDAR}"
    return await generate_content(prompt, system, max_tokens=400)


def _default_instructions(products: list[str]) -> str:
    """Fallback instructions when AI is unavailable."""
    return (
        "Thank you for choosing TX TURF PROS! Please water your lawn within "
        "24 hours of application. Avoid mowing for 24-48 hours. Keep children "
        "and pets off treated areas until the product has dried completely "
        "(typically 1-2 hours). You may notice some weed yellowing within "
        "7-14 days — this is normal and expected."
    )
