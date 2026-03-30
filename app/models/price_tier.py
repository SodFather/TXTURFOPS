from sqlalchemy import Column, Integer, String, Float
from ..database import Base


class PriceTier(Base):
    __tablename__ = "price_tiers"

    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(String(100), nullable=False, index=True)
    size_tier_name = Column(String(50), nullable=False)  # Small / Medium / Large / XL
    min_sqft = Column(Integer, default=0)
    max_sqft = Column(Integer, default=999999)
    price = Column(Float, nullable=False)


# Default pricing for TX TURF PROS service area
DEFAULT_TIERS = [
    # Fertilization & Pre-Emergent rounds
    ("Fertilization Round", "Small (<5k)", 0, 4999, 55.0),
    ("Fertilization Round", "Medium (5-10k)", 5000, 9999, 75.0),
    ("Fertilization Round", "Large (10-20k)", 10000, 19999, 110.0),
    ("Fertilization Round", "XL (20k+)", 20000, 999999, 150.0),
    # Post-emergent weed control
    ("Weed Control", "Small (<5k)", 0, 4999, 55.0),
    ("Weed Control", "Medium (5-10k)", 5000, 9999, 75.0),
    ("Weed Control", "Large (10-20k)", 10000, 19999, 110.0),
    ("Weed Control", "XL (20k+)", 20000, 999999, 150.0),
    # Pest & grub control
    ("Pest Control", "Small (<5k)", 0, 4999, 65.0),
    ("Pest Control", "Medium (5-10k)", 5000, 9999, 90.0),
    ("Pest Control", "Large (10-20k)", 10000, 19999, 130.0),
    ("Pest Control", "XL (20k+)", 20000, 999999, 175.0),
    # Grub preventive
    ("Grub Preventive", "Small (<5k)", 0, 4999, 70.0),
    ("Grub Preventive", "Medium (5-10k)", 5000, 9999, 95.0),
    ("Grub Preventive", "Large (10-20k)", 10000, 19999, 140.0),
    ("Grub Preventive", "XL (20k+)", 20000, 999999, 185.0),
    # Irrigation
    ("Irrigation Diagnostic", "Flat Rate", 0, 999999, 85.0),
    ("Irrigation Repair", "Flat Rate", 0, 999999, 125.0),
]


def seed_price_tiers(db):
    """Populate default price tiers if the table is empty."""
    if db.query(PriceTier).count() == 0:
        for svc, tier, lo, hi, price in DEFAULT_TIERS:
            db.add(PriceTier(
                service_type=svc, size_tier_name=tier,
                min_sqft=lo, max_sqft=hi, price=price,
            ))
        db.commit()
