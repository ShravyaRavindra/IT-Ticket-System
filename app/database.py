import sqlite3
from pathlib import Path

DATABASE = Path(__file__).parent.parent / "instance" / "tickets.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection