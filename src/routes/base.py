from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
    
)

@base_router.get("/")
def welcome():
    app_name = os.getenv("APP_NAME", "mini-RAG")
    app_version = os.getenv("APP_VERSION", "1.0.0") 
    return {"message": f"Welcome to the {app_name} (v{app_version})!"}
