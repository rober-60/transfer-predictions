from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session

class Base(DeclarativeBase):
    pass

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    transfermarkt_id: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    nationality: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)
    height: Mapped[int] = mapped_column(Integer)
    foot: Mapped[str] = mapped_column(String)

    market_values: Mapped[list["MarketValueSnapshot"]] = relationship(back_populates="player")


class MarketValueSnapshot(Base):
    __tablename__ = "market_value_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    date: Mapped[date] = mapped_column(Date)
    market_value: Mapped[int] = mapped_column(Integer)
    age:Mapped[int] = mapped_column(Integer)
    club_name:Mapped[str] = mapped_column(String)

    player: Mapped["Player"] = relationship(back_populates="market_values")

def get_engine():
    return create_engine("sqlite:///data/football_values.db")

def init_db():
    Base.metadata.create_all(get_engine())

def get_session():
    session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    db = session()
    return db
