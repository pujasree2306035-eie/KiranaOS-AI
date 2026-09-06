from tools.draft_billing import add_item
from tools.billing import finalize_draft_bill


USER_ID = "final_test_user"


print("\nAdding items...")

print(add_item(USER_ID, "Maggi 70g", 2))
print(add_item(USER_ID, "Tata Salt 1kg", 1))


print("\nFinalizing draft...")

result = finalize_draft_bill(USER_ID)

print(result)