from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, Text, ForeignKey, DateTime
from datetime import datetime
from typing import Optional, List
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class CompanyORM(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    sector: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reports: Mapped[List["EarningsReportORM"]] = relationship("EarningsReportORM", back_populates="company")


class EarningsReportORM(Base):
    __tablename__ = "earnings_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    fiscal_quarter: Mapped[str] = mapped_column(String(10))
    fiscal_year: Mapped[int] = mapped_column()
    report_date: Mapped[datetime] = mapped_column(DateTime)
    revenue: Mapped[float] = mapped_column(Float)
    revenue_yoy: Mapped[float] = mapped_column(Float)
    eps: Mapped[float] = mapped_column(Float)
    eps_yoy: Mapped[float] = mapped_column(Float)
    net_income: Mapped[float] = mapped_column(Float)
    operating_cash_flow: Mapped[float] = mapped_column(Float)
    guidance_revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    guidance_eps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    summary: Mapped[str] = mapped_column(Text)
    management_commentary: Mapped[str] = mapped_column(Text)
    beat_estimate: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["CompanyORM"] = relationship("CompanyORM", back_populates="reports")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
