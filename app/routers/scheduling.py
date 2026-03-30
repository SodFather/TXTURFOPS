import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.customer import Customer
from ..models.service_visit import ServiceVisit, ServiceType, VisitStatus
from ..services.weather import get_forecast, parse_daily_forecast
from ..services.routing import optimize_route

router = APIRouter(prefix="/schedule", tags=["scheduling"])


@router.get("/")
async def calendar_view(request: Request, db: Session = Depends(get_db)):
    # Get all visits for calendar (JSON for FullCalendar)
    visits = db.query(ServiceVisit).join(Customer).all()
    events = []
    color_map = {
        "Scheduled": "#0d6efd", "In Progress": "#ffc107",
        "Completed": "#198754", "Cancelled": "#dc3545", "Rescheduled": "#6c757d",
    }
    for v in visits:
        events.append({
            "id": v.id,
            "title": f"{v.customer.name} — {v.service_type}",
            "start": v.scheduled_date.isoformat() if v.scheduled_date else "",
            "url": f"/schedule/visit/{v.id}",
            "color": color_map.get(v.status, "#0d6efd"),
        })

    # Weather forecast
    forecast = await get_forecast()
    daily = parse_daily_forecast(forecast) if forecast else []

    return request.app.state.templates.TemplateResponse(
        request, "schedule/calendar.html", {
            "events_json": json.dumps(events),
            "forecast": daily,
        },
    )


@router.get("/day/{date}")
async def day_view(request: Request, date: str, db: Session = Depends(get_db)):
    try:
        target = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return RedirectResponse(url="/schedule", status_code=303)

    next_day = target + timedelta(days=1)
    visits = (
        db.query(ServiceVisit).join(Customer)
        .filter(ServiceVisit.scheduled_date >= target, ServiceVisit.scheduled_date < next_day)
        .order_by(ServiceVisit.scheduled_order, ServiceVisit.scheduled_date)
        .all()
    )

    # Build stops for route optimization
    stops = []
    for v in visits:
        if v.customer.latitude and v.customer.longitude:
            stops.append({
                "id": v.id, "lat": v.customer.latitude,
                "lon": v.customer.longitude, "name": v.customer.name,
            })

    route = await optimize_route(stops) if len(stops) >= 2 else None

    # Weather for this date
    forecast = await get_forecast(days=7)
    daily = parse_daily_forecast(forecast) if forecast else []
    day_weather = next((d for d in daily if d["date"] == date), None)

    return request.app.state.templates.TemplateResponse(
        request, "schedule/day.html", {
            "date": target, "date_str": date,
            "visits": visits, "route": route,
            "weather": day_weather,
        },
    )


@router.get("/new")
async def new_visit_form(request: Request, db: Session = Depends(get_db),
                         customer_id: str = "", date: str = ""):
    customers = db.query(Customer).filter(
        Customer.status.in_(["Active", "Quoted", "Lead"])
    ).order_by(Customer.name).all()

    return request.app.state.templates.TemplateResponse(
        request, "schedule/visit_form.html", {
            "visit": None,
            "customers": customers,
            "service_types": [s.value for s in ServiceType],
            "customer_id": customer_id,
            "date": date,
        },
    )


@router.post("/create")
async def create_visit(request: Request, db: Session = Depends(get_db),
                       customer_id: int = Form(...),
                       service_type: str = Form(...),
                       scheduled_date: str = Form(...),
                       notes: str = Form("")):
    visit = ServiceVisit(
        customer_id=customer_id,
        service_type=service_type,
        scheduled_date=datetime.strptime(scheduled_date, "%Y-%m-%dT%H:%M") if "T" in scheduled_date
                       else datetime.strptime(scheduled_date, "%Y-%m-%d"),
        notes=notes.strip(),
        status=VisitStatus.SCHEDULED.value,
    )
    db.add(visit)
    db.commit()

    request.session["flash"] = "Service visit scheduled."
    date_str = visit.scheduled_date.strftime("%Y-%m-%d")
    return RedirectResponse(url=f"/schedule/day/{date_str}", status_code=303)


@router.get("/visit/{visit_id}")
async def visit_detail(request: Request, visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(ServiceVisit).filter(ServiceVisit.id == visit_id).first()
    if not visit:
        return RedirectResponse(url="/schedule", status_code=303)
    return request.app.state.templates.TemplateResponse(
        request, "schedule/visit_detail.html", {"visit": visit},
    )


@router.post("/visit/{visit_id}/cancel")
async def cancel_visit(request: Request, visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(ServiceVisit).filter(ServiceVisit.id == visit_id).first()
    if visit:
        visit.status = VisitStatus.CANCELLED.value
        db.commit()
    return RedirectResponse(url="/schedule", status_code=303)


@router.delete("/visit/{visit_id}")
async def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(ServiceVisit).filter(ServiceVisit.id == visit_id).first()
    if visit:
        db.delete(visit)
        db.commit()
    return ""
