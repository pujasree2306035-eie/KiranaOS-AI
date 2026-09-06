from tools.analytics import (
    daily_sales_summary,
    get_top_selling_products,
    daily_close_report
)


print("DAILY SALES SUMMARY")
print("--------------------")
print(daily_sales_summary())


print("\nTOP SELLING PRODUCTS")
print("--------------------")
print(get_top_selling_products())


print("\nDAILY CLOSE REPORT")
print("--------------------")
print(daily_close_report())