# Synthetic purchase data

These files are fictional examples for development and demonstrations. Supplier names, product names, prices, invoice numbers, and transactions are invented. They are not market prices or real purchasing records.

## Files

- `purchase_history.csv` — spreadsheet-compatible purchase history with two records.
- `invoices/invoice_inv-2025-0042.pdf` and `invoices/invoice_inv-2024-0187.pdf` — fictional invoices corresponding to the purchase-history rows.

## Common record fields represented

The CSV includes the product description and specifications, supplier, quantity, unit price, currency, tax, shipping, total, purchase date, warranty, and a source filename. The invoice PDFs repeat key transaction fields so a later document-extraction step can compare extracted values with structured history.

Prices are illustrative only. These files are intended to test reading, normalization, matching, source tracking, and calculation checks—not to recommend a supplier or estimate Indian market prices.
