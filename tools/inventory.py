import sqlite3

DATABASE = "kirana.db"


def find_product(product_name):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name, stock, unit
        FROM products
        WHERE LOWER(name) = LOWER(?)
        """,
        (product_name,)
    )

    product = cursor.fetchone()

    if product is None:
        cursor.execute(
            """
            SELECT name, stock, unit
            FROM products
            WHERE LOWER(name) LIKE LOWER(?)
            """,
            (f"%{product_name}%",)
        )
        product = cursor.fetchone()

    connection.close()

    return product


def check_stock(product_name):
    product = find_product(product_name)

    if product is None:
        return f"Product '{product_name}' not found."

    name, stock, unit = product

    return f"{name}: {stock:g} {unit} available."


def receive_stock(product_name, quantity):
    product = find_product(product_name)

    if product is None:
        return f"Product '{product_name}' not found."

    name, stock, unit = product

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    new_stock = stock + quantity

    cursor.execute(
        """
        UPDATE products
        SET stock = ?
        WHERE name = ?
        """,
        (new_stock, name)
    )

    connection.commit()
    connection.close()

    return (
        f"Added {quantity:g} {unit} of {name}. "
        f"New stock: {new_stock:g} {unit}."
    )


def reduce_stock(product_name, quantity):
    product = find_product(product_name)

    if product is None:
        return f"Product '{product_name}' not found."

    name, stock, unit = product

    if quantity > stock:
        return (
            f"Cannot sell {quantity:g} {unit} of {name}. "
            f"Only {stock:g} {unit} available."
        )

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    new_stock = stock - quantity

    cursor.execute(
        """
        UPDATE products
        SET stock = ?
        WHERE name = ?
        """,
        (new_stock, name)
    )

    connection.commit()
    connection.close()

    return (
        f"Sold {quantity:g} {unit} of {name}. "
        f"Remaining stock: {new_stock:g} {unit}."
    )