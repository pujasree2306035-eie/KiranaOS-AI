from tools.draft_billing import (
    add_item,
    remove_item,
    update_quantity,
    view_draft
)


USER_ID = "test_user"


print("\n1. Add Maggi")
print(add_item(USER_ID, "Maggi 70g", 2))


print("\n2. Add Tata Salt")
print(add_item(USER_ID, "Tata Salt 1kg", 1))


print("\n3. View Draft")
print(view_draft(USER_ID))


print("\n4. Change Maggi to 3")
print(update_quantity(USER_ID, "Maggi 70g", 3))


print("\n5. Remove Tata Salt")
print(remove_item(USER_ID, "Tata Salt 1kg"))


print("\n6. Final Draft")
print(view_draft(USER_ID))