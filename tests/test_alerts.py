from tools.alerts import (
    get_low_stock,
    get_reorder_suggestions
)


print("LOW STOCK")
print("--------------------")
print(get_low_stock())


print("\nREORDER SUGGESTIONS")
print("--------------------")
print(get_reorder_suggestions())