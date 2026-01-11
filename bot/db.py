import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from bot.config import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String(64))
    tariff: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    webapp_query_id: Mapped[str] = mapped_column(String(128), nullable=True)

def create_user(user_key: str, days: int, devices: int) -> str:
    return f"hysteria2://{user_key}@extra.xferant-vpn.ru:443?sni=gosuslugi.ru&obfs=salamander&obfs-password=xferantHyst&fastopen=0&downmbps=270&upmbps=270&security=tls&insecure=1#{user_key.upper()}"

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
