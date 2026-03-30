import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

from ..database import get_db
from ..models.customer import Customer, CustomerStatus
from ..models.invoice import Invoice, InvoiceStatus
from ..models.quote import Quote, QuoteStatus
from ..models.service_visit import ServiceVisit, VisitStatus
from ..services.weather import get_forecast, parse_daily_forecast
from ..services.ai_engine import generate_business_insight

router = APIRouter()


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=now.weekday())

    # Customer stats
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    active_customers = db.query(func.count(Customer.id)).filter(Customer.status == CustomerStatus.ACTIVE.value).scalar() or 0
    pending_leads = db.query(func.count(Customer.id)).filter(Customer.status == CustomerStatus.LEAD.value).scalar() or 0

    # Revenue
    total_revenue = db.query(func.coalesce(func.sum(Customer.lifetime_revenue), 0.0)).scalar()
    month_revenue = (
        db.query(func.coalesce(func.sum(Invoice.total), 0.0))
        .filter(Invoice.status == InvoiceStatus.PAID.value, Invoice.paid_date >= month_start)
        .scalar()
    )
    week_revenue = (
        db.query(func.coalesce(func.sum(Invoice.total), 0.0))
        .filter(Invoice.status == InvoiceStatus.PAID.value, Invoice.paid_date >= week_start)
        .scalar()
    )

    # Outstanding AR
    outstanding = (
        db.query(func.coalesce(func.sum(Invoice.total), 0.0))
        .filter(Invoice.status.in_([InvoiceStatus.SENT.value, InvoiceStatus.DRAFT.value, InvoiceStatus.OVERDUE.value]))
        .scalar()
    )

    # Open quotes
    open_quotes = db.query(func.count(Quote.id)).filter(Quote.status.in_([QuoteStatus.SENT.value, QuoteStatus.DRAFT.value])).scalar() or 0
    quote_value = (
        db.query(func.coalesce(func.sum(Quote.total), 0.0))
        .filter(Quote.status.in_([QuoteStatus.SENT.value, QuoteStatus.DRAFT.value]))
        .scalar()
    )

    # Zones
    zones = (
        db.query(Customer.service_zone, func.count(Customer.id))
        .filter(Customer.service_zone.isnot(None), Customer.service_zone != "")
        .group_by(Customer.service_zone).all()
    )

    # Recent customers
    recent = db.query(Customer).order_by(Customer.created_at.desc()).limit(5).all()

    # Follow-up needed
    cutoff = now - timedelta(days=60)
    followup = (
        db.query(Customer).filter(
            Customer.status == CustomerStatus.ACTIVE.value,
            (Customer.last_service_date < cutoff) | (Customer.last_service_date.is_(None)),
        ).order_by(Customer.last_service_date.asc().nullsfirst()).limit(10).all()
    )

    # Today's schedule
    today = now.date()
    today_visits = (
        db.query(ServiceVisit).join(Customer)
        .filter(
            ServiceVisit.scheduled_date >= datetime.combine(today, datetime.min.time()),
            ServiceVisit.scheduled_date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
        ).order_by(ServiceVisit.scheduled_order).all()
    )

    # Weather
    forecast_data = await get_forecast(days=3)
    forecast = parse_daily_forecast(forecast_data) if forecast_data else []

    # AI Insight
    ai_insight = None
    try:
        stats = {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "pending_leads": pending_leads,
            "month_revenue": float(month_revenue),
            "outstanding_ar": float(outstanding),
            "open_quotes": open_quotes,
            "quote_pipeline_value": float(quote_value),
            "zones": {z: c for z, c in zones},
            "jobs_today": len(today_visits),
        }
        ai_insight = await generate_business_insight(stats)
    except Exception as exc:
        log.error("AI insight failed: %s", exc)

    return request.app.state.templates.TemplateResponse(
        request, "dashboard.html", {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "pending_leads": pending_leads,
            "total_revenue": total_revenue,
            "month_revenue": month_revenue,
            "week_revenue": week_revenue,
            "outstanding": outstanding,
            "open_quotes": open_quotes,
            "quote_value": quote_value,
            "zones": zones,
            "recent_customers": recent,
            "followup_customers": followup,
            "today_visits": today_visits,
            "forecast": forecast,
            "ai_insight": ai_insight,
        },
    )
