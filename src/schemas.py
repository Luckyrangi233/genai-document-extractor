"""Strict typed output schemas."""
from pydantic import BaseModel, Field
from datetime import date

class LineItem(BaseModel):
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    total: float = Field(ge=0)

class Invoice(BaseModel):
    vendor_name: str
    vendor_gstin: str | None = None
    invoice_number: str
    invoice_date: date
    currency: str = "INR"
    line_items: list[LineItem]
    subtotal: float = Field(ge=0)
    tax_amount: float = Field(ge=0)
    grand_total: float = Field(ge=0)
