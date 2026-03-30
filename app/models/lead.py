from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    referred_name = Column(String(200), nullable=False)
    referred_email = Column(String(200))
    referred_phone = Column(String(30))
    referred_address = Column(String(500))
    status = Column(String(50), default="Pending")  # Pending / Converted / Expired
    credit_amount = Column(Float, default=25.0)
    credit_applied = Column(Integer, default=0)  # 0 = not yet applied
    converted_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    referrer = relationship("Customer", foreign_keys=[referrer_id], backref="referrals_given")
    converted_customer = relationship("Customer", foreign_keys=[converted_customer_id])


class Neighborhood(Base):
    __tablename__ = "neighborhoods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    zone = Column(String(50))  # Lakeway / Spicewood / Bee Caves
    estimated_homes = Column(Integer, default=0)
    notes = Column(Text)
    center_lat = Column(Float)
    center_lon = Column(Float)

    @property
    def penetration_rate(self):
        if not self.estimated_homes:
            return 0.0
        # Calculated dynamically in the route handler
        return 0.0


# Default neighborhoods for TX TURF PROS territory
DEFAULT_NEIGHBORHOODS = [
    ("Rough Hollow", "Lakeway", 1200, 30.3920, -97.9580),
    ("Flintrock Falls", "Lakeway", 450, 30.3640, -97.9420),
    ("Lakeway Highlands", "Lakeway", 800, 30.4050, -97.9700),
    ("The Hills", "Lakeway", 600, 30.3700, -97.9200),
    ("Tuscan Village", "Lakeway", 350, 30.3850, -97.9500),
    ("Falconhead", "Bee Caves", 500, 30.3400, -97.9600),
    ("Spanish Oaks", "Bee Caves", 400, 30.3200, -97.9400),
    ("Sweetwater", "Bee Caves", 350, 30.3100, -97.9300),
    ("West Cypress Hills", "Spicewood", 300, 30.4400, -98.0200),
    ("Briarcliff", "Spicewood", 250, 30.4100, -97.9900),
]


def seed_neighborhoods(db):
    if db.query(Neighborhood).count() == 0:
        for name, zone, homes, lat, lon in DEFAULT_NEIGHBORHOODS:
            db.add(Neighborhood(
                name=name, zone=zone, estimated_homes=homes,
                center_lat=lat, center_lon=lon,
            ))
        db.commit()
