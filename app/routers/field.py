import json
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.customer import Customer
from ..models.service_visit import ServiceVisit, VisitStatus
from ..models.invoice import Invoice, InvoiceLineItem, InvoiceStatus, generate_invoice_number
from ..services.weather import get_current_conditions

router = APIRouter(prefix="/field", tags=["field"])


@router.get("/")
async def today_view(request: Request, db: Session = Depends(get_db)):
    """Mobile-optimized view of today's jobs."""
    today = datetime.now(timezone.utc).date()
    tomorrow = today.replace(day=today.day + 1) if today.day < 28 else today

    visits = (
        db.query(ServiceVisit).join(Customer)
        .filter(
            ServiceVisit.scheduled_date >= datetime.combine(today, datetime.min.time()),
            ServiceVisit.scheduled_date < datetime.combine(tomorrow, datetime.min.time()),
            ServiceVisit.status.in_([VisitStatus.SCHEDULED.value, VisitStatus.IN_PROGRESS.value]),
        )
        .order_by(ServiceVisit.scheduled_order, ServiceVisit.scheduled_date)
        .all()
    )

    weather = await get_current_conditions()
    completed_today = (
        db.query(ServiceVisit)
        .filter(
            ServiceVisit.scheduled_date >= datetime.combine(today, datetime.min.time()),
            ServiceVisit.status == VisitStatus.COMPLETED.value,
        ).count()
    )

    return request.app.state.templates.TemplateResponse(
        request, "field/today.html", {
            "visits": visits,
            "weather": weather,
            "completed_today": completed_today,
            "total_today": len(visits) + completed_today,
        },
    )


@router.post("/visit/{visit_id}/start")
async def start_job(request: Request, visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(ServiceVisit).filter(ServiceVisit.id == visit_id).first()
    if visit:
        visit.status = VisitStatus.IN_PROGRESS.value
        visit.start_time = datetime.now(timezone.utc)

        # Auto-populate weather
        weather = await get_current_conditions(
            visit.customer.latitude, visit.customer.longitude
        )
        if weather:
            visit.temperature_f = weather["temperature_f"]
            visit.wind_speed_mph = weather["wind_speed_mph"]
            visit.wind_direction = weather["wind_direction"]
            visit.humidity_pct = weather["humidity_pct"]
            visit.conditions = weather["conditions"]
        db.commit()

    return RedirectResponse(url=f"/field/visit/{visit_id}", status_code=303)


@router.get("/visit/{visit_id}")
async def visit_form(request: Request, visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(ServiceVisit).filter(ServiceVisit.id == visit_id).first()
    if not visit:
        return RedirectResponse(url="/field", status_code=303)
    return request.app.state.templates.TemplateResponse(
        request, "field/visit.html", {"visit": visit},
    )


@router.post("/visit/{visit_id}/complete")
async def complete_job(request: Request, visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(ServiceVisit).filter(ServiceVisit.id == visit_id).first()
    if not visit:
        return RedirectResponse(url="/field", status_code=303)

    form = await request.form()
    visit.status = VisitStatus.COMPLETED.value
    visit.end_time = datetime.now(timezone.utc)
    visit.products_applied = form.get("products_applied", "")
    visit.equipment_used = form.get("equipment_used", "")
    area = form.get("area_treated_sqft", "")
    visit.area_treated_sqft = int(area) if area and area.isdigit() else visit.customer.property_size_sqft
    visit.notes = form.get("notes", "")

    # Update customer last service date
    visit.customer.last_service_date = datetime.now(timezone.utc)
    visit.customer.last_contact_date = datetime.now(timezone.utc)

    # Auto-generate invoice
    auto_invoice = form.get("auto_invoice", "on")
    if auto_invoice == "on":
        inv = Invoice(
            customer_id=visit.customer_id,
            invoice_number=generate_invoice_number(db),
            status=InvoiceStatus.DRAFT.value,
            notes=f"Service: {visit.service_type}",
        )
        db.add(inv)
        db.flush()

        price = float(form.get("service_price", 0) or 0)
        item = InvoiceLineItem(
            invoice_id=inv.id,
            description=f"{visit.service_type} — {visit.customer.address or visit.customer.name}",
            quantity=1, unit_price=price, total=price,
        )
        db.add(item)
        inv.subtotal = price
        inv.total = price
        visit.invoice_id = inv.id

        visit.customer.lifetime_revenue = (visit.customer.lifetime_revenue or 0) + price

    db.commit()
    request.session["flash"] = f"Job completed for {visit.customer.name}."
    return RedirectResponse(url="/field", status_code=303)
