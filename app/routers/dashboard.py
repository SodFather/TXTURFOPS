from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.customer import Customer, CustomerStatus

router = APIRouter()


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    total = db.query(func.count(Customer.id)).scalar() or 0
    active = (
        db.query(func.count(Customer.id))
        .filter(Customer.status == CustomerStatus.ACTIVE.value)
        .scalar()
        or 0
    )
    leads = (
        db.query(func.count(Customer.id))
        .filter(Customer.status == CustomerStatus.LEAD.value)
        .scalar()
        or 0
    )
    quoted = (
        db.query(func.count(Customer.id))
        .filter(Customer.status == CustomerStatus.QUOTED.value)
        .scalar()
        or 0
    )

    # Revenue totals
    total_revenue = (
        db.query(func.coalesce(func.sum(Customer.lifetime_revenue), 0.0)).scalar()
    )

    # Customers by zone
    zones = (
        db.query(Customer.service_zone, func.count(Customer.id))
        .filter(Customer.service_zone.isnot(None), Customer.service_zone != "")
        .group_by(Customer.service_zone)
        .all()
    )

    # Recently added
    recent = db.query(Customer).order_by(Customer.created_at.desc()).limit(5).all()

    # Active customers needing follow-up (no service in 60+ days or never serviced)
    cutoff = datetime.now(timezone.utc) - timedelta(days=60)
    followup = (
        db.query(Customer)
        .filter(
            Customer.status == CustomerStatus.ACTIVE.value,
            (Customer.last_service_date < cutoff) | (Customer.last_service_date.is_(None)),
        )
        .order_by(Customer.last_service_date.asc().nullsfirst())
        .limit(10)
        .all()
    )

    return request.app.state.templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total_customers": total,
            "active_customers": active,
            "pending_leads": leads,
            "quoted_customers": quoted,
            "total_revenue": total_revenue,
            "zones": zones,
            "recent_customers": recent,
            "followup_customers": followup,
        },
    )
