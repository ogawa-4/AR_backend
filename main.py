from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- DB設定 ---
DATABASE_URL = os.getenv("postgresql://ogawa_ss:QSocNF3MpMScG1ozSppJHMJw2YAf8RiX@dpg-d3d44vbuibrs738cce1g-a.oregon-postgres.render.com/ar_db_shml")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL が設定されていません。Renderの環境変数に追加してください。")

# Render用の接続URL形式調整（postgres → postgresql）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- モデル定義 ---
class Letter(Base):
    __tablename__ = "letters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


# --- リクエスト用スキーマ ---
class LetterCreate(BaseModel):
    title: str
    content: str
    latitude: float
    longitude: float


# --- FastAPI本体 ---
app = FastAPI()


# --- APIルート ---
@app.get("/letters")
def get_letters():
    db = SessionLocal()
    letters = db.query(Letter).all()
    db.close()
    return letters


@app.post("/letters")
def create_letter(letter: LetterCreate):
    db = SessionLocal()
    new_letter = Letter(
        title=letter.title,
        content=letter.content,
        latitude=letter.latitude,
        longitude=letter.longitude
    )
    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    db.close()
    return {"message": "手紙を追加しました", "letter": new_letter}
