from pydantic import BaseModel


class UserModelSchema(BaseModel):
    tg_id: str
    username: str
    role: str