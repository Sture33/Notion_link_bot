from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from ..data.config import DATABASE_URL

engine = create_async_engine(url=DATABASE_URL)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger)

    tokens: Mapped['NotionToken'] = relationship(back_populates='user', cascade='all, delete-orphan')


class NotionToken(Base):
    __tablename__ = 'notion_tokens'
    token: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['User'] = relationship(back_populates="tokens")

    pages: Mapped['Page'] = relationship(back_populates='notion_token', cascade='all, delete-orphan')


class Page(Base):
    __tablename__ = 'pages'

    page_api: Mapped[str] = mapped_column(String(100))
    token: Mapped[int] = mapped_column(ForeignKey('notion_tokens.id'))

    notion_token: Mapped['NotionToken'] = relationship(back_populates='pages')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
