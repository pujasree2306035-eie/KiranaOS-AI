from tools.product_management import add_product, list_products

result = add_product(
    "Britannia Good Day 100g",
    "Biscuits",
    25,
    "packet",
    10,
    15,
    18,
    5
)

print(result)

print("\nAll products:")
print(list_products())