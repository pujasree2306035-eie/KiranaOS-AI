from tools.inventory import check_stock, receive_stock, reduce_stock


def stock_tool(product_name):
    return check_stock(product_name)


def receive_stock_tool(product_name, quantity):
    return receive_stock(product_name, quantity)


def sell_stock_tool(product_name, quantity):
    return reduce_stock(product_name, quantity)