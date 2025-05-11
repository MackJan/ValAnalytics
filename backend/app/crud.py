from typing import List

from sqlmodel import Session, select
from .database import engine
from .models import User, Match, Round, Event
import datetime

def get_user_by_riot_id(riot_id: str) -> User:
    with Session(engine) as session:
        statement = select(User).where(User.riot_id==riot_id)
        return session.exec(statement).first()

def create_user(riot_id: str, name: str, tag: str) -> User:
    user = User(riot_id=riot_id, name=name, tag=tag)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def create_match(player_id: str, **match_data) -> Match:
    match = Match(player_id=player_id, **match_data)
    with Session(engine) as session:
        session.add(match)
        session.commit()
        session.refresh(match)
    return match

def list_user_matches(player_id: str) -> List[Match]:
    with Session(engine) as session:
        statement = select(Match).where(Match.player_id==player_id)
        return session.exec(statement).all()
