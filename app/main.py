from fastapi import FastAPI
from app.api.routes import auth, tickets, messages

app = FastAPI()

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(messages.router)
