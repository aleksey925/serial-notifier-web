from pydantic.main import BaseModel


class ErrorResp(BaseModel):
    message: str
