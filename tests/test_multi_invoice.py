from tools.draft_billing import add_item
from tools.billing import finalize_draft_bill
from tools.invoice import create_invoice


USER_ID = "invoice_test_user"


print("\nAdding products...")

print(add_item(USER_ID, "Maggi 70g", 1))
print(add_item(USER_ID, "Tata Salt 1kg", 1))


print("\nFinalizing bill...")

bill = finalize_draft_bill(USER_ID)

print(bill)


if bill["success"]:

    file_path = create_invoice(bill)

    print("\nInvoice created:")
    print(file_path)

else:

    print("\nInvoice was not created.")