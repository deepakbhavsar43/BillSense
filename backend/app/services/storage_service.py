import json
from pathlib import Path

from app.core.config import settings
from app.schemas.bill import ParsedBill, StoredBillRecord


class BillStorageService:
    def __init__(self) -> None:
        self.parsed_bills_dir = Path(settings.parsed_bills_dir)
        self.exports_dir = Path(settings.exports_dir)
        self.uploads_dir = Path(settings.uploads_dir)
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.parsed_bills_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, bill_id: str, suffix: str, content: bytes) -> str:
        safe_suffix = suffix if suffix.startswith(".") else f".{suffix}" if suffix else ".bin"
        path = self.uploads_dir / f"{bill_id}{safe_suffix.lower()}"
        path.write_bytes(content)
        return str(path)

    def save_record(self, record: StoredBillRecord) -> str:
        path = self.parsed_bills_dir / f"{record.bill_id}.json"
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        return str(path)

    def load_record(self, bill_id: str) -> StoredBillRecord:
        path = self.parsed_bills_dir / f"{bill_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Bill '{bill_id}' was not found.")
        return StoredBillRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def export_bill(self, bill_id: str) -> str:
        record = self.load_record(bill_id)
        path = self.exports_dir / f"{bill_id}.json"
        payload = record.bill.model_dump(mode="json")
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path)

    def save_parsed_bill(self, bill: ParsedBill, bill_id: str, source_file_name: str, source_media_type: str, source_image_path: str) -> StoredBillRecord:
        record = StoredBillRecord(
            bill_id=bill_id,
            source_file_name=source_file_name,
            source_media_type=source_media_type,
            source_image_path=source_image_path,
            parsed_at=__import__("datetime").datetime.utcnow(),
            bill=bill,
        )
        self.save_record(record)
        return record


storage_service = BillStorageService()
