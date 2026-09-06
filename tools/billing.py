import sqlite3
from datetime import datetime

DATABASE = "kirana.db"


def get_product(product_name):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, selling_price, gst_rate, stock, unit
        FROM products
        WHERE name = ?
    """, (product_name,))

    product = cursor.fetchone()
    connection.close()

    return product


def calculate_item(product_name, quantity):
    product = get_product(product_name)

    if product is None:
        return {
            "success": False,
            "message": f"Product '{product_name}' not found."
        }

    name, selling_price, gst_rate, stock, unit = product

    if quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    if quantity > stock:
        return {
            "success": False,
            "message": f"Only {stock:g} {unit} of {name} are available."
        }

    subtotal = selling_price * quantity
    gst_amount = subtotal * gst_rate / 100
    total = subtotal + gst_amount

    return {
        "success": True,
        "product": name,
        "quantity": quantity,
        "unit": unit,
        "price": selling_price,
        "gst_rate": gst_rate,
        "subtotal": round(subtotal, 2),
        "gst_amount": round(gst_amount, 2),
        "total": round(total, 2),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def finalize_bill(product_name, quantity):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, selling_price, gst_rate, stock, unit
        FROM products
        WHERE name = ?
    """, (product_name,))

    product = cursor.fetchone()

    if product is None:
        connection.close()
        return {
            "success": False,
            "message": f"Product '{product_name}' not found."
        }

    name, selling_price, gst_rate, stock, unit = product

    if quantity <= 0:
        connection.close()
        return {
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    if quantity > stock:
        connection.close()
        return {
            "success": False,
            "message": f"Cannot finalize bill. Only {stock:g} {unit} of {name} are available."
        }

    subtotal = selling_price * quantity
    gst_amount = subtotal * gst_rate / 100
    total = subtotal + gst_amount

    new_stock = stock - quantity

    cursor.execute(
        "UPDATE products SET stock = ? WHERE name = ?",
        (new_stock, name)
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            subtotal REAL NOT NULL,
            gst_amount REAL NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO sales
        (product_name, quantity, subtotal, gst_amount, total, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        quantity,
        subtotal,
        gst_amount,
        total,
        created_at
    ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Bill finalized successfully.",
        "product": name,
        "quantity": quantity,
        "subtotal": round(subtotal, 2),
        "gst_amount": round(gst_amount, 2),
        "total": round(total, 2),
        "remaining_stock": new_stock,
        "created_at": created_at
    }


def finalize_draft_bill(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM draft_bills
        WHERE user_id = ? AND status = 'draft'
    """, (str(user_id),))

    bill = cursor.fetchone()

    if bill is None:
        connection.close()
        return {
            "success": False,
            "message": "No active draft bill."
        }

    bill_id = bill[0]

    cursor.execute("""
        SELECT product_name, quantity
        FROM draft_bill_items
        WHERE bill_id = ?
    """, (bill_id,))

    items = cursor.fetchall()

    if not items:
        connection.close()
        return {
            "success": False,
            "message": "Draft bill is empty."
        }

    bill_items = []
    subtotal_total = 0
    gst_total = 0
    grand_total = 0

    # First check ALL stock before changing anything
    for product_name, quantity in items:

        cursor.execute("""
            SELECT name, selling_price, gst_rate, stock, unit
            FROM products
            WHERE name = ?
        """, (product_name,))

        product = cursor.fetchone()

        if product is None:
            connection.close()
            return {
                "success": False,
                "message": f"Product '{product_name}' not found."
            }

        name, price, gst_rate, stock, unit = product

        if quantity <= 0:
            connection.close()
            return {
                "success": False,
                "message": f"Invalid quantity for {name}."
            }

        if quantity > stock:
            connection.close()
            return {
                "success": False,
                "message": (
                    f"Cannot finalize bill. "
                    f"Only {stock:g} {unit} of {name} are available."
                )
            }

        subtotal = price * quantity
        gst_amount = subtotal * gst_rate / 100
        total = subtotal + gst_amount

        bill_items.append({
            "product": name,
            "quantity": quantity,
            "unit": unit,
            "price": price,
            "gst_rate": gst_rate,
            "subtotal": round(subtotal, 2),
            "gst_amount": round(gst_amount, 2),
            "total": round(total, 2)
        })

        subtotal_total += subtotal
        gst_total += gst_amount
        grand_total += total

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Deduct stock and record every sale
    for item in bill_items:

        cursor.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE name = ?
        """, (
            item["quantity"],
            item["product"]
        ))

        cursor.execute("""
            INSERT INTO sales
            (product_name, quantity, subtotal, gst_amount, total, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item["product"],
            item["quantity"],
            item["subtotal"],
            item["gst_amount"],
            item["total"],
            created_at
        ))

    # Mark draft as completed
    cursor.execute("""
        UPDATE draft_bills
        SET status = 'finalized'
        WHERE id = ?
    """, (bill_id,))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Draft bill finalized successfully.",
        "items": bill_items,
        "subtotal": round(subtotal_total, 2),
        "gst_amount": round(gst_total, 2),
        "total": round(grand_total, 2),
        "created_at": created_at
    }