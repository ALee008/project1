import csv
import time
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def import_book_details(file_name: str) -> tuple:
    """Return a list with all rows from csv file and set of authors."""
    with open(file_name) as books:
        csv_reader = csv.reader(books, delimiter=",")
        # skip header
        _ = next(csv_reader)

        result = list(csv_reader)

    authors = set([row[2] for row in result])

    return result, authors


def database_import(rows):
    result, authors = rows
    for author in authors:
        db.execute("INSERT INTO authors(name) VALUES (:name)", {"name": author})
    db.commit()
    print(f"{len(authors)} rows affected.")

    for row in result:
        db.execute(
            "INSERT INTO book_details(isbn, title, author_id, year) VALUES("
            ":isbn, :title, (SELECT author_id FROM authors WHERE name = :name), :year)"
            , {"isbn": row[0], "title": row[1], "name": row[2], "year": row[3]}
        )
    db.commit()
    print(f"{len(result)} rows affected.")

    return None


if __name__ == '__main__':
    books = import_book_details("books.csv")
    t0 = time.time()
    database_import(books)
    print(time.time() - t0)
