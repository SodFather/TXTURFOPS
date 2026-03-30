import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    invoice_number = Column(String(50), unique=True, index=True)
    status = Column(String(50), default=InvoiceStatus.DRAFT.value, index=True)
    notes = Column(Text)
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    sent_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", backref="invoices")
    quote = relationship("Quote", backref="invoice")
    line_items = relationship(
        "InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan"
    )

    @property
    def is_overdue(self):
        if self.status in (InvoiceStatus.PAID.value, InvoiceStatus.CANCELLED.value):
            return False
        if not self.due_date:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.due_date.replace(tzinfo=timezone.utc)

    @property
    def days_outstanding(self):
        if not self.created_at:
            return 0
        from datetime import datetime, timezone
        return (datetime.now(timezone.utc) - self.created_at.replace(tzinfo=timezone.utc)).days


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="line_items")


def generate_invoice_number(db) -> str:
    """Generate next invoice number like INV-2026-0001."""
    from datetime import datetime
    year = datetime.now().year
    prefix = f"INV-{year}-"
    last = (
        db.query(Invoice)
        .filter(Invoice.invoice_number.like(f"{prefix}%"))
        .order_by(Invoice.invoice_number.desc())
        .first()
    )
    if last and last.invoice_number:
        seq = int(last.invoice_number.split("-")[-1]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"
