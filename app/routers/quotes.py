from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.customer import Customer
from ..models.quote import Quote, QuoteLineItem, QuoteStatus
from ..models.price_tier import PriceTier
from ..services.pdf_generator import generate_quote_pdf
from ..services.email_service import send_email

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/")
async def list_quotes(request: Request, db: Session = Depends(get_db),
                      status: str = "", customer_id: str = ""):
    query = db.query(Quote).join(Customer)
    if status:
        query = query.filter(Quote.status == status)
    if customer_id and customer_id.isdigit():
        query = query.filter(Quote.customer_id == int(customer_id))
    quotes = query.order_by(Quote.created_at.desc()).all()

    return request.app.state.templates.TemplateResponse(
        request, "quotes/list.html", {
            "quotes": quotes,
            "statuses": [s.value for s in QuoteStatus],
            "status": status,
        },
    )


@router.get("/new")
async def new_quote_form(request: Request, db: Session = Depends(get_db),
                         customer_id: str = ""):
    customers = db.query(Customer).order_by(Customer.name).all()
    tiers = db.query(PriceTier).order_by(PriceTier.service_type, PriceTier.min_sqft).all()
    # Group tiers by service type for the JS price lookup
    price_map = {}
    for t in tiers:
        price_map.setdefault(t.service_type, []).append({
            "tier": t.size_tier_name, "min": t.min_sqft,
            "max": t.max_sqft, "price": t.price,
        })

    selected = None
    if customer_id and customer_id.isdigit():
        selected = db.query(Customer).get(int(customer_id))

    return request.app.state.templates.TemplateResponse(
        request, "quotes/form.html", {
            "quote": None,
            "customers": customers,
            "selected_customer": selected,
            "price_map": price_map,
            "service_types": list(price_map.keys()),
        },
    )


@router.post("/create")
async def create_quote(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    customer_id = int(form.get("customer_id", 0))
    notes = form.get("notes", "").strip()

    quote = Quote(customer_id=customer_id, notes=notes, status=QuoteStatus.DRAFT.value)
    db.add(quote)
    db.flush()

    # Parse line items from form (item_service_0, item_desc_0, item_qty_0, item_price_0, ...)
    idx = 0
    subtotal = 0.0
    while f"item_service_{idx}" in form:
        svc = form.get(f"item_service_{idx}", "")
        desc = form.get(f"item_desc_{idx}", "")
        qty = int(form.get(f"item_qty_{idx}", 1) or 1)
        price = float(form.get(f"item_price_{idx}", 0) or 0)
        line_total = qty * price
        subtotal += line_total
        if svc:
            db.add(QuoteLineItem(
                quote_id=quote.id, service_type=svc, description=desc,
                quantity=qty, unit_price=price, total=line_total,
            ))
        idx += 1

    quote.subtotal = subtotal
    quote.total = subtotal
    db.commit()

    request.session["flash"] = f"Quote #{quote.id} created."
    return RedirectResponse(url=f"/quotes/{quote.id}", status_code=303)


@router.get("/{quote_id}")
async def quote_detail(request: Request, quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return RedirectResponse(url="/quotes", status_code=303)
    return request.app.state.templates.TemplateResponse(
        request, "quotes/detail.html", {"quote": quote},
    )


@router.get("/{quote_id}/pdf")
async def quote_pdf(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return RedirectResponse(url="/quotes", status_code=303)
    pdf_bytes = generate_quote_pdf(quote, quote.customer)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=quote-{quote.id}.pdf"},
    )


@router.post("/{quote_id}/send")
async def send_quote(request: Request, quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote or not quote.customer.email:
        request.session["flash"] = "Cannot send — customer has no email."
        return RedirectResponse(url=f"/quotes/{quote_id}", status_code=303)

    pdf_bytes = generate_quote_pdf(quote, quote.customer)
    # Save temp PDF for attachment
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(pdf_bytes)
    tmp.close()

    sent = await send_email(
        to=quote.customer.email,
        subject=f"Quote from TX TURF PROS — #{quote.id}",
        body_html=f"<p>Hi {quote.customer.name},</p><p>Please find your quote attached. Total: <b>${quote.total:.2f}</b></p><p>Thank you,<br>TX TURF PROS</p>",
        attachment_path=tmp.name,
    )
    os.unlink(tmp.name)

    quote.status = QuoteStatus.SENT.value
    quote.sent_date = datetime.now(timezone.utc)
    db.commit()

    request.session["flash"] = f"Quote #{quote.id} marked as sent."
    return RedirectResponse(url=f"/quotes/{quote_id}", status_code=303)


@router.post("/{quote_id}/status")
async def update_quote_status(request: Request, quote_id: int,
                               db: Session = Depends(get_db),
                               new_status: str = Form(...)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if quote:
        quote.status = new_status
        if new_status in (QuoteStatus.ACCEPTED.value, QuoteStatus.DECLINED.value):
            quote.responded_date = datetime.now(timezone.utc)
        db.commit()
    return RedirectResponse(url=f"/quotes/{quote_id}", status_code=303)


@router.delete("/{quote_id}")
async def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if quote:
        db.delete(quote)
        db.commit()
    return ""
