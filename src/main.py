from fastapi import FastAPI
from src.routes import base
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI()
app.include_router(base.base_router)