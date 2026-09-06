import sqlite3

DATABASE = "kirana.db"


def add_product(
    name,
    category,
    stock,
    unit,
    cost_price,
    selling_price,
    mrp,
    gst_rate
):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM products WHERE LOWER(name) = LOWER(?)",
        (name,)
    )

    existing = cursor.fetchone()

    if existing:
        connection.close()
        return {
            "success": False,
            "message": f"Product '{existing[0]}' already exists."
        }

    if stock < 0:
        connection.close()
        return {
            "success": False,
            "message": "Stock cannot be negative."
        }

    if cost_price < 0 or selling_price < 0 or mrp < 0:
        connection.close()
        return {
            "success": False,
            "message": "Prices cannot be negative."
        }

    if gst_rate < 0 or gst_rate > 100:
        connection.close()
        return {
            "success": False,
            "message": "GST rate must be between 0 and 100."
        }

    cursor.execute(
        """
        INSERT INTO products
        (name, category, stock, unit, cost_price,
         selling_price, mrp, gst_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            category,
            stock,
            unit,
            cost_price,
            selling_price,
            mrp,
            gst_rate
        )
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": f"Product '{name}' added successfully.",
        "product": {
            "name": name,
            "category": category,
            "stock": stock,
            "unit": unit,
            "cost_price": cost_price,
            "selling_price": selling_price,
            "mrp": mrp,
            "gst_rate": gst_rate
        }
    }


def list_products():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name, category, stock, unit,
               cost_price, selling_price, mrp, gst_rate
        FROM products
        ORDER BY name
        """
    )

    products = cursor.fetchall()
    connection.close()

    result = []

    for product in products:
        result.append({
            "name": product[0],
            "category": product[1],
            "stock": product[2],
            "unit": product[3],
            "cost_price": product[4],
            "selling_price": product[5],
            "mrp": product[6],
            "gst_rate": product[7]
        })

    return {
        "success": True,
        "products": result
    }