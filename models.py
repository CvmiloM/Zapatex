from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sucursal(Base):
    __tablename__ = 'sucursales'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)
    cantidad = Column(Integer)
    precio = Column(Integer)
