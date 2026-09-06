import sqlite3

DATABASE = "kirana.db"

def resolve_product_name(cursor, product_name):
    cursor.execute(
        """
        SELECT name
        FROM products
        WHERE LOWER(name) = LOWER(?)
           OR LOWER(name) LIKE LOWER(?)
        """,
        (product_name, f"%{product_name}%")
    )

    products = cursor.fetchall()

    if len(products) == 1:
        return products[0][0]

    return None


def get_or_create_draft(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    user_id = str(user_id)

    cursor.execute(
        """
        SELECT id, status
        FROM draft_bills
        WHERE user_id = ?
        """,
        (user_id,)
    )

    bill = cursor.fetchone()

    if bill:
        bill_id, status = bill

        if status == "draft":
            connection.close()
            return bill_id

        cursor.execute(
            """
            UPDATE draft_bills
            SET status = 'draft'
            WHERE id = ?
            """,
            (bill_id,)
        )

        cursor.execute(
            """
            DELETE FROM draft_bill_items
            WHERE bill_id = ?
            """,
            (bill_id,)
        )

        connection.commit()
        connection.close()

        return bill_id

    cursor.execute(
        """
        INSERT INTO draft_bills (user_id, status)
        VALUES (?, 'draft')
        """,
        (user_id,)
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

    # Find product by exact name, case-insensitive, or unique partial name
    cursor.execute(
        """
        SELECT name, stock, unit
        FROM products
        WHERE LOWER(name) = LOWER(?)
           OR LOWER(name) LIKE LOWER(?)
        """,
        (product_name, f"%{product_name}%")
    )

    products = cursor.fetchall()

    if len(products) == 0:
        connection.close()

        return {
            "success": False,
            "message": f"Product '{product_name}' not found."
        }

    if len(products) > 1:
        connection.close()

        return {
            "success": False,
            "message": (
                f"Multiple products match '{product_name}'. "
                "Please specify the product name more clearly."
            )
        }

    name, stock, unit = products[0]

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
        SELECT product_name
        FROM draft_bill_items
        WHERE bill_id = ?
        """,
        (bill_id,)
    )

    draft_items = [row[0] for row in cursor.fetchall()]

    matched_name = None

    for item in draft_items:
        if (
            item.lower() == product_name.lower()
            or product_name.lower() in item.lower()
        ):
            if matched_name is not None:
                connection.close()
                return {
                    "success": False,
                    "message": f"Multiple items match '{product_name}'."
                }
            matched_name = item

    if matched_name is None:
        connection.close()
        return {
            "success": False,
            "message": f"{product_name} is not in the draft bill."
        }

    cursor.execute(
        """
        DELETE FROM draft_bill_items
        WHERE bill_id = ? AND product_name = ?
        """,
        (bill_id, matched_name)
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": f"Removed {matched_name} from the draft bill."
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

    # Resolve the user's product name to the actual catalog name
    cursor.execute(
        """
        SELECT product_name
        FROM draft_bill_items
        WHERE bill_id = ?
        """,
        (bill_id,)
    )

    draft_items = [row[0] for row in cursor.fetchall()]

    matched_name = None

    for item in draft_items:
        if (
            item.lower() == product_name.lower()
            or product_name.lower() in item.lower()
        ):
            if matched_name is not None:
                connection.close()
                return {
                    "success": False,
                    "message": f"Multiple items match '{product_name}'."
                }
            matched_name = item

    if matched_name is None:
        connection.close()
        return {
            "success": False,
            "message": f"{product_name} is not in the draft bill."
        }

    cursor.execute(
        """
        SELECT name, stock, unit
        FROM products
        WHERE name = ?
        """,
        (matched_name,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        return {
            "success": False,
            "message": f"Product '{matched_name}' not found."
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