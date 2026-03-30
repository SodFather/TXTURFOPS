import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ServiceType(str, enum.Enum):
    FERT_PREEMERGENT_1 = "Pre-Emergent Round 1"
    FERT_PREEMERGENT_2 = "Pre-Emergent Round 2"
    FERTILIZATION = "Fertilization"
    POST_EMERGENT = "Post-Emergent Weed Control"
    GRUB_PREVENTIVE = "Grub Preventive"
    PEST_CONTROL = "Pest Control"
    WINTERIZER = "Winterizer"
    IRRIGATION_DIAGNOSTIC = "Irrigation Diagnostic"
    IRRIGATION_REPAIR = "Irrigation Repair"
    IRRIGATION_INSTALL = "Irrigation Install"


class VisitStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    RESCHEDULED = "Rescheduled"


class ServiceVisit(Base):
    __tablename__ = "service_visits"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    service_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default=VisitStatus.SCHEDULED.value, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    scheduled_order = Column(Integer, default=0)

    # Field data (filled during visit)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    start_lat = Column(Float)
    start_lon = Column(Float)
    products_applied = Column(Text)  # JSON: [{"name":..,"epa_reg":..,"rate":..,"area":..}]
    equipment_used = Column(String(200))
    area_treated_sqft = Column(Integer)
    notes = Column(Text)

    # Weather (auto-populated from Open-Meteo)
    temperature_f = Column(Float)
    wind_speed_mph = Column(Float)
    wind_direction = Column(String(20))
    humidity_pct = Column(Float)
    conditions = Column(String(100))

    # Billing link
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", backref="service_visits")
    invoice = relationship("Invoice", backref="service_visit")

    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return None
