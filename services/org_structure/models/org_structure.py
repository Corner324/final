from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)


class Position(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=False
    )


class OrgMember(Base):
    __tablename__ = "org_members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    position_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("positions.id"), nullable=False
    )
    manager_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("org_members.id"), nullable=True
    )
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
