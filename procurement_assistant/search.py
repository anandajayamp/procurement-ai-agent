"""Deterministic laptop matching for the first prototype."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from .data import PurchaseRecord


@dataclass(frozen=True)
class LaptopRequest:
    manufacturer: str | None = None
    model: str | None = None
    screen_size_in: Decimal | None = None
    min_ram_gb: int | None = None
    min_storage_gb: int | None = None
    processor: str | None = None
    operating_system: str | None = None

    @property
    def exact_model_search(self) -> bool:
        return bool(self.manufacturer and self.model)

    @property
    def specification_count(self) -> int:
        return sum(
            value is not None
            for value in (
                self.screen_size_in,
                self.min_ram_gb,
                self.min_storage_gb,
                self.processor,
                self.operating_system,
            )
        )

    @property
    def has_enough_detail(self) -> bool:
        # This first prototype asks for two useful requirements, or an exact
        # manufacturer/model pair, before comparing the laptop records.
        return self.exact_model_search or self.specification_count >= 2


@dataclass(frozen=True)
class MatchResult:
    record: PurchaseRecord
    label: str
    matched_details: tuple[str, ...]
    differences: tuple[str, ...]
    unavailable_details: tuple[str, ...]
    sort_key: tuple[int, int, int]


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def search_laptops(
    records: list[PurchaseRecord], request: LaptopRequest
) -> tuple[list[MatchResult], list[MatchResult]]:
    """Return exact model results and related records, most relevant first."""
    laptop_records = [
        record for record in records if "laptop" in record.item_description.casefold()
    ]

    exact_matches: list[MatchResult] = []
    if request.exact_model_search:
        exact_matches = [
            _exact_result(record)
            for record in laptop_records
            if normalize_text(record.manufacturer or "")
            == normalize_text(request.manufacturer or "")
            and normalize_text(record.model or "") == normalize_text(request.model or "")
        ]
        if exact_matches:
            exact_matches.sort(key=lambda item: item.sort_key, reverse=True)
            return exact_matches, []

    related: list[MatchResult] = []
    for record in laptop_records:
        matches, differences, unavailable = _compare_details(record, request)
        if not matches:
            continue

        if differences:
            label = "Related past purchase (does not meet every entered detail)"
        elif unavailable:
            label = "Potentially similar (some requested details are not recorded)"
        else:
            label = "Similar product (meets the entered specifications)"

        related.append(
            MatchResult(
                record=record,
                label=label,
                matched_details=tuple(matches),
                differences=tuple(differences),
                unavailable_details=tuple(unavailable),
                sort_key=(len(matches), -len(differences), record.purchase_date.toordinal()),
            )
        )

    related.sort(key=lambda item: item.sort_key, reverse=True)
    return [], related


def _exact_result(record: PurchaseRecord) -> MatchResult:
    return MatchResult(
        record=record,
        label="Exact model match",
        matched_details=(f"{record.manufacturer} {record.model}",),
        differences=(),
        unavailable_details=(),
        sort_key=(1, 0, record.purchase_date.toordinal()),
    )


def _compare_details(
    record: PurchaseRecord, request: LaptopRequest
) -> tuple[list[str], list[str], list[str]]:
    matches: list[str] = []
    differences: list[str] = []
    unavailable: list[str] = []

    if request.manufacturer:
        if not record.manufacturer:
            unavailable.append("Manufacturer is not recorded")
        elif normalize_text(record.manufacturer) == normalize_text(request.manufacturer):
            matches.append(f"Manufacturer: {record.manufacturer}")
        else:
            differences.append(f"Different manufacturer: {record.manufacturer}")

    if request.model:
        if not record.model:
            unavailable.append("Model is not recorded")
        elif normalize_text(record.model) == normalize_text(request.model):
            matches.append(f"Model: {record.model}")
        else:
            differences.append(f"Different model: {record.model}")

    if request.screen_size_in is not None:
        if record.screen_size_in is None:
            unavailable.append("Screen size is not recorded")
        elif record.screen_size_in == request.screen_size_in:
            matches.append(f"Screen size: {record.screen_size_in} in")
        else:
            differences.append(f"Screen size: {record.screen_size_in} in")

    if request.min_ram_gb is not None:
        if record.ram_gb is None:
            unavailable.append("RAM is not recorded")
        elif record.ram_gb >= request.min_ram_gb:
            matches.append(f"RAM: {record.ram_gb} GB (meets minimum)")
        else:
            differences.append(
                f"RAM: {record.ram_gb} GB (below requested minimum "
                f"{request.min_ram_gb} GB)"
            )

    if request.min_storage_gb is not None:
        if record.storage_gb is None:
            unavailable.append("Storage is not recorded")
        elif record.storage_gb >= request.min_storage_gb:
            matches.append(
                f"Storage: {record.storage_gb} GB (meets minimum)"
            )
        else:
            differences.append(
                f"Storage: {record.storage_gb} GB (below requested minimum "
                f"{request.min_storage_gb} GB)"
            )

    if request.processor:
        if not record.processor:
            unavailable.append("Processor is not recorded")
        elif normalize_text(request.processor) in normalize_text(record.processor):
            matches.append(f"Processor: {record.processor}")
        else:
            differences.append(f"Processor: {record.processor}")

    if request.operating_system:
        if not record.operating_system:
            unavailable.append("Operating system is not recorded")
        elif normalize_text(request.operating_system) in normalize_text(
            record.operating_system
        ):
            matches.append(f"Operating system: {record.operating_system}")
        else:
            differences.append(f"Operating system: {record.operating_system}")

    return matches, differences, unavailable
