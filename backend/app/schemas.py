from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    riot_id: str
    name: str
    tag: str

class EventCreate(BaseModel):
    round_id: int
    type: str
    actor: str
    target: Optional[str]
    value: Optional[int]

class EventRead(EventCreate):
    id: int
    timestamp: datetime

class MatchRead(BaseModel):
    match_uuid: str
    map_name: str
    agent: str
    started_at: datetime
    ended_at: datetime
    rounds: List[EventRead]

