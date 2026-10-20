"""Extract text from local invoice PDFs and compare it with a CSV record.

This initial parser is tuned to the synthetic invoice examples. It does not run
OCR and it never changes the source CSV or purchase record.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .data import PurchaseRecord


class InvoiceReadError(Exception):
    """Raised when an invoice PDF cannot be read or has no extractable text."""


@dataclass(frozen=True)
class FieldComparison:
    label: str
    csv_value: object | None
    pdf_value: object | None
    status: str


@dataclass(frozen=True)
class InvoiceComparison:
    page_count: int
    checks: tuple[FieldComparison, ...]

    @property
    def matched_count(self) -> int:
        return sum(check.status == "MATCH" for check in self.checks)

    @property
    def mismatch_count(self) -> int:
        return sum(check.status == "MISMATCH" for check in self.checks)

    @property
    def unavailable_count(self) -> int:
        return sum(check.status != "MATCH" and check.status != "MISMATCH" for check in self.checks)


def _read_labeled_value(text: str, label: str) -> str | None:
    match = re.search(
        rf"(?:^|\n)\s*{re.escape(label)}\s*:\s*(.*?)\s*(?=\n|$)",
        text,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    cleaned = value.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return Decimal(match.group(0))
    except InvalidOperation:
        return None


def _parse_money(text: str, label: str) -> tuple[str | None, Decimal | None]:
    value = _read_labeled_value(text, label)
    if not value:
        return None, None
    currency_match = re.search(r"\b([A-Z]{3})\b", value, re.IGNORECASE)
    amount = _parse_decimal(value)
    currency = currency_match.group(1).upper() if currency_match else None
    return currency, amount


def _parse_invoice_fields(text: str) -> dict[str, object | None]:
    fields: dict[str, object | None] = {
        "document_reference": _read_labeled_value(text, "Invoice number"),
        "purchase_date": None,
        "supplier_name": _read_labeled_value(text, "Supplier"),
        "item_description": _read_labeled_value(text, "Item"),
        "manufacturer": None,
        "model": None,
        "screen_size_in": None,
        "processor": None,
        "ram_gb": None,
        "storage_gb": None,
        "operating_system": _read_labeled_value(text, "Operating system"),
        "quantity": None,
        "currency": None,
        "unit_price_ex_tax": None,
        "tax_rate_percent": None,
        "tax_amount": None,
        "shipping_amount": None,
        "total_amount": None,
        "warranty_months": None,
    }

    date_text = _read_labeled_value(text, "Invoice date")
    if date_text:
        try:
            fields["purchase_date"] = date.fromisoformat(date_text)
        except ValueError:
            pass

    manufacturer_model = _read_labeled_value(text, "Manufacturer and model")
    if manufacturer_model:
        parts = manufacturer_model.rsplit(" ", maxsplit=1)
        if len(parts) == 2:
            fields["manufacturer"], fields["model"] = parts

    specifications = _read_labeled_value(text, "Specifications") or ""
    screen = re.search(r"\b(\d+(?:\.\d+)?)\s*-?\s*inch(?:es)?\b", specifications, re.IGNORECASE)
    processor = re.search(r"\b(?:Core\s+i[3579]\s+class|Ryzen\s+[3579])\b", specifications, re.IGNORECASE)
    ram = re.search(r"\b(\d+)\s*GB\s+RAM\b", specifications, re.IGNORECASE)
    storage = re.search(r"\b(\d+)\s*GB\s+(?:SSD|storage)\b", specifications, re.IGNORECASE)
    if screen:
        fields["screen_size_in"] = Decimal(screen.group(1))
    if processor:
        fields["processor"] = processor.group(0)
    if ram:
        fields["ram_gb"] = int(ram.group(1))
    if storage:
        fields["storage_gb"] = int(storage.group(1))

    quantity = _read_labeled_value(text, "Quantity")
    if quantity:
        try:
            fields["quantity"] = int(quantity)
        except ValueError:
            pass

    currency_value = _read_labeled_value(text, "Currency")
    if currency_value:
        currency_match = re.search(r"\b([A-Z]{3})\b", currency_value, re.IGNORECASE)
        if currency_match:
            fields["currency"] = currency_match.group(1).upper()

    for label, field_name in (
        ("Unit price before tax", "unit_price_ex_tax"),
        ("GST amount", "tax_amount"),
        ("Shipping", "shipping_amount"),
        ("Invoice total", "total_amount"),
    ):
        currency, amount = _parse_money(text, label)
        if currency:
            fields["currency"] = currency
        fields[field_name] = amount

    tax_rate = _read_labeled_value(text, "GST rate")
    if tax_rate:
        fields["tax_rate_percent"] = _parse_decimal(tax_rate)

    warranty = _read_labeled_value(text, "Warranty")
    if warranty:
        fields["warranty_months"] = _parse_decimal(warranty)

    return fields


def _normalize(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def _compare(label: str, csv_value: object | None, pdf_value: object | None) -> FieldComparison:
    if pdf_value is None:
        status = "NOT EXTRACTED FROM PDF"
    elif csv_value is None:
        status = "NOT RECORDED IN CSV"
    elif isinstance(csv_value, str) and isinstance(pdf_value, str):
        status = "MATCH" if _normalize(csv_value) == _normalize(pdf_value) else "MISMATCH"
    else:
        status = "MATCH" if csv_value == pdf_value else "MISMATCH"
    return FieldComparison(label, csv_value, pdf_value, status)


def compare_invoice_to_record(
    record: PurchaseRecord, sample_data_directory: Path
) -> InvoiceComparison:
    """Extract a sample invoice and compare its values with one CSV line."""
    root = sample_data_directory.resolve()
    pdf_path = (root / record.source_file).resolve()
    if root not in pdf_path.parents:
        raise InvoiceReadError("Invoice source path is outside the sample data folder.")
    if not pdf_path.is_file():
        raise InvoiceReadError(f"Invoice file not found: {record.source_file}")

    try:
        reader = PdfReader(pdf_path, strict=False)
        page_text = [page.extract_text() or "" for page in reader.pages]
    except (OSError, PdfReadError, ValueError) as exc:
        raise InvoiceReadError(f"Could not read invoice PDF: {exc}") from exc

    text = "\n".join(page_text).strip()
    if not text:
        raise InvoiceReadError(
            "PDF has no extractable text; scanned invoices need a later OCR step."
        )

    pdf_fields = _parse_invoice_fields(text)
    comparisons = (
        _compare("Invoice number", record.document_reference, pdf_fields["document_reference"]),
        _compare("Invoice date", record.purchase_date, pdf_fields["purchase_date"]),
        _compare("Supplier", record.supplier_name, pdf_fields["supplier_name"]),
        _compare("Item", record.item_description, pdf_fields["item_description"]),
        _compare("Manufacturer", record.manufacturer, pdf_fields["manufacturer"]),
        _compare("Model", record.model, pdf_fields["model"]),
        _compare("Screen size", record.screen_size_in, pdf_fields["screen_size_in"]),
        _compare("Processor", record.processor, pdf_fields["processor"]),
        _compare("RAM", record.ram_gb, pdf_fields["ram_gb"]),
        _compare("Storage", record.storage_gb, pdf_fields["storage_gb"]),
        _compare("Operating system", record.operating_system, pdf_fields["operating_system"]),
        _compare("Quantity", record.quantity, pdf_fields["quantity"]),
        _compare("Currency", record.currency, pdf_fields["currency"]),
        _compare("Unit price before tax", record.unit_price_ex_tax, pdf_fields["unit_price_ex_tax"]),
        _compare("Tax rate", record.tax_rate_percent, pdf_fields["tax_rate_percent"]),
        _compare("Tax amount", record.tax_amount, pdf_fields["tax_amount"]),
        _compare("Shipping", record.shipping_amount, pdf_fields["shipping_amount"]),
        _compare("Invoice total", record.total_amount, pdf_fields["total_amount"]),
        _compare("Warranty", record.warranty_months, pdf_fields["warranty_months"]),
    )
    return InvoiceComparison(page_count=len(page_text), checks=comparisons)
