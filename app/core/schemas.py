from pydantic import BaseModel


class UserInput(BaseModel):
    question: str