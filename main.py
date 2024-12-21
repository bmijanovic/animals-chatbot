import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel




app = FastAPI()

class UserInput(BaseModel):
    question: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Animals Chatbot API"}


@app.post("/")
async def ask_question(request: UserInput):
    question = request.question
    return {"message": f"Your question was: {question}"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)