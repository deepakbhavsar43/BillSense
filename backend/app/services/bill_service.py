import json
from pathlib import Path
from uuid import uuid4

from app.schemas.bill import ParsedBill, StoredBillRecord
from app.services.genai_service import genai_service
from app.services.storage_service import storage_service

TRANSCRIPTION_PROMPT = """
You are reading a purchase bill image.
Transcribe every visible piece of useful bill information as faithfully as possible.
Rules:
- Preserve item lines, totals, taxes, discounts, bill numbers, date/time, merchant details, and payment information.
- Do not summarize.
- Do not invent missing text.
- If a value is unclear, keep the ambiguous text as-is instead of guessing.
""".strip()

STRUCTURED_PARSE_PROMPT = """
Convert the following bill transcription into structured JSON.
Rules:
- Return only data supported by the transcription.
- Use null for missing scalar fields.
- Use an empty list for missing items or notes.
- Keep monetary values numeric without currency symbols.
- Populate tax_breakdown with all tax components when present (for example: CGST, SGST, IGST, GST, VAT, cess, service tax).
- Include separate tax_breakdown entries for product-level taxes and other charge-level taxes (delivery, packing, service charges, fees, etc.).
- For each tax_breakdown entry, fill applies_to and reference when the bill indicates where that tax was applied.
- Put extraction caveats into notes.
- Set raw_text to null. The backend will store the full transcription.

Bill transcription:
{transcript}
""".strip()

QUESTION_ANSWER_SYSTEM_PROMPT = """
You answer questions only from parsed bill data provided by the user.
Rules:
- Use only the supplied bill JSON.
- If the answer is not present, say that the information is not available in the extracted bill.
- Keep answers concise and factual.
""".strip()


class BillService:
    async def parse_bill_image(self, file_bytes: bytes, mime_type: str) -> ParsedBill:
        transcript = await genai_service.generate_from_image(
            image_bytes=file_bytes,
            mime_type=mime_type,
            prompt=TRANSCRIPTION_PROMPT,
            temperature=0.1,
            max_tokens=4096,
        )
        payload = await genai_service.generate_json(
            prompt=STRUCTURED_PARSE_PROMPT.format(transcript=transcript),
            response_json_schema=ParsedBill.model_json_schema(),
            temperature=0.0,
            max_tokens=4096,
        )
        if not payload.get("raw_text"):
            payload["raw_text"] = transcript
        return ParsedBill.model_validate(payload)

    async def parse_and_store(
        self,
        file_bytes: bytes,
        file_name: str,
        mime_type: str,
    ) -> StoredBillRecord:
        bill_id = str(uuid4())
        suffix = Path(file_name).suffix or ".img"
        source_image_path = storage_service.save_upload(bill_id, suffix, file_bytes)
        parsed_bill = await self.parse_bill_image(file_bytes, mime_type)
        return storage_service.save_parsed_bill(
            bill=parsed_bill,
            bill_id=bill_id,
            source_file_name=file_name,
            source_media_type=mime_type,
            source_image_path=source_image_path,
        )

    async def answer_question(self, bill_id: str, question: str) -> str:
        record = storage_service.load_record(bill_id)
        prompt = (
            "Answer the question using this parsed bill JSON only.\n\n"
            f"Bill JSON:\n{json.dumps(record.bill.model_dump(mode='json'), indent=2)}\n\n"
            f"Question: {question}"
        )
        return await genai_service.generate(
            prompt=prompt,
            system_prompt=QUESTION_ANSWER_SYSTEM_PROMPT,
            temperature=0.0,
            max_tokens=512,
        )


bill_service = BillService()
