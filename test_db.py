import psycopg2
from db.config import DB

conn = psycopg2.connect(**DB)
cur = conn.cursor()
cur.execute("SELECT version()")
print(cur.fetchone())
cur.close()
conn.close()
