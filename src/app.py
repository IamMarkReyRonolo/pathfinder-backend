import sys, os, pdb, json, imp, re, math
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from fastapi import FastAPI
from router import user
from fastapi.middleware.cors import CORSMiddleware
from db.connection import create_db_and_tables

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user.routes)

@app.on_event("startup")
async def on_startup():         
    create_db_and_tables()

@app.get('/ping')
def ping_server():
    return { "message": "Server is up!!!"}
