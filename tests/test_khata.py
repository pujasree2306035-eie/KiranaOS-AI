from tools.khata import (
    add_credit,
    record_payment,
    get_balance
)


customer = "Arun"


print("\n1. Add credit")
print(add_credit(customer, 500))


print("\n2. Check balance")
print(get_balance(customer))


print("\n3. Record payment")
print(record_payment(customer, 200))


print("\n4. Check final balance")
print(get_balance(customer))