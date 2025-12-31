from pydantic import BaseModel

class DecorateResponse(BaseModel):
    image_base64: str
    explanation: str
