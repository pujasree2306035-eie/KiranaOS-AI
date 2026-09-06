import sqlite3
from datetime import datetime

DATABASE = "kirana.db"


def setup_khata():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS khata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    connection.commit()
    connection.close()


def add_credit(customer_name, amount, description="Credit sale"):

    if amount <= 0:
        return {
            "success": False,
            "message": "Amount must be greater than zero."
        }

    setup_khata()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO customers (name) VALUES (?)",
        (customer_name,)
    )

    cursor.execute(
        "SELECT id FROM customers WHERE name = ?",
        (customer_name,)
    )

    customer = cursor.fetchone()
    customer_id = customer[0]

    cursor.execute(
        """
        INSERT INTO khata
        (customer_id, amount, transaction_type, description, created_at)
        VALUES (?, ?, 'credit', ?, ?)
        """,
        (
            customer_id,
            amount,
            description,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": f"₹{amount:.2f} added to {customer_name}'s Khata."
    }


def record_payment(customer_name, amount):

    if amount <= 0:
        return {
            "success": False,
            "message": "Amount must be greater than zero."
        }

    setup_khata()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM customers WHERE name = ?",
        (customer_name,)
    )

    customer = cursor.fetchone()

    if customer is None:
        connection.close()

        return {
            "success": False,
            "message": f"Customer '{customer_name}' not found."
        }

    customer_id = customer[0]

    cursor.execute(
        """
        INSERT INTO khata
        (customer_id, amount, transaction_type, description, created_at)
        VALUES (?, ?, 'payment', 'Payment received', ?)
        """,
        (
            customer_id,
            amount,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": f"₹{amount:.2f} payment recorded for {customer_name}."
    }


def get_balance(customer_name):

    setup_khata()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM customers WHERE name = ?",
        (customer_name,)
    )

    customer = cursor.fetchone()

    if customer is None:
        connection.close()

        return {
            "success": True,
            "customer": customer_name,
            "balance": 0,
            "message": f"No Khata account found for {customer_name}."
        }

    customer_id = customer[0]

    cursor.execute(
        """
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'credit'
                        THEN amount
                        ELSE 0
                    END
                ), 0
            ),
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'payment'
                        THEN amount
                        ELSE 0
                    END
                ), 0
            )
        FROM khata
        WHERE customer_id = ?
        """,
        (customer_id,)
    )

    credit, payments = cursor.fetchone()

    balance = credit - payments

    connection.close()

    return {
        "success": True,
        "customer": customer_name,
        "total_credit": round(credit, 2),
        "total_payment": round(payments, 2),
        "balance": round(balance, 2),
        "message": (
            f"{customer_name}'s outstanding Khata balance "
            f"is ₹{balance:.2f}."
        )
    }