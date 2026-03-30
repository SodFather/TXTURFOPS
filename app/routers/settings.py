from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.price_tier import PriceTier

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/pricing")
async def pricing_page(request: Request, db: Session = Depends(get_db)):
    tiers = db.query(PriceTier).order_by(PriceTier.service_type, PriceTier.min_sqft).all()
    # Group by service type
    grouped = {}
    for t in tiers:
        grouped.setdefault(t.service_type, []).append(t)

    return request.app.state.templates.TemplateResponse(
        request, "settings/pricing.html", {"grouped_tiers": grouped},
    )


@router.post("/pricing")
async def update_pricing(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    for key, value in form.items():
        if key.startswith("price_"):
            tier_id = int(key.replace("price_", ""))
            tier = db.query(PriceTier).get(tier_id)
            if tier:
                tier.price = float(value or 0)
    db.commit()
    request.session["flash"] = "Pricing updated."
    return RedirectResponse(url="/settings/pricing", status_code=303)
