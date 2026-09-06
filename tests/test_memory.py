from database.memory import (
    save_memory,
    get_memory,
    get_all_memories
)


user_id = "test_user"


print("SAVE MEMORY")
print("--------------------")
print(
    save_memory(
        user_id,
        "shop_name",
        "Sri Lakshmi Stores"
    )
)


print("\nGET MEMORY")
print("--------------------")
print(
    get_memory(
        user_id,
        "shop_name"
    )
)


print("\nALL MEMORIES")
print("--------------------")
print(
    get_all_memories(
        user_id
    )
)