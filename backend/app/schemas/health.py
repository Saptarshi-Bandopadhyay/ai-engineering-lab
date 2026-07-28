from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    project: str
    environment: str
    version: str
