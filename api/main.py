from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import sys
import os
sys.path.append(os.getcwd())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")