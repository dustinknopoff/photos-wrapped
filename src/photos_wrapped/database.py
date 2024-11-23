from enum import IntEnum
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel, Session

class Status(IntEnum):
    CREATED = 0
    IN_PROGRESS = 1
    COMPLETE = 2
    ERROR = -1

class Queue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    payload: str = Field()
    response: str | None = Field(default=None)
    status: int = Field(default=0)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]