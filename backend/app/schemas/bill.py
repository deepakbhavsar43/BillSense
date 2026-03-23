from datetime import datetime

from pydantic import BaseModel, Field


class BillItem(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    line_total: float | None = None
    category: str | None = None


class TaxBreakdownEntry(BaseModel):
    tax_type: str | None = None
    rate: float | None = None
    amount: float | None = None
    applies_to: str | None = None
    reference: str | None = None


class ParsedBill(BaseModel):
    merchant_name: str | None = None
    merchant_address: str | None = None
    merchant_phone: str | None = None
    bill_number: str | None = None
    invoice_number: str | None = None
    purchase_date: str | None = None
    purchase_time: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    tax_breakdown: list[TaxBreakdownEntry] = Field(default_factory=list)
    discount: float | None = None
    total: float | None = None
    payment_method: str | None = None
    items: list[BillItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    raw_text: str | None = None


class StoredBillRecord(BaseModel):
    bill_id: str
    source_file_name: str
    source_media_type: str
    source_image_path: str
    parsed_at: datetime
    bill: ParsedBill


class BillQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class BillQuestionResponse(BaseModel):
    bill_id: str
    answer: str
    provider: str


class BillExportResponse(BaseModel):
    bill_id: str
    export_path: str
