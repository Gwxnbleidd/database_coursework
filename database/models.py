from sqlalchemy import Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase

class Base(DeclarativeBase):
    abstract = True
    table_args = {
        'schema': 'du'
    }
    pass

class Rebenok(Base):
    __tablename__ = 'rebenok'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adres: Mapped[str] = mapped_column(String)
    fio: Mapped[str] = mapped_column(String)
    data_rozhdeniya: Mapped[Date] = mapped_column(Date)
    kategoriya: Mapped[str] = mapped_column(String)


class Roditel(Base):
    __tablename__ = 'roditel'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fio: Mapped[str] = mapped_column(String)
    nomer: Mapped[str] = mapped_column(String)
    svedeniya: Mapped[str] = mapped_column(String)
    rol: Mapped[str] = mapped_column(String)

class RoditelRebenka(Base):
    __tablename__ = 'roditel_rebenka'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    roditel_id: Mapped[int] = mapped_column(Integer, ForeignKey('roditel.id', ondelete='RESTRICT', onupdate='CASCADE'))
    rebenok_id: Mapped[int] = mapped_column(Integer, ForeignKey('rebenok.id', ondelete='RESTRICT', onupdate='CASCADE'))

class TipDu(Base):
    __tablename__ = 'tip_du'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nazvanie: Mapped[str] = mapped_column(String)

class DoshkolnoeUchrezhdenie(Base):
    __tablename__ = 'doshkolnoe_uchregdenie'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nazvanie: Mapped[str] = mapped_column(String)
    naznachenie: Mapped[str] = mapped_column(String)
    tip_id: Mapped[int] = mapped_column(Integer, ForeignKey('tip_du.id', ondelete='RESTRICT', onupdate='CASCADE'))
    kontaktnye_dannye: Mapped[str] = mapped_column(String)
    kolichestvo_mest: Mapped[int] = mapped_column(Integer)
    stoimost: Mapped[int] = mapped_column(Integer)
    direktor: Mapped[str] = mapped_column(String)
    telefon: Mapped[str] = mapped_column(String)

class Profil(Base):
    __tablename__ = 'profil'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    naimenovanie: Mapped[str] = mapped_column(String)

class ProfilVDu(Base):
    __tablename__ = 'profil_v_du'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    du_id: Mapped[int] = mapped_column(Integer, ForeignKey('doshkolnoe_uchregdenie.id', ondelete='RESTRICT', onupdate='CASCADE'))
    profil_id: Mapped[int] = mapped_column(Integer, ForeignKey('profil.id', ondelete='RESTRICT', onupdate='CASCADE'))

class MestaDu(Base):
    __tablename__ = 'mesta_du'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    du_id: Mapped[int] = mapped_column(Integer, ForeignKey('doshkolnoe_uchregdenie.id', ondelete='RESTRICT', onupdate='CASCADE'))
    rebenok_id: Mapped[int] = mapped_column(Integer, ForeignKey('rebenok.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=True)
    zanyatost: Mapped[bool] = mapped_column(Boolean)
    vozrast: Mapped[int] = mapped_column(Integer)

class Ochered(Base):
    __tablename__ = 'ochered'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rebenok_id: Mapped[int] = mapped_column(Integer, ForeignKey('rebenok.id', ondelete='RESTRICT', onupdate='CASCADE'))
    du_id: Mapped[int] = mapped_column(Integer, ForeignKey('doshkolnoe_uchregdenie.id', ondelete='RESTRICT', onupdate='CASCADE'))
    data_postanovki: Mapped[Date] = mapped_column(Date)
    prioritet: Mapped[bool] = mapped_column(Boolean)

