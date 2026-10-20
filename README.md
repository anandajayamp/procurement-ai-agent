# Procurement Purchase Request Assistant

An early, local prototype for researching previous laptop purchases. The goal is to grow this into a reusable tool that companies can connect to their own purchase records.

## Run the first prototype

Requires Python 3.12. The local virtual environment is in `.venv/` (it is excluded from Git).

Activate the environment on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the PDF-reading dependency:

```bash
python -m pip install -r requirements.txt
```

From the project root, run:

```bash
python3 -m procurement_assistant
```

Try one of these example requests:

```text
14-inch laptop with at least 16 GB RAM and 512 GB SSD
Aarav Computing model AC14-16-512
```

The tool reads `sample_data/purchase_history.csv` and prints exact model matches or related historical records, with differences, purchase dates, prices, and invoice source references. For each result, it extracts text from the referenced local invoice PDF and reports fields that agree or differ from the CSV.

## Current limitations

- The sample suppliers, products, and prices are fictional and for software demonstration only.
- Search is a small deterministic prototype. It is not an LLM agent and does not use a vector database.
- Invoice parsing currently supports text-based PDFs and the layout of the synthetic examples. Scanned invoices are not OCR-processed.
- Extracted PDF values are compared with the CSV for review. They do not update or override the CSV record.
- Prices are historical. The tool does not search current supplier offers, place orders, or connect to an ERP/S2P system or cloud database.
- Laptop descriptions and invoice fields are interpreted using simple text patterns; other company invoice layouts may not be understood.

## Project notes

- [Initial requirements](requirement_doc.md)
- [Common purchase record draft](docs/common_purchase_record_draft.md)
- [Purchase match rules](docs/matching_rules_draft.md)
- [MVP acceptance criteria](docs/mvp_acceptance_criteria.md)
- [Editable system design diagram](docs/system_design_mvp.drawio)
