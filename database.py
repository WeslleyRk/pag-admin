from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./linuxstore.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False) 
    valor_ativo = Column(Float, default=0.0) # <--- NOVO: Custo por cliente

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    usuario = Column(String) # <--- NOVO: Username do cliente
    valor = Column(Float)    # Mudado para Float para aceitar centavos
    status = Column(String)  # 'pago' ou 'receber'
    data_criacao = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id")) 

Base.metadata.create_all(bind=engine)