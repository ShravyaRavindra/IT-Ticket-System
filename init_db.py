from app.database import get_db_connection


def initialize_database():
    connection = get_db_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (
                role IN ('EMPLOYEE', 'AGENT', 'ADMIN')
            ),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'MEDIUM',
            status TEXT NOT NULL DEFAULT 'NEW',

            created_by INTEGER NOT NULL,
            assigned_to INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            closed_at TIMESTAMP,
            user_confirmed INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (created_by)
                REFERENCES users(user_id),

            FOREIGN KEY (assigned_to)
                REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS ticket_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            changed_by INTEGER NOT NULL,

            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (ticket_id)
                REFERENCES tickets(ticket_id)
                ON DELETE CASCADE,

            FOREIGN KEY (changed_by)
                REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS ticket_comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (ticket_id)
                REFERENCES tickets(ticket_id)
                ON DELETE CASCADE,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
        );
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()