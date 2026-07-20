# all models for API 

from pydantic import BaseModel

class SubmissionInput(BaseModel):
    tag: str
    asset_type: str
    system: str
    file_names: list[str]


class SubmissionOutput(BaseModel):
    asset: str
    status: str
    reason: str
    action: str
