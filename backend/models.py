# all models for API 

from pydantic import BaseModel
from typing import List

class SubmissionInput(BaseModel):
    tag: str
    asset_type: str
    system: str
    file_names: List[str]
    punch: str


class SubmissionOutput(BaseModel):
    asset: str
    status: str
    reason: str
    action: str