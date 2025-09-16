from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models.enums.LabelEnum import LabelEnum

class Product(BaseModel):    
    offers = relationship("Offer", back_populates="product")

    external_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    label = Column(Enum(LabelEnum), nullable=False)
    description = Column(String(100), nullable=False)

