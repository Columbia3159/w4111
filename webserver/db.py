from flask import g
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import hashlib
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

DATABASEURI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"

engine = create_engine(DATABASEURI, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)

def connect_db():
  try:
    g.conn = engine.connect()
  except Exception as e:
    print("Database connection failed")
    print(e)
    g.conn = None

def close_db():
  try:
    if hasattr(g, 'conn'):
      g.conn.close()
  except Exception as e:
    print("Failed to close the database connection")
    print(e)

def create_user(email, name, password):
  password = hashlib.sha256(password.encode()).hexdigest()
  cmd = "INSERT INTO users (email, name, password) VALUES (:email, :name, :password)"
  result = g.conn.execute(text(cmd).params(email=email.lower(), name=name, password=password))
  g.conn.commit() 
  
def authenticate(email, password):
  hashed_password = hashlib.sha256(password.encode()).hexdigest()
  cmd = "SELECT * FROM users WHERE email = :email AND password = :password"
  user = g.conn.execute(text(cmd), {"email": email.lower(), "password": hashed_password}).fetchone()
  return user
    
def get_users():
  cursor = g.conn.execute(text("SELECT name FROM users"))
  names = []
  for result in cursor:
    names.append(result)  
  cursor.close()
  return names