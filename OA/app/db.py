from sqlmodel import create_engine, Session, select
from .models import Plan
from typing import List
import os

DB_URL = os.getenv("TASKPLANNER_DB_URL", "sqlite:///./plans.db")
engine = create_engine(DB_URL, echo=False)


def init_db():
    SQLModel = __import__('sqlmodel').SQLModel
    SQLModel.metadata.create_all(engine)


def save_plan(goal: str, due_days: int | None, data: str) -> Plan:
    with Session(engine) as session:
        p = Plan(goal=goal, due_days=due_days, data=data)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p


def list_plans() -> List[Plan]:
    with Session(engine) as session:
        q = select(Plan).order_by(Plan.created_at.desc())
        return session.exec(q).all()


def delete_plan(plan_id: int) -> bool:
    from sqlmodel import select
    with Session(engine) as session:
        q = select(Plan).where(Plan.id == plan_id)
        res = session.exec(q).one_or_none()
        if not res:
            return False
        session.delete(res)
        session.commit()
        return True


def clear_plans() -> int:
    with Session(engine) as session:
        plans = session.exec(select(Plan)).all()
        count = len(plans)
        for p in plans:
            session.delete(p)
        session.commit()
        return count
