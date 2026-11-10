import psycopg2

from db.config import DB
from db.import_data import *


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        import_users(cur)
        import_sizes(cur)
        import_categories(cur)
        import_subcategories(cur)
        import_manufactures(cur)
        import_models(cur)
        import_items(cur)
        import_orders(cur)
        import_order_items(cur)
        conn.commit()
        print("Импорт завершён")
    except Exception as e:
        conn.rollback()
        print("Ошибка импорта:", e)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
