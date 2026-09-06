import sqlite3
from datetime import datetime

DATABASE = "kirana.db"


def daily_sales_summary():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(quantity), 0),
            COALESCE(SUM(subtotal), 0),
            COALESCE(SUM(gst_amount), 0),
            COALESCE(SUM(total), 0)
        FROM sales
        WHERE DATE(created_at) = ?
    """, (today,))

    sales_count, quantity, subtotal, gst, total = cursor.fetchone()

    connection.close()

    return {
        "success": True,
        "date": today,
        "number_of_sales": sales_count,
        "quantity_sold": quantity,
        "subtotal": round(subtotal, 2),
        "gst_collected": round(gst, 2),
        "total_sales": round(total, 2)
    }


def get_top_selling_products():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT
            product_name,
            SUM(quantity) AS quantity_sold,
            SUM(total) AS sales_value
        FROM sales
        WHERE DATE(created_at) = ?
        GROUP BY product_name
        ORDER BY quantity_sold DESC
        LIMIT 5
    """, (today,))

    products = cursor.fetchall()

    connection.close()

    result = []

    for product_name, quantity_sold, sales_value in products:
        result.append({
            "product": product_name,
            "quantity_sold": quantity_sold,
            "sales_value": round(sales_value, 2)
        })

    return result


def daily_close_report():
    summary = daily_sales_summary()

    top_products = get_top_selling_products()

    return {
        "success": True,
        "date": summary["date"],
        "number_of_sales": summary["number_of_sales"],
        "quantity_sold": summary["quantity_sold"],
        "subtotal": summary["subtotal"],
        "gst_collected": summary["gst_collected"],
        "total_sales": summary["total_sales"],
        "top_selling_products": top_products,
        "status": "Daily business report ready."
    }