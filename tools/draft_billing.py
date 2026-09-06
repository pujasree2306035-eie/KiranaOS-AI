import sqlite3

DATABASE = "kirana.db"


def get_or_create_draft(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM draft_bills WHERE user_id = ? AND status = 'draft'",
        (str(user_id),)
    )

    bill = cursor.fetchone()

    if bill:
        bill_id = bill[0]

    else:
        cursor.execute(
            """
            INSERT INTO draft_bills (user_id, status)
            VALUES (?, 'draft')
            """,
            (str(user_id),)
        )

        bill_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return bill_id


def add_item(user_id, product_name, quantity):

    if quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Check product
    cursor.execute(
        """
        SELECT name, stock, unit
        FROM products
        WHERE name = ?
        """,
        (product_name,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()

        return {
            "success": False,
            "message": f"Product '{product_name}' not found."
        }

    name, stock, unit = product

    # Create or get draft
    bill_id = get_or_create_draft(user_id)

    # Check if item already exists
    cursor.execute(
        """
        SELECT id, quantity
        FROM draft_bill_items
        WHERE bill_id = ? AND product_name = ?
        """,
        (bill_id, name)
    )

    existing_item = cursor.fetchone()

    if existing_item:

        item_id, old_quantity = existing_item
        new_quantity = old_quantity + quantity

        cursor.execute(
            """
            UPDATE draft_bill_items
            SET quantity = ?
            WHERE id = ?
            """,
            (new_quantity, item_id)
        )

    else:

        new_quantity = quantity

        cursor.execute(
            """
            INSERT INTO draft_bill_items
            (bill_id, product_name, quantity)
            VALUES (?, ?, ?)
            """,
            (bill_id, name, quantity)
        )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": (
            f"Added {quantity:g} {unit} of {name} "
            f"to the draft bill."
        ),
        "current_quantity": new_quantity,
        "available_stock": stock
    }


def remove_item(user_id, product_name):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM draft_bills
        WHERE user_id = ? AND status = 'draft'
        """,
        (str(user_id),)
    )

    bill = cursor.fetchone()

    if bill is None:
        connection.close()

        return {
            "success": False,
            "message": "No active draft bill."
        }

    bill_id = bill[0]

    cursor.execute(
        """
        DELETE FROM draft_bill_items
        WHERE bill_id = ? AND product_name = ?
        """,
        (bill_id, product_name)
    )

    if cursor.rowcount == 0:
        connection.close()

        return {
            "success": False,
            "message": f"{product_name} is not in the draft bill."
        }

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": f"Removed {product_name} from the draft bill."
    }


def update_quantity(user_id, product_name, quantity):

    if quantity <= 0:
        return remove_item(user_id, product_name)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM draft_bills
        WHERE user_id = ? AND status = 'draft'
        """,
        (str(user_id),)
    )

    bill = cursor.fetchone()

    if bill is None:
        connection.close()

        return {
            "success": False,
            "message": "No active draft bill."
        }

    bill_id = bill[0]

    cursor.execute(
        """
        SELECT name, stock, unit
        FROM products
        WHERE name = ?
        """,
        (product_name,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()

        return {
            "success": False,
            "message": f"Product '{product_name}' not found."
        }

    name, stock, unit = product

    if quantity > stock:
        connection.close()

        return {
            "success": False,
            "message": (
                f"Only {stock:g} {unit} of {name} "
                f"are available."
            )
        }

    cursor.execute(
        """
        UPDATE draft_bill_items
        SET quantity = ?
        WHERE bill_id = ? AND product_name = ?
        """,
        (quantity, bill_id, name)
    )

    if cursor.rowcount == 0:
        connection.close()

        return {
            "success": False,
            "message": f"{name} is not in the draft bill."
        }

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": (
            f"Updated {name} quantity to "
            f"{quantity:g} {unit}."
        )
    }


def view_draft(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM draft_bills
        WHERE user_id = ? AND status = 'draft'
        """,
        (str(user_id),)
    )

    bill = cursor.fetchone()

    if bill is None:
        connection.close()

        return {
            "success": True,
            "message": "No active draft bill.",
            "items": []
        }

    bill_id = bill[0]

    cursor.execute(
        """
        SELECT product_name, quantity
        FROM draft_bill_items
        WHERE bill_id = ?
        """,
        (bill_id,)
    )

    items = cursor.fetchall()

    connection.close()

    if not items:
        return {
            "success": True,
            "message": "Draft bill is empty.",
            "items": []
        }

    formatted_items = []

    for product_name, quantity in items:
        formatted_items.append({
            "product": product_name,
            "quantity": quantity
        })

    return {
        "success": True,
        "message": "Draft bill retrieved.",
        "items": formatted_items
    }