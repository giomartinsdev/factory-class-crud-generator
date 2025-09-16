from sqlalchemy import Column, Integer, ForeignKey
from models.base import BaseModel
from sqlalchemy.orm import relationship

class Offer(BaseModel):
    product = relationship("Product", back_populates="offers")

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    reference_year = Column(Integer, nullable=False)
    reference_month = Column(Integer, nullable=False)
    value = Column(Integer, nullable=False)    
