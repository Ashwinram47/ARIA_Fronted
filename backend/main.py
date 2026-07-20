# fastapi and routing

import os
import logging
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import SubmissionInput, SubmissionOutput
from evaluation import evaluate_submission
from explain import explain_evaluation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Asset Document Checker", version="1.0")

# CORS configuration
# Adjust origins to the specific frontend origins in production.
origins: List[str] = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # remove or restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"status": "ok", "service": "Asset Document Checker"}


@app.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_endpoint(payload: SubmissionInput):
    """
    Accepts SubmissionInput JSON and returns the evaluation dictionary.
    This endpoint only runs the deterministic evaluation (no LLM calls).
    """
    try:
        eval_dict = evaluate_submission(payload)
        return eval_dict
    except Exception as exc:
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/explain", response_model=SubmissionOutput)
async def explain_endpoint(evaluation_dict: Dict[str, Any]):
    """
    Accepts an evaluation dictionary (the output of evaluate_submission)
    and returns a SubmissionOutput after calling the explain logic (LLM + fallback).
    """
    try:
        result = explain_evaluation(evaluation_dict)
        return result
    except Exception as exc:
        logger.exception("Explain failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/process", response_model=SubmissionOutput)
async def process_endpoint(payload: SubmissionInput):
    """
    Convenience endpoint that accepts the frontend SubmissionInput,
    runs evaluation, then runs explain and returns SubmissionOutput.
    """
    try:
        eval_dict = evaluate_submission(payload)
        result = explain_evaluation(eval_dict)
        return result
    except Exception as exc:
        logger.exception("Processing failed")
        raise HTTPException(status_code=500, detail=str(exc))


# Optional: health check endpoint
@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse(status_code=200, content={"healthy": True})
