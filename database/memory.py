import sqlite3

DATABASE = "kirana.db"


def create_memory_table():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            UNIQUE(user_id, memory_key)
        )
    """)

    connection.commit()
    connection.close()


def save_memory(user_id, memory_key, memory_value):
    create_memory_table()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO memories
        (user_id, memory_key, memory_value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, memory_key)
        DO UPDATE SET memory_value = excluded.memory_value
    """, (
        str(user_id),
        memory_key,
        memory_value
    ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": f"Saved preference '{memory_key}'."
    }


def get_memory(user_id, memory_key):
    create_memory_table()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT memory_value
        FROM memories
        WHERE user_id = ? AND memory_key = ?
    """, (
        str(user_id),
        memory_key
    ))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return {
            "success": False,
            "message": "Memory not found."
        }

    return {
        "success": True,
        "memory_key": memory_key,
        "memory_value": result[0]
    }


def get_all_memories(user_id):
    create_memory_table()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT memory_key, memory_value
        FROM memories
        WHERE user_id = ?
        ORDER BY memory_key
    """, (str(user_id),))

    memories = cursor.fetchall()

    connection.close()

    result = []

    for key, value in memories:
        result.append({
            "key": key,
            "value": value
        })

    return {
        "success": True,
        "memories": result
    }