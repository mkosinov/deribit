from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db: str


class ReadyResponse(BaseModel):
    status: str = "ready"
