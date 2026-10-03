import os
from sqlalchemy import create_engine, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine(os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/documents"))
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class ExtractionRecord(Base):
    __tablename__ = "extractions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))  # accepted | needs_review
    payload: Mapped[str] = mapped_column(Text)
    issues: Mapped[str] = mapped_column(Text, default="")

def init_db():
    Base.metadata.create_all(engine)
