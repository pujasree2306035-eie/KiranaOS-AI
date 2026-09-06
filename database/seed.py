import sqlite3

connection = sqlite3.connect("kirana.db")
cursor = connection.cursor()

products = [
    ("Maggi 70g", "Instant Food", 50, "packet", 12, 14, 14, 5),
    ("Aashirvaad Atta 5kg", "Grocery", 20, "bag", 260, 290, 310, 5),
    ("Sugar 1kg", "Grocery", 30, "kg", 42, 48, 50, 5),
    ("Tata Salt 1kg", "Grocery", 25, "packet", 20, 25, 28, 5),
    ("Parle-G 800g", "Biscuits", 40, "packet", 55, 65, 70, 5),
    ("Surf Excel 1kg", "Cleaning", 15, "packet", 90, 110, 120, 18),
    ("Milk 500ml", "Dairy", 30, "packet", 22, 25, 27, 5),
    ("Coca Cola 750ml", "Beverages", 24, "bottle", 35, 40, 45, 28)
]

cursor.executemany("""
INSERT OR IGNORE INTO products
(name, category, stock, unit, cost_price, selling_price, mrp, gst_rate)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", products)

connection.commit()
connection.close()

print("Products added successfully!")