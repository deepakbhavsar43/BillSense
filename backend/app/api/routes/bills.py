from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.bill import BillExportResponse, BillQuestionRequest, BillQuestionResponse, StoredBillRecord
from app.services.bill_service import bill_service
from app.services.storage_service import storage_service

router = APIRouter()


@router.post("/bills/parse", response_model=StoredBillRecord)
async def parse_bill(file: UploadFile = File(...)) -> StoredBillRecord:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded bill image is empty.")

    try:
        return await bill_service.parse_and_store(
            file_bytes=file_bytes,
            file_name=file.filename or "bill-image",
            mime_type=file.content_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/bills/{bill_id}", response_model=StoredBillRecord)
async def get_bill(bill_id: str) -> StoredBillRecord:
    try:
        return storage_service.load_record(bill_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/bills/{bill_id}/query", response_model=BillQuestionResponse)
async def query_bill(bill_id: str, payload: BillQuestionRequest) -> BillQuestionResponse:
    try:
        answer = await bill_service.answer_question(bill_id=bill_id, question=payload.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return BillQuestionResponse(bill_id=bill_id, answer=answer, provider="gemini")


@router.post("/bills/{bill_id}/export", response_model=BillExportResponse)
async def export_bill_json(bill_id: str) -> BillExportResponse:
    try:
        export_path = storage_service.export_bill(bill_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BillExportResponse(bill_id=bill_id, export_path=export_path)
