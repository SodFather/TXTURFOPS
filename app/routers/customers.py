import csv
import io
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.customer import Customer, CustomerStatus, PropertyType, ServiceZone, LeadSource
from ..services.geocoding import geocode_address, assign_zone

router = APIRouter(prefix="/customers", tags=["customers"])


# ── Fixed-path routes (must be declared before /{customer_id}) ────────────


@router.get("/")
async def list_customers(
    request: Request,
    db: Session = Depends(get_db),
    q: str = "",
    zone: str = "",
    status: str = "",
):
    query = db.query(Customer)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Customer.name.ilike(like),
                Customer.address.ilike(like),
                Customer.email.ilike(like),
                Customer.phone.ilike(like),
            )
        )
    if zone:
        query = query.filter(Customer.service_zone == zone)
    if status:
        query = query.filter(Customer.status == status)

    customers = query.order_by(Customer.name).all()

    # HTMX partial: return just the table rows
    if request.headers.get("HX-Request"):
        return request.app.state.templates.TemplateResponse(
            request,
            "customers/_table_body.html",
            {"customers": customers},
        )

    return request.app.state.templates.TemplateResponse(
        request,
        "customers/list.html",
        {
            "customers": customers,
            "zones": [z.value for z in ServiceZone],
            "statuses": [s.value for s in CustomerStatus],
            "q": q,
            "zone": zone,
            "status": status,
        },
    )


@router.get("/new")
async def new_customer_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "customers/form.html",
        {
            "customer": None,
            "statuses": [s.value for s in CustomerStatus],
            "property_types": [p.value for p in PropertyType],
            "zones": [z.value for z in ServiceZone],
            "lead_sources": [l.value for l in LeadSource],
        },
    )


@router.get("/export")
async def export_csv(db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.name).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "Name", "Address", "Email", "Phone", "Property Size (sqft)",
            "Property Type", "Service Zone", "Status", "Lead Source",
            "Notes", "Lifetime Revenue", "Last Service Date", "Created",
        ]
    )
    for c in customers:
        writer.writerow(
            [
                c.name, c.address or "", c.email or "", c.phone or "",
                c.property_size_sqft or "",
                c.property_type or "", c.service_zone or "",
                c.status or "", c.lead_source or "",
                c.notes or "", c.lifetime_revenue or 0,
                c.last_service_date.isoformat() if c.last_service_date else "",
                c.created_at.isoformat() if c.created_at else "",
            ]
        )

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers.csv"},
    )


@router.post("/import")
async def import_csv(
    request: Request,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    count = 0

    for row in reader:
        size_raw = row.get("Property Size (sqft)", "").strip()
        customer = Customer(
            name=row.get("Name", "").strip(),
            address=row.get("Address", "").strip(),
            email=row.get("Email", "").strip(),
            phone=row.get("Phone", "").strip(),
            property_size_sqft=int(size_raw) if size_raw.isdigit() else None,
            property_type=row.get("Property Type", PropertyType.RESIDENTIAL.value).strip(),
            service_zone=row.get("Service Zone", "").strip(),
            status=row.get("Status", CustomerStatus.LEAD.value).strip(),
            lead_source=row.get("Lead Source", "").strip(),
            notes=row.get("Notes", "").strip(),
        )

        # Auto-geocode
        if customer.address:
            geo = await geocode_address(customer.address)
            if geo:
                customer.latitude = geo["latitude"]
                customer.longitude = geo["longitude"]
            if not customer.service_zone:
                zone = assign_zone(customer.address, geo.get("postcode", "") if geo else "")
                if zone:
                    customer.service_zone = zone

        db.add(customer)
        count += 1

    db.commit()
    request.session["flash"] = f"Imported {count} customer{'s' if count != 1 else ''}."
    return RedirectResponse(url="/customers", status_code=303)


# ── Parameterised routes ──────────────────────────────────────────────────


@router.post("/create")
async def create_customer(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    address: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    property_size_sqft: str = Form(""),
    property_type: str = Form(PropertyType.RESIDENTIAL.value),
    service_zone: str = Form(""),
    notes: str = Form(""),
    lead_source: str = Form(""),
    status: str = Form(CustomerStatus.LEAD.value),
):
    customer = Customer(
        name=name.strip(),
        address=address.strip(),
        email=email.strip(),
        phone=phone.strip(),
        property_size_sqft=int(property_size_sqft) if property_size_sqft.strip().isdigit() else None,
        property_type=property_type,
        service_zone=service_zone,
        notes=notes.strip(),
        lead_source=lead_source,
        status=status,
        last_contact_date=datetime.now(timezone.utc),
    )

    # Auto-geocode
    if customer.address:
        geo = await geocode_address(customer.address)
        if geo:
            customer.latitude = geo["latitude"]
            customer.longitude = geo["longitude"]
            if not service_zone:
                zone = assign_zone(customer.address, geo.get("postcode", ""))
                if zone:
                    customer.service_zone = zone

    if not customer.service_zone and customer.address:
        zone = assign_zone(customer.address)
        if zone:
            customer.service_zone = zone

    db.add(customer)
    db.commit()
    db.refresh(customer)

    request.session["flash"] = f"Customer \"{customer.name}\" created."
    return RedirectResponse(url=f"/customers/{customer.id}", status_code=303)


@router.get("/{customer_id}")
async def customer_detail(
    request: Request, customer_id: int, db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        request.session["flash"] = "Customer not found."
        return RedirectResponse(url="/customers", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request, "customers/detail.html", {"customer": customer}
    )


@router.get("/{customer_id}/edit")
async def edit_customer_form(
    request: Request, customer_id: int, db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return RedirectResponse(url="/customers", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request,
        "customers/form.html",
        {
            "customer": customer,
            "statuses": [s.value for s in CustomerStatus],
            "property_types": [p.value for p in PropertyType],
            "zones": [z.value for z in ServiceZone],
            "lead_sources": [l.value for l in LeadSource],
        },
    )


@router.post("/{customer_id}")
async def update_customer(
    request: Request,
    customer_id: int,
    db: Session = Depends(get_db),
    name: str = Form(...),
    address: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    property_size_sqft: str = Form(""),
    property_type: str = Form(PropertyType.RESIDENTIAL.value),
    service_zone: str = Form(""),
    notes: str = Form(""),
    lead_source: str = Form(""),
    status: str = Form(CustomerStatus.LEAD.value),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return RedirectResponse(url="/customers", status_code=303)

    address_changed = customer.address != address.strip()

    customer.name = name.strip()
    customer.address = address.strip()
    customer.email = email.strip()
    customer.phone = phone.strip()
    customer.property_size_sqft = int(property_size_sqft) if property_size_sqft.strip().isdigit() else None
    customer.property_type = property_type
    customer.notes = notes.strip()
    customer.lead_source = lead_source
    customer.status = status
    customer.last_contact_date = datetime.now(timezone.utc)

    # Re-geocode if address changed
    if address_changed and customer.address:
        geo = await geocode_address(customer.address)
        if geo:
            customer.latitude = geo["latitude"]
            customer.longitude = geo["longitude"]
            if not service_zone:
                zone = assign_zone(customer.address, geo.get("postcode", ""))
                if zone:
                    service_zone = zone

    if service_zone:
        customer.service_zone = service_zone
    elif not customer.service_zone and customer.address:
        zone = assign_zone(customer.address)
        if zone:
            customer.service_zone = zone

    db.commit()
    request.session["flash"] = f"Customer \"{customer.name}\" updated."
    return RedirectResponse(url=f"/customers/{customer.id}", status_code=303)


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return ""
