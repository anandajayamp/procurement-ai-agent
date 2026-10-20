"""Load synthetic purchase history into a consistent Python record shape."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


class PurchaseHistoryError(Exception):
    """Raised when the purchase-history file cannot be read safely."""


@dataclass(frozen=True)
class PurchaseRecord:
    record_id: str
    document_type: str
    document_reference: str
    purchase_date: date
    supplier_name: str
    item_description: str
    manufacturer: str | None
    model: str | None
    screen_size_in: Decimal | None
    processor: str | None
    ram_gb: int | None
    storage_gb: int | None
    operating_system: str | None
    quantity: int
    currency: str
    unit_price_ex_tax: Decimal
    tax_rate_percent: Decimal | None
    tax_amount: Decimal | None
    shipping_amount: Decimal | None
    total_amount: Decimal
    warranty_months: int | None
    source_file: str


def _required_text(row: dict[str, str], field: str, row_number: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise PurchaseHistoryError(
            f"Row {row_number}: required field '{field}' is blank."
        )
    return value


def _optional_text(row: dict[str, str], field: str) -> str | None:
    value = (row.get(field) or "").strip()
    return value or None


def _decimal(
    row: dict[str, str], field: str, row_number: int, *, required: bool = False
) -> Decimal | None:
    raw_value = (row.get(field) or "").strip()
    if not raw_value:
        if required:
            raise PurchaseHistoryError(
                f"Row {row_number}: required numeric field '{field}' is blank."
            )
        return None
    try:
        return Decimal(raw_value)
    except InvalidOperation as exc:
        raise PurchaseHistoryError(
            f"Row {row_number}: '{field}' must be a number, got {raw_value!r}."
        ) from exc


def _integer(
    row: dict[str, str], field: str, row_number: int, *, required: bool = False
) -> int | None:
    raw_value = (row.get(field) or "").strip()
    if not raw_value:
        if required:
            raise PurchaseHistoryError(
                f"Row {row_number}: required numeric field '{field}' is blank."
            )
        return None
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise PurchaseHistoryError(
            f"Row {row_number}: '{field}' must be a whole number, got {raw_value!r}."
        ) from exc
    return value


def load_purchase_history(path: Path) -> list[PurchaseRecord]:
    """Read CSV rows and fail clearly if required transaction data is malformed."""
    if not path.is_file():
        raise PurchaseHistoryError(f"Purchase-history file not found: {path}")

    records: list[PurchaseRecord] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            required_headers = {
                "record_id",
                "document_type",
                "document_reference",
                "purchase_date",
                "supplier_name",
                "item_description",
                "quantity",
                "currency",
                "unit_price_ex_tax_inr",
                "total_amount_inr",
                "source_file",
            }
            headers = set(reader.fieldnames or [])
            missing_headers = sorted(required_headers - headers)
            if missing_headers:
                raise PurchaseHistoryError(
                    "Purchase-history CSV is missing required columns: "
                    + ", ".join(missing_headers)
                )

            for row_number, row in enumerate(reader, start=2):
                date_text = _required_text(row, "purchase_date", row_number)
                try:
                    purchase_date = date.fromisoformat(date_text)
                except ValueError as exc:
                    raise PurchaseHistoryError(
                        f"Row {row_number}: purchase_date must use YYYY-MM-DD, "
                        f"got {date_text!r}."
                    ) from exc

                quantity = _integer(row, "quantity", row_number, required=True)
                if quantity is None or quantity <= 0:
                    raise PurchaseHistoryError(
                        f"Row {row_number}: quantity must be greater than zero."
                    )

                screen_size = _decimal(row, "screen_size_in", row_number)
                ram_gb = _integer(row, "ram_gb", row_number)
                storage_gb = _integer(row, "storage_gb", row_number)
                warranty_months = _integer(row, "warranty_months", row_number)
                if ram_gb is not None and ram_gb < 0:
                    raise PurchaseHistoryError(
                        f"Row {row_number}: ram_gb cannot be negative."
                    )
                if storage_gb is not None and storage_gb < 0:
                    raise PurchaseHistoryError(
                        f"Row {row_number}: storage_gb cannot be negative."
                    )

                records.append(
                    PurchaseRecord(
                        record_id=_required_text(row, "record_id", row_number),
                        document_type=_required_text(
                            row, "document_type", row_number
                        ),
                        document_reference=_required_text(
                            row, "document_reference", row_number
                        ),
                        purchase_date=purchase_date,
                        supplier_name=_required_text(
                            row, "supplier_name", row_number
                        ),
                        item_description=_required_text(
                            row, "item_description", row_number
                        ),
                        manufacturer=_optional_text(row, "manufacturer"),
                        model=_optional_text(row, "model"),
                        screen_size_in=screen_size,
                        processor=_optional_text(row, "processor"),
                        ram_gb=ram_gb,
                        storage_gb=storage_gb,
                        operating_system=_optional_text(row, "operating_system"),
                        quantity=quantity,
                        currency=_required_text(row, "currency", row_number),
                        unit_price_ex_tax=_decimal(
                            row,
                            "unit_price_ex_tax_inr",
                            row_number,
                            required=True,
                        ),
                        tax_rate_percent=_decimal(
                            row, "tax_rate_percent", row_number
                        ),
                        tax_amount=_decimal(row, "tax_amount_inr", row_number),
                        shipping_amount=_decimal(
                            row, "shipping_amount_inr", row_number
                        ),
                        total_amount=_decimal(
                            row, "total_amount_inr", row_number, required=True
                        ),
                        warranty_months=warranty_months,
                        source_file=_required_text(row, "source_file", row_number),
                    )
                )
    except OSError as exc:
        raise PurchaseHistoryError(
            f"Could not read purchase-history file: {exc}"
        ) from exc

    if not records:
        raise PurchaseHistoryError("Purchase-history CSV contains no records.")
    return records
