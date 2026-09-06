import sqlite3

connection = sqlite3.connect("kirana.db")
cursor = connection.cursor()

cursor.execute("SELECT * FROM products")

products = cursor.fetchall()

for product in products:
    print(product)

connection.close()