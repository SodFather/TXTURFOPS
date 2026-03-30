import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from ..database import Base


class CustomerStatus(str, enum.Enum):
    LEAD = "Lead"
    QUOTED = "Quoted"
    ACTIVE = "Active"
    PAUSED = "Paused"
    CANCELLED = "Cancelled"


class PropertyType(str, enum.Enum):
    RESIDENTIAL = "Residential"
    HOA = "HOA Common Area"
    COMMERCIAL = "Commercial"


class ServiceZone(str, enum.Enum):
    LAKEWAY = "Lakeway"
    SPICEWOOD = "Spicewood"
    BEE_CAVES = "Bee Caves"


class LeadSource(str, enum.Enum):
    REFERRAL = "Referral"
    WEBSITE = "Website"
    YARD_SIGN = "Yard Sign"
    NEXTDOOR = "Nextdoor"
    GOOGLE = "Google"
    OTHER = "Other"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(String(500))
    email = Column(String(200))
    phone = Column(String(30))

    # GPS (auto-populated via geocoding)
    latitude = Column(Float)
    longitude = Column(Float)

    # Property details
    property_size_sqft = Column(Integer)
    property_type = Column(String(50), default=PropertyType.RESIDENTIAL.value)

    # Service info
    service_zone = Column(String(50), index=True)
    active_service_plan = Column(Text)  # JSON string describing current plan rounds
    notes = Column(Text)
    lead_source = Column(String(50))
    status = Column(String(50), default=CustomerStatus.LEAD.value, index=True)

    # Financials
    lifetime_revenue = Column(Float, default=0.0)

    # Dates
    last_service_date = Column(DateTime)
    last_contact_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def days_since_last_service(self):
        if not self.last_service_date:
            return None
        from datetime import datetime, timezone
        delta = datetime.now(timezone.utc) - self.last_service_date.replace(tzinfo=timezone.utc)
        return delta.days

    @property
    def needs_followup(self):
        days = self.days_since_last_service
        return (days is None or days >= 60) and self.status == CustomerStatus.ACTIVE.value
