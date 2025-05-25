from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user, accounts,transactions,chat,help,sessions

app = FastAPI(
    title="Banking API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(help.router)


@app.get("/")
def read_root():
    return {"message": "Banking API is running"}
