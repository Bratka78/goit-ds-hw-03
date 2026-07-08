import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError


def get_database():
    connection_string = "mongodb+srv://maksymbrat_db_user:bratus2027@bratka.olpejck.mongodb.net/"
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Перевірка з'єднання
        client.admin.command("ping")

        # Створення/вибір бази даних 'cats_db' та колекції 'cats'
        db = client["cats_db"]
        return db["cats"]
    except ConnectionFailure:
        print("Помилка: Не вдалося підключитися до MongoDB. Перевірте, чи запущений сервер.")
        sys.exit(1)

# ЧИТАННЯ (READ)

def print_all_cats(collection):
    #Виводить усі записи з колекції.
    try:
        cats = collection.find()
        # Перевіряємо, чи колекція не порожня
        cats_list = list(cats)
        if not cats_list:
            print("Колекція порожня.")
            return

        print("\n--- Список всіх котів ---")
        for cat in cats_list:
            print(
                f"Ім'я: {cat.get('name')}, Вік: {cat.get('age')}, Характеристики: {', '.join(cat.get('features', []))}"
            )
    except PyMongoError as e:
        print(f"Помилка при читанні даних: {e}")


def print_cat_by_name(collection, name):
    #Знаходить та виводить інформацію про кота за ім'ям.
    try:
        cat = collection.find_one({"name": name})
        if cat:
            print(f"\nЗнайдено кота: {cat.get('name')}")
            print(f"- Вік: {cat.get('age')}")
            print(f"- Характеристики: {', '.join(cat.get('features', []))}")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено.")
    except PyMongoError as e:
        print(f"Помилка при пошуку кота: {e}")

# ОНОВЛЕННЯ (UPDATE)

def update_cat_age(collection, name, new_age):
    #Оновлює вік кота за його ім'ям.
    try:
        result = collection.update_one({"name": name}, {"$set": {"age": new_age}})
        if result.matched_count > 0:
            print(f"Вік кота '{name}' успішно оновлено до {new_age}.")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено для оновлення віку.")
    except PyMongoError as e:
        print(f"Помилка при оновленні віку: {e}")


def add_cat_feature(collection, name, new_feature):
    #Додає нову характеристику до списку features кота за ім'ям.
    try:
        result = collection.update_one(
            {"name": name}, {"$addToSet": {"features": new_feature}}
        )
        if result.matched_count > 0:
            if result.modified_count > 0:
                print(
                    f"Характеристику '{new_feature}' успішно додано до кота '{name}'."
                )
            else:
                print(f"У кота '{name}' вже є характеристика '{new_feature}'.")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено для додавання характеристики.")
    except PyMongoError as e:
        print(f"Помилка при додаванні характеристики: {e}")

# ВИДАЛЕННЯ (DELETE)

def delete_cat_by_name(collection, name):
    #Видаляє запис про кота з колекції за ім'ям.
    try:
        result = collection.delete_one({"name": name})
        if result.deleted_count > 0:
            print(f"Запис про кота '{name}' успішно видалено.")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено для видалення.")
    except PyMongoError as e:
        print(f"Помилка при видаленні кота: {e}")


def delete_all_cats(collection):
    #Видаляє всі записи з колекції.
    try:
        result = collection.delete_many({})
        print(f"Усі записи видалено. Кількість видалених документів: {result.deleted_count}")
    except PyMongoError as e:
        print(f"Помилка при очищенні колекції: {e}")

# ДЕМОНСТРАЦІЯ РОБОТИ (MAIN)

def seed_data(collection):
    #Допоміжна функція для наповнення бази початковими даними.
    print("\nНаповнення бази початковими даними...")
    collection.delete_many({})  # Очищуємо перед демонстрацією

    test_cats = [
        {
            "name": "barsik",
            "age": 3,
            "features": ["ходить в капці", "дає себе гладити", "рудий"],
        },
        {"name": "murzik", "age": 5, "features": ["полюбляє рибу", "спить на дивані"]},
        {"name": "gosha", "age": 1, "features": ["грається з м'ячиком"]},
    ]
    collection.insert_many(test_cats)


if __name__ == "__main__":

    # Ініціалізація підключення
    cats_collection = get_database()

    seed_data(cats_collection)

    print_all_cats(cats_collection)

    print_cat_by_name(cats_collection, "barsik")
    print_cat_by_name(cats_collection, "unknown_cat")  

    update_cat_age(cats_collection, "barsik", 4)
    print_cat_by_name(cats_collection, "barsik")  

    add_cat_feature(cats_collection, "barsik", "любить котячу м'яту")
    print_cat_by_name(cats_collection, "barsik")  

    delete_cat_by_name(cats_collection, "gosha")
    print_all_cats(cats_collection)  

    delete_all_cats(cats_collection)
    print_all_cats(cats_collection)  