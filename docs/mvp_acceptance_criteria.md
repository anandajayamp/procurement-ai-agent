# MVP Acceptance Criteria — Draft

**Status:** CSV search milestone manually walked through; local text-PDF comparison is the next increment.

## Goal

Given a laptop purchase request and the synthetic purchase-history CSV, the tool finds and explains relevant prior purchase records. It does not place orders or make purchasing decisions.

## In scope

- Read the sample purchase-history CSV from local project data.
- Accept a laptop request as text or structured fields (the first implementation can use a simple developer input; no UI is required).
- Prototype clarification rule: require an exact manufacturer/model pair or at least two useful specifications before comparing. This is a starting assumption to revisit, not a procurement policy.
- Find exact model matches before similar laptop records.
- Explain which known product details match, differ, or are missing.
- Return historical prices with currency, purchase date, quantity, available taxes/charges, and source invoice reference.
- Extract embedded text from a referenced local invoice PDF and compare supported fields with the CSV record, reporting mismatches for human review.
- Ask for clarification when the request does not contain enough information for a useful comparison.
- Clearly report when no reliable match is found.

## Example acceptance scenarios

### 1. Exact model match

**Given** a request that specifies manufacturer `Aarav Computing` and model `AC14-16-512`,
**when** the tool searches the sample history,
**then** it returns `PH-2025-0042` as an exact model match,
**and** shows the supplier, purchase date, quantity, INR unit price, invoice total, and source invoice reference.

### 2. Similar product and visible differences

**Given** a request for a 14-inch laptop with at least 16 GB RAM and 512 GB storage but no model number,
**when** the tool searches the sample history,
**then** it may show both laptop records as candidates,
**and** it identifies `PH-2025-0042` as meeting the recorded RAM/storage requirements,
**and** calls out that `PH-2024-0187` has 8 GB RAM and 256 GB storage,
**and** does not describe either as an exact model match because the request did not specify a model.

### 3. Clarification for an underspecified request

**Given** a request that only says “I need a laptop,”
**when** the tool cannot tell which specifications matter for a useful comparison,
**then** it asks a focused question (for example, preferred screen size and minimum RAM/storage) before making a recommendation.

### 4. No reliable match

**Given** a request for a product or required specification not represented in the sample history,
**when** no sufficiently similar record can be supported by available data,
**then** the tool says no reliable match was found and does not invent one.

### 5. Historical price and source

**Given** any purchase record is shown,
**then** its price is labeled historical,
**and** the tool displays the purchase date and source invoice reference,
**and** it does not present that price as a current supplier offer.

## Out of scope for this increment

- OCR for scanned/image-only invoices and support for arbitrary vendor-specific invoice layouts.
- Live supplier or public market searches.
- Connecting to a company ERP, S2P system, database, or the developer's personal PostgreSQL database.
- Creating or sending requisitions or purchase orders.
- A chat or web user interface.

## Open questions before implementation

- Which request fields are mandatory versus optional?
- What match threshold should be used for similar products, beyond the explicit examples above?
- Should the first implementation accept free text, structured input, or both?
- What should happen if an invoice and its CSV row disagree?
