from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.bill import ParsedBill, StoredBillRecord
from app.services.bill_service import bill_service
from app.services.genai_service import genai_service
from app.services.storage_service import storage_service

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint(monkeypatch) -> None:
    async def fake_generate(*args, **kwargs) -> str:
        return "Hello from Gemini"

    monkeypatch.setattr(genai_service, "generate", fake_generate)

    response = client.post(
        "/api/v1/chat",
        json={"prompt": "Hi"},
    )

    assert response.status_code == 200
    assert response.json() == {"text": "Hello from Gemini", "provider": "gemini"}


def test_parse_bill_endpoint(monkeypatch) -> None:
    record = StoredBillRecord(
        bill_id="bill-123",
        source_file_name="bill.jpg",
        source_media_type="image/jpeg",
        source_image_path="data/uploads/bill-123.jpg",
        parsed_at=datetime(2026, 3, 22, 12, 0, 0),
        bill=ParsedBill(
            merchant_name="Store",
            total=42.5,
            items=[],
            notes=[],
            raw_text="Store Total 42.5",
        ),
    )

    async def fake_parse_and_store(*args, **kwargs) -> StoredBillRecord:
        return record

    monkeypatch.setattr(bill_service, "parse_and_store", fake_parse_and_store)

    response = client.post(
        "/api/v1/bills/parse",
        files={"file": ("bill.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["bill_id"] == "bill-123"
    assert response.json()["bill"]["merchant_name"] == "Store"


def test_get_bill_endpoint(monkeypatch) -> None:
    record = StoredBillRecord(
        bill_id="bill-123",
        source_file_name="bill.jpg",
        source_media_type="image/jpeg",
        source_image_path="data/uploads/bill-123.jpg",
        parsed_at=datetime(2026, 3, 22, 12, 0, 0),
        bill=ParsedBill(
            merchant_name="Store",
            total=42.5,
            items=[],
            notes=[],
            raw_text="Store Total 42.5",
        ),
    )

    monkeypatch.setattr(storage_service, "load_record", lambda bill_id: record)

    response = client.get("/api/v1/bills/bill-123")

    assert response.status_code == 200
    assert response.json()["bill"]["total"] == 42.5


def test_bill_query_endpoint(monkeypatch) -> None:
    async def fake_answer_question(*args, **kwargs) -> str:
        return "The total is 42.5"

    monkeypatch.setattr(bill_service, "answer_question", fake_answer_question)

    response = client.post(
        "/api/v1/bills/bill-123/query",
        json={"question": "What is the total?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "bill_id": "bill-123",
        "answer": "The total is 42.5",
        "provider": "gemini",
    }


def test_bill_export_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(storage_service, "export_bill", lambda bill_id: "data/exports/bill-123.json")

    response = client.post("/api/v1/bills/bill-123/export")

    assert response.status_code == 200
    assert response.json() == {
        "bill_id": "bill-123",
        "export_path": "data/exports/bill-123.json",
    }
