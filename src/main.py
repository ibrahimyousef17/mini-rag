from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv('.env')
from routes import base , data 
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)

