"""Command-line entry point for the local purchase-history prototype."""

from __future__ import annotations

import re
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from .data import PurchaseHistoryError, PurchaseRecord, load_purchase_history
from .invoice_reader import InvoiceReadError, compare_invoice_to_record
from .search import LaptopRequest, MatchResult, normalize_text, search_laptops


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PURCHASE_HISTORY_PATH = PROJECT_ROOT / "sample_data" / "purchase_history.csv"


def _extract_model(text: str, known_models: set[str]) -> str | None:
    normalized_text = normalize_text(text)
    for model in known_models:
        if normalize_text(model) in normalized_text:
            return model

    match = re.search(r"\b[A-Za-z]{1,8}\d{1,5}(?:-[A-Za-z0-9]+){1,3}\b", text)
    if match:
        return match.group(0)

    labeled_match = re.search(
        r"\bmodel\s*(?:number|no\.?|#)?\s*[:=]?\s*([A-Za-z0-9][A-Za-z0-9._/-]+)",
        text,
        re.IGNORECASE,
    )
    return labeled_match.group(1).rstrip(".,") if labeled_match else None


def _extract_request(
    text: str,
    records: list[PurchaseRecord],
    *,
    manufacturer_override: str | None = None,
) -> LaptopRequest:
    manufacturer = manufacturer_override
    if not manufacturer:
        normalized_text = normalize_text(text)
        for known_manufacturer in sorted(
            {record.manufacturer for record in records if record.manufacturer},
            key=len,
            reverse=True,
        ):
            if normalize_text(known_manufacturer) in normalized_text:
                manufacturer = known_manufacturer
                break

    screen_match = re.search(
        r"(?<!\d)(\d{1,2}(?:\.\d+)?)\s*(?:-\s*)?(?:inches?\b|inch\b|in\b|\")",
        text,
        re.IGNORECASE,
    )
    screen_size = Decimal(screen_match.group(1)) if screen_match else None

    ram_match = re.search(
        r"\b(?:at\s+least\s+|minimum\s+|min\s+)?(\d+)\s*gb\s*(?:ram|memory)\b",
        text,
        re.IGNORECASE,
    )
    min_ram = int(ram_match.group(1)) if ram_match else None

    storage_match = re.search(
        r"\b(?:at\s+least\s+|minimum\s+|min\s+)?(\d+(?:\.\d+)?)\s*(gb|tb)\s*(?:ssd|storage|drive|disk)\b",
        text,
        re.IGNORECASE,
    )
    min_storage = None
    if storage_match:
        capacity = Decimal(storage_match.group(1))
        unit = storage_match.group(2).casefold()
        min_storage = int(capacity * (1000 if unit == "tb" else 1))

    processor_match = re.search(
        r"\b(?:core\s*i[3579]|intel\s+core\s+i[3579]|ryzen\s*[3579])\b",
        text,
        re.IGNORECASE,
    )
    operating_system_match = re.search(
        r"\b(?:windows\s*\d{1,2}(?:\s+pro)?|macos|ubuntu|linux)\b",
        text,
        re.IGNORECASE,
    )

    return LaptopRequest(
        manufacturer=manufacturer,
        model=_extract_model(
            text, {record.model for record in records if record.model}
        ),
        screen_size_in=screen_size,
        min_ram_gb=min_ram,
        min_storage_gb=min_storage,
        processor=processor_match.group(0) if processor_match else None,
        operating_system=(
            operating_system_match.group(0) if operating_system_match else None
        ),
    )


def _merge_requests(first: LaptopRequest, second: LaptopRequest) -> LaptopRequest:
    return LaptopRequest(
        manufacturer=second.manufacturer or first.manufacturer,
        model=second.model or first.model,
        screen_size_in=second.screen_size_in or first.screen_size_in,
        min_ram_gb=second.min_ram_gb or first.min_ram_gb,
        min_storage_gb=second.min_storage_gb or first.min_storage_gb,
        processor=second.processor or first.processor,
        operating_system=second.operating_system or first.operating_system,
    )


def _format_money(currency: str, amount: Decimal) -> str:
    return f"{currency} {amount:,.2f}"


def _print_result(result: MatchResult) -> None:
    record = result.record
    print(f"\n{result.label}")
    print(f"  Item: {record.item_description}")
    product_name = " ".join(
        value for value in (record.manufacturer or "Unknown", record.model) if value
    )
    print(f"  Product: {product_name}")
    specs = []
    if record.screen_size_in is not None:
        specs.append(f"{record.screen_size_in} in screen")
    if record.processor:
        specs.append(record.processor)
    if record.ram_gb is not None:
        specs.append(f"{record.ram_gb} GB RAM")
    if record.storage_gb is not None:
        specs.append(f"{record.storage_gb} GB storage")
    if record.operating_system:
        specs.append(record.operating_system)
    if specs:
        print(f"  Recorded specifications: {', '.join(specs)}")
    print(f"  Supplier: {record.supplier_name}")
    print(f"  Purchase date: {record.purchase_date.isoformat()} (historical)")
    print(f"  Quantity: {record.quantity}")
    print(
        "  Unit price before tax: "
        f"{_format_money(record.currency, record.unit_price_ex_tax)}"
    )
    if record.tax_amount is not None:
        print(f"  Tax amount: {_format_money(record.currency, record.tax_amount)}")
    if record.shipping_amount is not None:
        print(
            "  Shipping: "
            f"{_format_money(record.currency, record.shipping_amount)}"
        )
    print(f"  Invoice total: {_format_money(record.currency, record.total_amount)}")
    if result.matched_details:
        print("  Matched details: " + "; ".join(result.matched_details))
    if result.differences:
        print("  Differences: " + "; ".join(result.differences))
    if result.unavailable_details:
        print("  Not recorded: " + "; ".join(result.unavailable_details))
    print(f"  Record: {record.record_id} ({record.document_reference})")
    print(f"  Source file: sample_data/{record.source_file}")
    try:
        invoice_check = compare_invoice_to_record(
            record, PROJECT_ROOT / "sample_data"
        )
    except InvoiceReadError as exc:
        print(f"  PDF-to-CSV check unavailable: {exc}")
        return

    print(
        "  PDF-to-CSV check: "
        f"{invoice_check.matched_count} consistent, "
        f"{invoice_check.mismatch_count} mismatched, "
        f"{invoice_check.unavailable_count} unavailable "
        f"across {invoice_check.page_count} page(s)."
    )
    for check in invoice_check.checks:
        if check.status == "MISMATCH":
            print(
                f"    REVIEW {check.label}: CSV={check.csv_value}; "
                f"PDF={check.pdf_value}"
            )
        elif check.status != "MATCH":
            print(f"    UNAVAILABLE {check.label}: {check.status.lower()}")


def _print_results(
    exact_matches: list[MatchResult],
    related_matches: list[MatchResult],
) -> None:
    if exact_matches:
        print("\nExact model match found:")
        for result in exact_matches:
            _print_result(result)
        return

    if not related_matches:
        print(
            "\nNo reliable match was found in the available purchase history. "
            "No current supplier price was checked. You can send the request "
            "to procurement for review."
        )
        return

    print("\nNo exact model match was found. Related historical records:")
    if not any(not result.differences for result in related_matches):
        print("None of the records shown meets every entered detail.")
    for result in related_matches:
        _print_result(result)


def main() -> int:
    try:
        records = load_purchase_history(PURCHASE_HISTORY_PATH)
    except PurchaseHistoryError as exc:
        print(f"Could not load purchase history: {exc}")
        return 1

    print("Procurement purchase-history search (prototype)")
    print("Data source: synthetic local CSV and text-based invoice PDFs.")
    print("All sample suppliers and prices are fictional.")
    print("Describe a laptop, for example:")
    print('  14-inch laptop with at least 16 GB RAM and 512 GB SSD')
    print("  Aarav Computing model AC14-16-512")
    description = input("\nLaptop request: ").strip()
    request = _extract_request(description, records)

    if request.model and not request.manufacturer:
        manufacturer = input(
            "Manufacturer for the model (press Enter if unknown): "
        ).strip()
        if manufacturer:
            request = replace(request, manufacturer=manufacturer)

    if not request.has_enough_detail:
        print(
            "\nI need more detail to make a useful comparison. Add an exact "
            "manufacturer and model, or at least two specifications such as "
            "screen size, minimum RAM, minimum storage, processor, or operating system."
        )
        additional_details = input("Additional laptop details (or press Enter to stop): ").strip()
        if additional_details:
            request = _merge_requests(
                request, _extract_request(additional_details, records)
            )
            if request.model and not request.manufacturer:
                manufacturer = input(
                    "Manufacturer for the model (press Enter if unknown): "
                ).strip()
                if manufacturer:
                    request = replace(request, manufacturer=manufacturer)

    if not request.has_enough_detail:
        print("\nNo search performed; the request still needs more detail.")
        return 0

    exact_matches, related_matches = search_laptops(records, request)
    _print_results(exact_matches, related_matches)
    print("\nReminder: historical prices are not current supplier offers.")
    return 0
