import sqlite3
from pathlib import Path
from flask import current_app


DATABASE = Path(__file__).parent.parent / "instance" / "tickets.db"


def get_db_connection():
    database = current_app.config.get("DATABASE", DATABASE)

    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection