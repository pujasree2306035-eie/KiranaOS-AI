from tools.inventory import check_stock, receive_stock, reduce_stock

print(check_stock("Maggi 70g"))

print(receive_stock("Maggi 70g", 20))

print(check_stock("Maggi 70g"))

print(reduce_stock("Maggi 70g", 10))

print(check_stock("Maggi 70g"))

print(reduce_stock("Maggi 70g", 100))