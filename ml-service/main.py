"""FastAPI app entrypoint. Routes only — business logic lives in services/."""

from fastapi import FastAPI, UploadFile, File, HTTPException

from schemas.resume import ParsedResume
from schemas.posting import PostingInput, ParsedPosting
from schemas.match import MatchInput, MatchResult
from schemas.gap import GapAnalysisInput, GapAnalysisResult
from services import resume_parser, posting_parser, matcher, gap_analyzer

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


@app.post("/parse-posting", response_model=ParsedPosting)
async def parse_posting(payload: PostingInput):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    return posting_parser.parse(payload.text)

@app.post("/match", response_model=MatchResult)
async def match(payload: MatchInput):
    try:
        return matcher.match(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gap-analysis", response_model=GapAnalysisResult)
async def gap_analysis(payload: GapAnalysisInput):
    try:
        return gap_analyzer.analyze(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))