import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class QuoteStatus(str, enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    VIEWED = "Viewed"
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    EXPIRED = "Expired"


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String(50), default=QuoteStatus.DRAFT.value, index=True)
    notes = Column(Text)
    subtotal = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    valid_days = Column(Integer, default=30)
    sent_date = Column(DateTime)
    viewed_date = Column(DateTime)
    responded_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", backref="quotes")
    line_items = relationship(
        "QuoteLineItem", back_populates="quote", cascade="all, delete-orphan"
    )

    @property
    def is_expired(self):
        if self.status != QuoteStatus.SENT.value:
            return False
        if not self.sent_date:
            return False
        from datetime import datetime, timezone, timedelta
        return datetime.now(timezone.utc) > (
            self.sent_date.replace(tzinfo=timezone.utc) + timedelta(days=self.valid_days)
        )


class QuoteLineItem(Base):
    __tablename__ = "quote_line_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    service_type = Column(String(100), nullable=False)
    description = Column(String(500))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    quote = relationship("Quote", back_populates="line_items")
