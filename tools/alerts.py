import sqlite3

DATABASE = "kirana.db"


def get_low_stock(threshold=10):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, stock, unit, selling_price
        FROM products
        WHERE stock <= ?
        ORDER BY stock ASC
    """, (threshold,))

    products = cursor.fetchall()
    connection.close()

    if not products:
        return {
            "success": True,
            "message": "No products are currently low in stock.",
            "products": []
        }

    low_stock = []

    for name, stock, unit, selling_price in products:

        target_stock = threshold * 3

        reorder_quantity = max(
            0,
            target_stock - stock
        )

        if stock <= threshold / 2:
            priority = "HIGH"
        else:
            priority = "MEDIUM"

        low_stock.append({
            "product": name,
            "current_stock": stock,
            "unit": unit,
            "reorder_quantity": reorder_quantity,
            "priority": priority,
            "selling_price": selling_price
        })

    return {
        "success": True,
        "message": f"{len(low_stock)} product(s) need attention.",
        "products": low_stock
    }


def get_reorder_suggestions():
    return get_low_stock(threshold=10)