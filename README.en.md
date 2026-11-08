# Invoice / Document Extractor

*Türkçe: [README.md](README.md)*

**Live demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo), tab: 🧾 Fatura Ayıklayıcı. The demo runs on OpenAI gpt-5.4-mini; the business logic is the same as in this repo.

In accounting, someone spends the day opening PDF invoices and copying the seller, buyer, line items and totals by hand. This service takes a PDF invoice and turns it into **checked, structured data** (JSON). It combines a local model, rule-based reading and math checks. The data never leaves the computer.

## How it works
```
PDF → text (pdfplumber) → ┬─ Model: extracts line items, amounts and date in a fixed format (JSON schema)
                          └─ Rules: read clearly labeled fields (Issuer, Customer, Tax ID, totals)
                       → merge (rules win on labeled fields) → check → approved / needs review
```
**Checks:** tax ID has 10 digits · date format · quantity × unit price = amount · line items add up to the subtotal · subtotal × VAT rate = VAT · subtotal + VAT = grand total · seller is not the same as buyer.

## Results (12 sample invoices, 2 different layouts)
| Version | All fields correct | Wrong readings caught |
|---|---|---|
| v1: everything in the model | 1/12 | 1/11 |
| **v2: model + rules + checks** | **10/12** | **2/2** |

## What broke, and how I fixed it

**1. In the first version I left everything to the model.** Only 1 of 12 invoices came out with all fields correct. The scary part: **10 of the 11 wrongly read invoices passed the checks as "approved".** Bad data would have gone silently into the books.

**2. Looking field by field showed the cause.** I measured each field's accuracy separately ([v1 report](eval/RAPOR_v1_sadece_llm.md)). Invoice number, date and VAT rate were 12/12. But the seller name was 5/12 and the buyer name 2/12. The errors weren't random: the small model (3B) **was swapping the seller and the buyer.** The amounts stayed consistent, so the total checks couldn't see it.

**3. I split the job.**
- I read the clearly labeled fields ("Issuer", "Customer", "Tax ID", totals) **with rules**. On those fields, rules override the model.
- I gave the model only the really hard part: the line-item table.
- The math checks stayed as the last gate. Once reading improved, catching errors went from 1/11 to 2/2.

| | v1: everything in the model | v2: model + rules + checks |
|---|---|---|
| All fields correct | 1/12 | **10/12** |
| Seller / buyer name | 5/12 · 2/12 | **12/12 · 12/12** |
| Wrong but passed as "approved" | **10** | **0** |

The 2 remaining errors were in the line-item table; both were caught by the checks and sent to a human as "needs review". There is also one false alarm: invoice_01 was read correctly but still went to review. That is a deliberate choice; if the system is going to be wrong, it is wrong on the careful side.

**Lesson:** I gave the model the job it is good at (reading tables whose layout changes) and gave rules the job that can be done exactly with rules. For me the most important measure wasn't accuracy, but **that bad data never passes silently.**

Detailed report: [eval/RAPOR.md](eval/RAPOR.md)

## Running it
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
python ornekler/uret.py          # generates sample invoices (made-up data)
uvicorn app.main:app --reload    # http://localhost:8000 → drag and drop a PDF
python eval/degerlendir.py       # accuracy report
pytest
```

## Tech
Python · FastAPI · Ollama (qwen2.5:3b, output with a JSON schema) · Pydantic · pdfplumber · reportlab · pytest

> The sample invoices are made-up documents generated for evaluation.

---
Built by **Emirhan Karaca**
