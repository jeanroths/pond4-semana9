from fastapi import APIRouter
import logging
import uvicorn
from pydantic import BaseModel
from typing import List

event_router = APIRouter()

class Events(BaseModel):
    id: int
    title: str
    content: str

# In-memory storage for events
event_database: List[Events] = []

# Setup logging
logger = logging.getLogger(__name__)

@event_router.post("/")
async def create_event(event: Events):
    logger.info(f"Creating event: {event}")
    event_database.append(event)
    return event

@event_router.get("/")
async def get_events():
    logger.info("Fetching all events")
    return event_database

@event_router.put("/{event_id}")
async def update_event(event_id: int, event: Events):
    logger.info(f"Updating event {event_id} with {event}")
    if event_id >= len(event_database):
        return {"error": "Event not found"}
    event_database[event_id] = event
    return event

@event_router.delete("/{event_id}")
async def delete_event(event_id: int):
    logger.info(f"Deleting event {event_id}")
    if event_id >= len(event_database):
        return {"error": "Event not found"}
    event_database.pop(event_id)
    return {"message": "Event deleted"}
