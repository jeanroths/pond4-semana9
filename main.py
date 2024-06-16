from fastapi import FastAPI
import logging
from logging_config import setup_logging
from events import event_router
import uvicorn
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Items(BaseModel):
    id: int
    title: str
    content: str
# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# In-memory storage
database: List[Items] = []

@app.get("/")
async def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the main service"}

@app.post("/items/")
async def create_item(item: Items):
    logger.info(f"Creating item: {item}")
    database.append(item)
    return item

@app.get("/items/")
async def get_items():
    logger.info("Fetching all items")
    return database

# Include event router
app.include_router(event_router, prefix="/events", tags=["events"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)