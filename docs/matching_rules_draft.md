# Purchase Match Rules — Draft

**Status:** Initial behavior proposal for the purchase-history search. Confirm and revise during analysis and testing.

## Goal

Help an employee find useful evidence from past purchases without presenting a merely similar product as an exact match or an old purchase price as a current quote.

## Result groups

1. **Exact model match** — same normalized manufacturer and model as the request, when both are known. Show these first.
2. **Similar product** — same broad product type with comparable specifications. Show relevant differences, such as less RAM or storage, a different processor, or a different warranty.
3. **Insufficient information** — request or purchase record lacks enough detail to judge comparability. Explain what is missing; do not label it an exact match.

## Matching behavior

- A shared product category or screen size by itself is not enough to call a laptop an exact match.
- Separate must-have requirements from preferences where the request provides that distinction.
- In the first prototype, ask for clarification unless the request contains an exact manufacturer/model pair or at least two useful specifications. This is a provisional usability rule, not a validated procurement standard.
- Do not infer an unknown specification from a product description or a similar record.
- Explain which attributes matched, differed, or were unavailable for every result shown.
- If no reliable match is found, say so and offer procurement review rather than inventing a result.

## Historical price display

- Display the purchase date and source document alongside every historical price.
- Label a past transaction price as **historical**, not as a current offer or guaranteed price.
- Do not silently adjust or extrapolate an old price to estimate today's price.
- No age cutoff is defined yet. Until procurement stakeholders agree on one, show the age/date clearly and leave the judgment to the user.
- Keep price comparisons fair by showing quantity, currency, tax, shipping, and other charges when those details are available.

## Example

For a request for a 14-inch laptop with 16 GB RAM and 512 GB storage:

- A past purchase of the same manufacturer and model is an exact model match.
- A 14-inch laptop with 8 GB RAM and 256 GB storage may be a similar product, but must be shown with those differences.
- A 14-inch laptop with no recorded RAM or storage is insufficiently described to determine whether it meets the request.
