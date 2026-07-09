"""FastAPI app entrypoint. Routes only — business logic lives in services/."""

from fastapi import FastAPI, UploadFile, File, HTTPException

from schemas.resume import ParsedResume
from services import resume_parser

app = FastAPI(title="ML Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse-resume", response_model=ParsedResume)
async def parse_resume(file: UploadFile = File(...)):
    content = await file.read()
    try:
        return resume_parser.parse(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))