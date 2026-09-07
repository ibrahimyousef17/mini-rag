from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv('.env')
from routes import base , data 
import os
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import Settings, get_settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):

    settings = get_settings()
    app.mongo_connection = AsyncIOMotorClient(settings.mongodb_url) # type: ignore
    app.db_client = app.mongo_connection[settings.mongodb_name] # type: ignore
    print("Starting App")

    yield
    app.mongo_connection.close() # type: ignore

    print("Shutdown App")



app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)

