# BillSense - AI-Powered Bill Processing API

Businesses and individuals deal with large volumes of physical and digital bills that require manual data entry, are difficult to search, and cannot be queried programmatically. BillSense solves this by using Gemini's multimodal AI to automatically extract structured data from bill images, make that data queryable in natural language, and export it as clean JSON — eliminating manual transcription and enabling downstream automation.

## Features

- Upload a bill image → instant structured JSON extraction via Gemini multimodal
- Query any parsed bill in natural language ("What is the tax amount?")
- Export clean bill JSON to disk for downstream processing
- General AI chat panel for expense and billing questions
- React + Vite + Tailwind frontend with drag-and-drop upload, bill list, and inline Q&A
- FastAPI backend with versioned routes, CORS, and Pydantic schemas
- Local persistence — parsed bills, uploaded images, and exports stored in `backend/data/`

## Documentation

- Backend walkthrough: [backend/README_BACKEND.md](backend/README_BACKEND.md)

## Project Structure

```text
.
├── backend/                    # FastAPI + Gemini API
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── bills.py
│   │   │   ├── genai.py
│   │   │   └── health.py
│   │   ├── core/config.py
│   │   ├── schemas/
│   │   │   ├── bill.py
│   │   │   ├── genai.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── bill_service.py
│   │   │   ├── genai_service.py
│   │   │   └── storage_service.py
│   │   └── main.py
│   ├── data/
│   │   ├── exports/
│   │   ├── parsed_bills/
│   │   └── uploads/
│   ├── tests/test_api.py
│   ├── .env.example
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/                   # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/
│   │   │   ├── BillCard.jsx
│   │   │   ├── BillInteract.jsx
│   │   │   ├── BillList.jsx
│   │   │   ├── BillUpload.jsx
│   │   │   └── ChatPanel.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Quick Start

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set GEMINI_API_KEY
fastapi dev app/main.py
```

API will be live at `http://localhost:8000`.

- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App opens at `http://localhost:3000`. The Vite dev server proxies all `/api` calls to the backend automatically — no manual CORS setup needed.

## API Endpoints

- `POST /api/v1/chat`: general conversation
- `POST /api/v1/generate`: alias of chat for backward compatibility
- `POST /api/v1/bills/parse`: upload a bill image and extract a structured bill JSON record
- `GET /api/v1/bills/{bill_id}`: fetch a previously parsed bill
- `POST /api/v1/bills/{bill_id}/query`: ask questions against extracted bill data
- `POST /api/v1/bills/{bill_id}/export`: save the extracted bill JSON into `data/exports`

## Example Requests

Chat:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, what can you do?",
    "temperature": 0.5,
    "max_tokens": 120
  }'
```

Parse a bill image:

```bash
curl -X POST http://localhost:8000/api/v1/bills/parse \
  -F "file=@sample-bill.jpg"
```

Query a parsed bill:

```bash
curl -X POST http://localhost:8000/api/v1/bills/<bill_id>/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total amount?"}'
```

Export parsed JSON:

```bash
curl -X POST http://localhost:8000/api/v1/bills/<bill_id>/export
```

## Bill Schema

The extracted bill JSON contains these top-level fields:

- `merchant_name`
- `merchant_address`
- `merchant_phone`
- `bill_number`
- `invoice_number`
- `purchase_date`
- `purchase_time`
- `currency`
- `subtotal`
- `tax`
- `tax_breakdown[]` (CGST/SGST/IGST/cess and other component taxes)
- `discount`
- `total`
- `payment_method`
- `items[]`
- `notes[]`
- `raw_text`

## Run Tests

```bash
pytest -q
```

## Notes

- The template uses the official Google GenAI SDK via `google-genai`.
- Default model is `gemini-2.5-flash`, configurable through `GEMINI_MODEL`.
- Bills are saved under `data/parsed_bills`, uploaded images under `data/uploads`, and exported JSON under `data/exports`.
- The parser uses a transcription-first flow before structured normalization to improve extraction reliability.

