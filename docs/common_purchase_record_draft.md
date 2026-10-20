# Common Purchase Record — Draft

**Status:** Initial design draft for the synthetic laptop examples. Review and revise before treating this as a final data contract.

## Purpose

Different companies may provide purchase information as spreadsheets, invoices, or database records. The tool should convert each source into a common record so it can search and compare purchases consistently while retaining a path back to the original evidence.

## Record shape

Use one record per purchased line item. A single invoice can contain multiple lines, so invoice-level details (supplier, invoice number, date, currency) may be shared by several item records.

| Group | Fields | Notes |
|---|---|---|
| Identity | `record_id`, `company_id` | `record_id` identifies the normalized line. `company_id` keeps each customer's data isolated. |
| Source | `source_type`, `source_reference`, `source_location`, `extraction_status`, `extraction_notes` | Preserve the originating file/record and location, such as invoice page or spreadsheet row. Track uncertain extraction. |
| Document | `document_type`, `document_number`, `document_date` | Examples: invoice, purchase order, goods receipt. Keep the document date as recorded. |
| Supplier | `supplier_name`, `supplier_identifier` | Identifier is optional and depends on what the company provides. |
| Product | `item_description`, `manufacturer`, `model`, `category` | Preserve the original description as well as normalized fields. |
| Specifications | `screen_size_in`, `processor`, `ram_gb`, `storage_gb`, `operating_system`, `warranty_months` | Product-specific fields are optional. Do not infer a missing specification as fact. |
| Quantity | `quantity`, `unit_of_measure` | Keep quantity separate from unit price and invoice totals. |
| Price | `currency`, `unit_price_ex_tax`, `tax_rate_percent`, `tax_amount`, `shipping_amount`, `other_charges`, `line_total` | Store monetary amounts as decimal values, never floating-point approximations. Preserve reported amounts and calculate checks separately. |
| Timing | `purchase_date`, `delivery_date` | A purchase date and a delivery date are different facts. Delivery may be unknown. |

## Field and evidence rules

- Keep the original value and source alongside normalized values where practical. For example, preserve the exact product description from the invoice even after extracting manufacturer and model.
- Unknown information should be `null` or marked unknown; do not fill gaps with guesses.
- Store currency on every monetary record. Do not assume INR for another company's records just because the demo uses INR.
- Keep purchase records distinct from current supplier quotes and public market listings. They have different source types and dates and should not be presented as equivalent evidence.
- Track extraction confidence or review status for values taken from PDFs. A value with low confidence should be checked by a person before it is used in a comparison.
- Retain source references so a user can inspect the source file and the relevant page or row.
- Treat company-specific identifiers and supplier names as belonging to that company's data only.

## Mapping of the synthetic examples

The CSV fields and their invoice counterparts map as follows:

| Common field | CSV column | Invoice text |
|---|---|---|
| `document_type` | `document_type` | Invoice heading / document type |
| `document_number` | `document_reference` | Invoice number |
| `document_date` / `purchase_date` | `purchase_date` | Invoice date |
| `supplier_name` | `supplier_name` | Supplier |
| `item_description` | `item_description` | Item |
| `manufacturer`, `model` | `manufacturer`, `model` | Manufacturer and model |
| Product specifications | `screen_size_in`, `processor`, `ram_gb`, `storage_gb`, `operating_system` | Specifications / operating system |
| `quantity` | `quantity` | Quantity |
| `currency` | `currency` | Currency |
| Price and charges | `unit_price_ex_tax_inr`, `tax_rate_percent`, `tax_amount_inr`, `shipping_amount_inr`, `total_amount_inr` | Unit price, subtotal, GST, shipping, invoice total |
| `warranty_months` | `warranty_months` | Warranty |
| `source_reference` | `source_file` | Invoice file and page |

## Open design questions

1. Should records be retained as individual source facts with a normalized view, or only as normalized records plus links to source documents?
2. Which company identifiers and access rules are needed when multiple customers use the tool?
3. Which product specification fields should be generic across categories, and which should be category-specific?
4. Should a user be able to correct extracted values, and how should the original and corrected values be audited?
5. Which date should drive price freshness: invoice date, purchase order date, or delivery date? The source dates should remain separately available regardless.
