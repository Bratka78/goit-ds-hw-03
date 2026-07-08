import json
import os
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import PyMongoError

BASE_URL = "http://quotes.toscrape.com"


def scrape_quotes_and_authors():
    quotes_data = []
    authors_data = {}  # Використовуємо словник, щоб уникнути дублікатів авторів

    current_page = "/"

    print("Початок скрапінгу сайту...")

    while current_page:
        print(f"Парсинг сторінки: {BASE_URL}{current_page}")
        response = requests.get(f"{BASE_URL}{current_page}")
        soup = BeautifulSoup(response.text, "html.parser")

        # Знаходимо всі блоки з цитатами на сторінці
        quote_elements = soup.find_all("div", class_="quote")

        for elem in quote_elements:
            # Збір тексту цитати
            text = elem.find("span", class_="text").text

            # Збір автора
            author_name = elem.find("small", class_="author").text

            # Збір тегів
            tags = [tag.text for tag in elem.find_all("a", class_="tag")]

            # Додаємо цитату до загального списку
            quotes_data.append(
                {"tags": tags, "author": author_name, "quote": text}
            )

            # Якщо автора ще немає в нашому списку, переходимо на його сторінку
            if author_name not in authors_data:
                author_url = elem.find("a")["href"]
                author_response = requests.get(f"{BASE_URL}{author_url}")
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                born_date = author_soup.find(
                    "span", class_="author-born-date"
                ).text
                born_location = author_soup.find(
                    "span", class_="author-born-location"
                ).text
                description = author_soup.find(
                    "div", class_="author-description"
                ).text.strip()

                authors_data[author_name] = {
                    "fullname": author_name,
                    "born_date": born_date,
                    "born_location": born_location,
                    "description": description,
                }

        # Шукаємо посилання на наступну сторінку 
        next_button = soup.find("li", class_="next")
        current_page = next_button.find("a")["href"] if next_button else None

    # Перетворюємо словник авторів у список
    authors_list = list(authors_data.values())

    # Збереження у файли JSON
    with open("qoutes.json", "w", encoding="utf-8") as f:
        json.dump(quotes_data, f, ensure_ascii=False, indent=2)

    with open("authors.json", "w", encoding="utf-8") as f:
        json.dump(authors_list, f, ensure_ascii=False, indent=2)

    print(
        f"Скрапінг завершено! Збережено {len(quotes_data)} цитат та {len(authors_list)} авторів у файли."
    )
    return quotes_data, authors_list


def import_to_mongodb_atlas(quotes, authors):
    MONGO_URI = "mongodb+srv://maksymbrat_db_user:bratus2027@bratka.olpejck.mongodb.net/"

    print("\nПідключення до MongoDB Atlas...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["production_db"] 

        # Колекції
        quotes_collection = db["quotes"]
        authors_collection = db["authors"]

        # Очищення старих даних перед імпортом
        quotes_collection.delete_many({})
        authors_collection.delete_many({})

        # Імпорт даних
        if authors:
            authors_collection.insert_many(authors)
            print(
                f"Успішно імпортовано {len(authors)} авторів у колекцію 'authors'."
            )

        if quotes:
            quotes_collection.insert_many(quotes)
            print(
                f"Успішно імпортовано {len(quotes)} цитат у колекцію 'quotes'."
            )

    except PyMongoError as e:
        print(f"Помилка при роботі з MongoDB Atlas: {e}")


if __name__ == "__main__":
    quotes, authors = scrape_quotes_and_authors()

    import_to_mongodb_atlas(quotes, authors)