import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.community_entry import CommunityEntry

with Session(engine) as session:
    entries = session.query(CommunityEntry.category, CommunityEntry.name).all()
    print(entries)
