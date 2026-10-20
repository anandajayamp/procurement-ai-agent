PURCHASE REQUEST ASSISTANT — INITIAL ANALYSIS

Status: Discovery in progress; initial choices are recorded below.

1. Problem idea

When an employee requests a product, the organization may need to determine whether it has bought a similar product before, identify suitable suppliers, compare prices and terms, and prepare the next purchasing document. Doing this research manually can take time and make comparisons difficult to audit.

2. Proposed first workflow

Input: An employee describes what they need, for example, “a laptop with a 14-inch display.” The initial intended user is the employee making the request. The purchasing context is India, with INR as the currency.

The assistant would:
- clarify missing or ambiguous product details;
- search the organization's purchase records for similar products and prior prices;
- in a later stage, find current supplier offers and public market listings from approved, traceable sources;
- compare offers using comparable specifications and total cost (including shipping, taxes, warranty, and delivery where available);
- show source links, dates, assumptions, and a concise comparison;
- explain that a public listing is only a reference and may not be an organization's actual quote or contracted price;
- present the research to the employee and, where needed, route it to procurement for review.

Data-source decision: The longer-term goal is to search purchase orders, invoices, supplier catalogs, and other available records. We have not yet confirmed which of these records exist or their formats. Start development with a small, clearly labeled sample dataset; add real source types one at a time after we understand their structure and quality.

Comparison decision: Do not make live market searches a dependency for the first working version. First establish reliable internal purchase-history search. Then add current supplier quotes or catalogs, followed by public market listings if we can retrieve stable source links and show when each price was observed. This keeps comparisons explainable and prevents unsupported prices from appearing authoritative.

Incomplete or unsupported requests: Ask the employee focused questions when required product details are missing. If the assistant still cannot find comparable, current, or trustworthy evidence, it must say what is missing, avoid inventing a match or price, and offer to send the request to procurement for help.

Possible later capability: prepare a purchase requisition or purchase order draft for a person to review and approve. The initial version should not commit spend or send an order automatically.

3. Important distinctions to confirm

- A previous purchase does not tell us whether the item is currently in stock internally. Checking inventory would require a separate, reliable inventory source.
- “14-inch monitor” could mean a laptop with a 14-inch screen or a laptop plus a separate monitor. The assistant must ask before comparing products.
- A lower listed price is not automatically the better offer. Specifications, quantity, currency, taxes, shipping, warranty, delivery, and supplier status can change the comparison.
- Public market listings may not be directly comparable to contracted or organization-specific supplier quotes.

4. Initial boundaries

- Focus: employee purchase-request research and comparison, initially using internal purchase history.
- Human role: employees provide request details; procurement staff verify comparisons and make purchasing decisions.
- Not in the first version: automatic purchase orders, supplier negotiation, or payment.

5. First version (MVP) agreement

- Input: an employee's purchase request, initially using a laptop request as the example.
- Main outcome: search internal purchase records for similar items and show the matching item details, supplier, price, purchase date, and source record when available.
- If required request details are missing, ask the employee focused clarification questions.
- If no reliable match is found, say so clearly and offer to send the request to procurement for review.
- Current supplier quotes and public market comparisons are later capabilities, after the internal-history workflow is understood and working.
- The MVP provides research only. It does not place orders, create commitments, or approve spend.

6. Draft data fields for the laptop example

These are starting assumptions for analysis, not a finalized schema. Actual records may contain different fields or use different names.

Employee request fields:
- product type (laptop);
- intended use or business purpose;
- required specifications, where known: brand preference, screen size, processor, memory (RAM), storage, and operating system;
- quantity;
- requested delivery date or urgency;
- delivery location, if it affects availability or cost;
- budget or estimated budget, if known.

Historical purchase record fields:
- product description, manufacturer, and model, where recorded;
- specifications, where recorded: screen size, processor, RAM, storage, and operating system;
- supplier name;
- quantity and unit price;
- currency (expected INR for the initial context);
- taxes and other charges, if available;
- purchase date;
- purchase order or invoice reference/source record;
- warranty and delivery details, if available.

Matching note: The assistant should distinguish required specifications from preferences. It should explain which fields matched, which were missing, and any meaningful differences instead of treating a textually similar description as an exact match. Price comparisons should account for quantity, currency, taxes, and other charges when that information is available.

7. Questions for discovery — answered so far

1. First intended user: employee making the request.
2. Purchasing context: India; currency: INR.
3. Desired records over time: purchase orders, invoices, supplier catalogs, and other available sources; the actual data formats are not yet known.
4. Comparison scope: both similar past purchases and supplier price comparisons. Build in stages: start with internal purchase history, then add current supplier offers and market references from approved, traceable sources.
5. Missing details or weak evidence: ask focused questions; if evidence remains unreliable or absent, explain the gap and offer procurement review.

8. Next discovery questions

1. Which request details should be mandatory before searching, and which should be optional?
2. Do you have access to any example purchase records, even a few anonymized rows or a spreadsheet? Do not share confidential supplier or employee information here.
3. Are any of the draft fields above irrelevant or missing for your intended use?
