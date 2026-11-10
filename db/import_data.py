import pandas
import psycopg2

from db.config import DB

PATH_USERS = "../data/Users_import.xlsx"
PATH_SIZES = "../data/Sizes_import.xlsx"
PATH_ORDERS = "../data/Orders_import.xlsx"
PATH_MODELS = "../data/Products_import.xlsx"
PATH_ITEMS = "../data/Stock_Items_import.xlsx"


def clean(value):  # функция форматирования строковых значений для бд
    if pandas.isna(value):
        return None
    if isinstance(value, str):
        return " ".join(value.split())
    return value


def find_id(cur, sql, params, what):
    cur.execute(sql, params)
    row = cur.fetchone()

    if row is None:
        print(f"Пропуск записи: не найдено {what} {params}")
        return None

    return row[0]


def import_users(cur):  # импорт пользователей
    df = pandas.read_excel(PATH_USERS)

    for _, row in df.iterrows():
        cur.execute(
            """INSERT INTO users (last_name, name, middle_name, login, role)
            VALUES (%s, %s, %s, %s, %s)""",
            (
                clean(row["Фамилия"]),
                clean(row["Имя"]),
                clean(row["Отчетсво"]),
                clean(row["Логин"]),
                clean(row["Роль"]),
            )
        )


def import_sizes(cur):  # импорт размеров
    df = pandas.read_excel(PATH_SIZES)

    for _, row in df.iterrows():
        cur.execute(
            """INSERT INTO sizes (value)
            VALUES (%s)""",
            (
                float(row["Размер"]),
            )
        )


def import_categories(cur):  # импорт категорий
    df = pandas.read_excel(PATH_MODELS)

    for _, row in df.iterrows():
        cur.execute(
            """INSERT INTO categories (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING""",
            (
                clean(row["Категория"]),
            )
        )


def import_subcategories(cur):  # импорт подкатегорий
    df = pandas.read_excel(PATH_MODELS)

    for _, row in df.iterrows():
        # ищем id категории
        subcategory_name = clean(row["Подкатегория"])
        category_name = clean(row["Категория"])
        category_id = find_id(cur, "SELECT id FROM categories WHERE name = %s",
                              (category_name,), "категория")
        if category_id is None:
            continue

        # вставляем данные
        cur.execute(
            """INSERT INTO subcategories (category_id, name)
            VALUES (%s, %s)
            ON CONFLICT (category_id, name) DO NOTHING""",
            (
                category_id,
                subcategory_name,
            )
        )


def import_manufacturers(cur):  # импорт производств
    df = pandas.read_excel(PATH_MODELS)

    for _, row in df.iterrows():
        cur.execute(
            """INSERT INTO manufacturers (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING""",
            (
                clean(row["Производство"]),
            )
        )


def import_models(cur):  # импорт моделей
    df = pandas.read_excel(PATH_MODELS)

    for _, row in df.iterrows():
        # ищем id подкатегории
        subcategory_id = find_id(
            cur,
            """SELECT s.id FROM subcategories s
            JOIN categories c ON c.id = s.category_id
            WHERE s.name = %s AND c.name = %s""",
            (clean(row["Подкатегория"]), clean(row["Категория"]),),
            "подкатегория"
        )
        if subcategory_id is None:
            continue
        # ищем id производства
        manufacture_id = find_id(cur, "SELECT id FROM manufacturers WHERE name = %s",
                                 (clean(row["Производство"]),), "производство")
        if manufacture_id is None:
            continue
        # вставляем данные
        cur.execute(
            """INSERT INTO models (name, image, composition, description, manufacture_id, subcategory_id, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                clean(row["Наименование товара"]),
                clean(row["Изображение"]),
                clean(row["Состав"]),
                clean(row["Описание"]),
                manufacture_id,
                subcategory_id,
                float(row["Цена"]),
            )
        )


def import_items(cur):  # импорт товаров
    df = pandas.read_excel(PATH_ITEMS)

    for _, row in df.iterrows():
        # получаем id модели
        model_id = find_id(cur, "SELECT id FROM models WHERE name = %s",
                           (clean(row["Наименование товара"]),), "модель")
        if model_id is None:
            continue
        # получаем id размера
        size_id = find_id(cur, "SELECT id FROM sizes WHERE value = %s",
                          (float(row["Размер"]),), "размер")
        if size_id is None:
            continue

        cur.execute(
            """INSERT INTO items (model_id, size_id, count)
            VALUES (%s, %s, %s)""",
            (
                model_id,
                size_id,
                int(row["Количество доступное для заказа"]),
            )
        )


def import_orders(cur):  # импорт заказов
    df = pandas.read_excel(PATH_ORDERS)

    for _, row in df.iterrows():
        # разбиваем фио
        parts = str(row["ФИО"]).split()
        last_name = parts[0]
        first_name = parts[1]
        middle_name = parts[2]

        # получаем id пользователя
        user_id = find_id(
            cur,
            """SELECT id FROM users
            WHERE last_name = %s AND name = %s AND middle_name = %s""",
            (last_name, first_name, middle_name),
            "пользователь")
        if user_id is None:
            continue
        # вставляем заказ
        cur.execute(
            """INSERT INTO orders (id, date, user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING""",
            (
                int(row["Номер заказа"]),
                pandas.to_datetime(row["Дата заказа"]).date(),
                user_id,
            )
        )
    cur.execute("SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders))")


def import_order_items(cur):
    df = pandas.read_excel(PATH_ORDERS)

    for _, row in df.iterrows():
        # получаем id товара
        item_id = find_id(
            cur,
            """SELECT i.id FROM items i
        JOIN models m ON m.id = i.model_id
        JOIN sizes s ON s.id = i.size_id
        WHERE m.name = %s AND s.value = %s::numeric""",
            (clean(row["Наименование товара"]), clean(row["Размер"]),),
            "товар"
                          )
        if item_id is None:
            continue
        # вставляем данные
        cur.execute("""
        INSERT INTO order_items (order_id, item_id, count, unit_price)
        VALUES(%s, %s, %s, %s)
        ON CONFLICT (order_id, item_id)
        DO UPDATE SET count = order_items.count + EXCLUDED.count
        """,
                    (
                        int(row["Номер заказа"]),
                        item_id,
                        int(row["Количество"]),
                        float(row["Цена за единицу"]),
                    )
                    )


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        import_users(cur)
        import_sizes(cur)
        import_categories(cur)
        import_subcategories(cur)
        import_manufacturers(cur)
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
