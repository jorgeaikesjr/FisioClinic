from typing import Optional, List
from sqlalchemy.orm import Session
from models.waiting_list import WaitingList
from schemas.waiting_list import WaitingListCreate

def add_to_waiting_list(db: Session, data: WaitingListCreate) -> WaitingList:
    db_item = WaitingList(**data.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_waiting_list(db: Session, category: Optional[str] = None) -> List[WaitingList]:
    query = db.query(WaitingList)
    if category:
        query = query.filter(WaitingList.category == category)
    # Order by date_added ascending so the oldest ones are first
    return query.order_by(WaitingList.date_added.asc()).all()

def remove_from_waiting_list(db: Session, item_id: str) -> Optional[WaitingList]:
    db_item = db.query(WaitingList).filter(WaitingList.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
