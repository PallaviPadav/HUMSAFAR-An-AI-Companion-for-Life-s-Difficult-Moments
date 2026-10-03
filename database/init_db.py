import sqlite3
from pathlib import Path


# HUMSAFAR project root
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database location
DB_PATH = BASE_DIR / "data" / "humsafar.db"


def init_database():
    # Make sure the data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create/open SQLite database
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    # Create movies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tmdb_id INTEGER UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            rating REAL,
            poster_url TEXT,
            video_url TEXT,
            details_url TEXT,
            genre TEXT,
            release_date TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    init_database()
