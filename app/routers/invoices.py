from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.customer import Customer
from ..models.invoice import Invoice, InvoiceLineItem, InvoiceStatus, generate_invoice_number
from ..services.pdf_generator import generate_invoice_pdf
from ..services.email_service import send_email

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/")
async def list_invoices(request: Request, db: Session = Depends(get_db),
                        status: str = "", view: str = ""):
    query = db.query(Invoice).join(Customer)
    if status:
        query = query.filter(Invoice.status == status)
    invoices = query.order_by(Invoice.created_at.desc()).all()

    # AR aging buckets
    now = datetime.now(timezone.utc)
    unpaid = [i for i in invoices if i.status not in (InvoiceStatus.PAID.value, InvoiceStatus.CANCELLED.value)]
    aging = {"current": [], "over30": [], "over60": [], "over90": []}
    for inv in unpaid:
        days = inv.days_outstanding
        if days >= 90:
            aging["over90"].append(inv)
        elif days >= 60:
            aging["over60"].append(inv)
        elif days >= 30:
            aging["over30"].append(inv)
        else:
            aging["current"].append(inv)

    total_outstanding = sum(i.total for i in unpaid)

    return request.app.state.templates.TemplateResponse(
        request, "invoices/list.html", {
            "invoices": invoices,
            "statuses": [s.value for s in InvoiceStatus],
            "status": status,
            "aging": aging,
            "total_outstanding": total_outstanding,
            "view": view,
        },
    )


@router.get("/new")
async def new_invoice_form(request: Request, db: Session = Depends(get_db),
                           customer_id: str = "", quote_id: str = ""):
    customers = db.query(Customer).order_by(Customer.name).all()
    selected = None
    if customer_id and customer_id.isdigit():
        selected = db.query(Customer).get(int(customer_id))

    return request.app.state.templates.TemplateResponse(
        request, "invoices/form.html", {
            "invoice": None,
            "customers": customers,
            "selected_customer": selected,
        },
    )


@router.post("/create")
async def create_invoice(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    customer_id = int(form.get("customer_id", 0))
    notes = form.get("notes", "").strip()
    due_days = int(form.get("due_days", 30) or 30)

    invoice = Invoice(
        customer_id=customer_id,
        invoice_number=generate_invoice_number(db),
        notes=notes,
        status=InvoiceStatus.DRAFT.value,
        due_date=datetime.now(timezone.utc) + timedelta(days=due_days),
    )
    db.add(invoice)
    db.flush()

    idx = 0
    subtotal = 0.0
    while f"item_desc_{idx}" in form:
        desc = form.get(f"item_desc_{idx}", "")
        qty = int(form.get(f"item_qty_{idx}", 1) or 1)
        price = float(form.get(f"item_price_{idx}", 0) or 0)
        line_total = qty * price
        subtotal += line_total
        if desc:
            db.add(InvoiceLineItem(
                invoice_id=invoice.id, description=desc,
                quantity=qty, unit_price=price, total=line_total,
            ))
        idx += 1

    tax_rate = float(form.get("tax_rate", 0) or 0)
    tax_amount = subtotal * (tax_rate / 100)
    invoice.subtotal = subtotal
    invoice.tax_rate = tax_rate
    invoice.tax_amount = tax_amount
    invoice.total = subtotal + tax_amount

    # Update customer lifetime revenue
    customer = db.query(Customer).get(customer_id)
    if customer:
        customer.lifetime_revenue = (customer.lifetime_revenue or 0) + invoice.total

    db.commit()

    request.session["flash"] = f"Invoice {invoice.invoice_number} created."
    return RedirectResponse(url=f"/invoices/{invoice.id}", status_code=303)


@router.get("/{invoice_id}")
async def invoice_detail(request: Request, invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return RedirectResponse(url="/invoices", status_code=303)
    return request.app.state.templates.TemplateResponse(
        request, "invoices/detail.html", {"invoice": invoice},
    )


@router.get("/{invoice_id}/pdf")
async def invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return RedirectResponse(url="/invoices", status_code=303)
    pdf_bytes = generate_invoice_pdf(invoice, invoice.customer)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={invoice.invoice_number}.pdf"},
    )


@router.post("/{invoice_id}/send")
async def send_invoice(request: Request, invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice or not invoice.customer.email:
        request.session["flash"] = "Cannot send — customer has no email."
        return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)

    pdf_bytes = generate_invoice_pdf(invoice, invoice.customer)
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(pdf_bytes)
    tmp.close()

    await send_email(
        to=invoice.customer.email,
        subject=f"Invoice {invoice.invoice_number} from TX TURF PROS",
        body_html=f"<p>Hi {invoice.customer.name},</p><p>Please find your invoice attached. Amount due: <b>${invoice.total:.2f}</b></p><p>Thank you,<br>TX TURF PROS</p>",
        attachment_path=tmp.name,
    )
    os.unlink(tmp.name)

    invoice.status = InvoiceStatus.SENT.value
    invoice.sent_date = datetime.now(timezone.utc)
    db.commit()

    request.session["flash"] = f"Invoice {invoice.invoice_number} sent."
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)


@router.post("/{invoice_id}/pay")
async def mark_paid(request: Request, invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice:
        invoice.status = InvoiceStatus.PAID.value
        invoice.paid_date = datetime.now(timezone.utc)
        db.commit()
    request.session["flash"] = f"Invoice {invoice.invoice_number} marked as paid."
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice:
        db.delete(invoice)
        db.commit()
    return ""
