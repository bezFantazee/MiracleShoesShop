import psycopg2
from db.config import DB

def db_connect():
    return psycopg2.connect(**DB)