import os
import json
import inspect

from dotenv import load_dotenv
from openai import OpenAI

from tools.inventory import (
    check_stock,
    receive_stock,
    reduce_stock
)

from tools.billing import (
    calculate_item,
    finalize_bill,
    finalize_draft_bill
)

from tools.draft_billing import (
    add_item,
    remove_item,
    update_quantity,
    view_draft
)

from tools.khata import (
    add_credit,
    record_payment,
    get_balance
)

from tools.alerts import (
    get_low_stock,
    get_reorder_suggestions
)

from tools.analytics import (
    daily_sales_summary,
    daily_close_report
)

from tools.invoice import create_invoice
from tools.reports import create_business_report

from tools.product_management import (
    add_product,
    list_products
)

from database.memory import (
    save_memory,
    get_memory,
    get_all_memories
)


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing from .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/pujasree2306035-eie/KiranaOS-AI",
        "X-Title": "KiranaOS AI"
    }
)
MODEL = "minimax/minimax-m3:free"

SYSTEM_PROMPT = """
You are KiranaOS AI, an AI operations assistant for an Indian retail shop.

Your job is to help the shopkeeper manage inventory, billing, customers,
credit, sales and business operations.

You must use tools to perform real actions and retrieve real information.

IMPORTANT RULES:

1. Never invent product stock.
2. Never invent prices.
3. Never invent customer balances.
4. Always use the appropriate tool for real business data.
5. Never sell more stock than is available.
6. Stock must be reduced only when a bill is finalized.
7. Draft bills do not reduce inventory.
8. GST must be calculated using the product GST rate.
9. BILLING RULE: When the user asks to create, start, make, prepare, or add products to a bill, you MUST use add_item_tool for EVERY product mentioned. NEVER use finalize_bill_tool for these requests.
10. For a bill containing multiple products, call add_item_tool separately for each product and quantity.
11. After adding the requested products, use view_draft_tool to verify the draft before replying.
12. Draft bills MUST remain drafts until the user explicitly asks to finalize them.
13. When the user asks to remove an item, use remove_item_tool.
14. When the user asks to change quantity, use update_quantity_tool.
15. When the user asks to show the bill, use view_draft_tool.
16. When the user explicitly asks to finalize the current draft bill, use finalize_draft_bill_tool.
17. NEVER claim that an item was added to a bill unless the corresponding tool successfully added it.
18. NEVER finalize a bill unless the user explicitly asks for finalization.
19. NEVER use finalize_bill_tool for normal bill creation or draft editing.
14. When a bill is finalized, provide a clear summary of items, subtotal, GST and total.
15. When the user asks about low stock, use the low-stock tool.
16. When the user asks what products need to be reordered or what should be purchased,
    use the reorder suggestion tool.
17. For reorder suggestions, clearly show product name, current stock,
    suggested reorder quantity and priority.
18. When the user asks to add a new product, collect all required information
    before calling the add-product tool.
19. When the user asks for all products, use the product-list tool.
20. When the user asks for today's sales, use the daily sales summary tool.
21. When the user asks for a daily business report or daily closing report,
    use the daily close report tool.
22. When the user asks for a PowerPoint business report, use the business report tool.
23. When the user tells you to remember a preference or important shop detail,
    save it using the memory tool.
24. When the user asks what you remember, retrieve their saved memories.
25. Use remembered preferences when they are relevant to the conversation.
26. Keep responses simple and useful for a shopkeeper.
27. Do not expose internal tool names or implementation details.
28. Do not use a hard-coded keyword router. Decide which tool is appropriate
    based on the user's request.
29. When a business report is successfully generated, clearly tell the user
    that the PowerPoint report has been created.
"""


def _json_result(value):
    return json.dumps(value, default=str)


def process_message(message, user_id="telegram_user"):

    artifact_file = None

    def check_stock_tool(product_name: str) -> str:
        """Check the current stock of a product."""
        return check_stock(product_name)

    def receive_stock_tool(product_name: str, quantity: float) -> str:
        """Receive new stock for an existing product."""
        return receive_stock(product_name, quantity)

    def sell_stock_tool(product_name: str, quantity: float) -> str:
        """Sell stock directly when explicitly requested."""
        return reduce_stock(product_name, quantity)

    def calculate_item_tool(product_name: str, quantity: float) -> str:
        """Calculate price and GST for a product."""
        return _json_result(calculate_item(product_name, quantity))

    def finalize_bill_tool(product_name: str, quantity: float) -> str:
        """Finalize a single-item bill."""
        return _json_result(finalize_bill(product_name, quantity))

    def add_item_tool(product_name: str, quantity: float) -> str:
        """Add a product to the current draft bill.

        MUST be called whenever the user asks to create, start, make,
        prepare, or add a product to a bill. For multiple products,
        call this tool separately for each product. This tool does NOT
        finalize the bill and does NOT reduce stock.
        """
        return _json_result(add_item(user_id, product_name, quantity))

    def remove_item_tool(product_name: str) -> str:
        """Remove a product from the current draft bill."""
        return _json_result(remove_item(user_id, product_name))

    def update_quantity_tool(product_name: str, quantity: float) -> str:
        """Update the quantity of a product in the current draft bill."""
        return _json_result(update_quantity(user_id, product_name, quantity))

    def view_draft_tool() -> str:
        """Show and verify the current draft bill."""
        return _json_result(view_draft(user_id))

    def finalize_draft_bill_tool() -> str:
        """Finalize the current draft bill and create a PDF invoice.

        Use ONLY when the user explicitly asks to finalize, complete,
        confirm, or checkout the current draft bill.
        """
        nonlocal artifact_file

        result = finalize_draft_bill(user_id)

        if result.get("success"):
            invoice_file = create_invoice(result)
            result["invoice_file"] = invoice_file
            artifact_file = invoice_file

        return _json_result(result)

    def add_credit_tool(customer_name: str, amount: float) -> str:
        """Add credit to a customer's Khata account."""
        return _json_result(add_credit(customer_name, amount))

    def record_payment_tool(customer_name: str, amount: float) -> str:
        """Record a customer payment."""
        return _json_result(record_payment(customer_name, amount))

    def get_balance_tool(customer_name: str) -> str:
        """Check a customer's outstanding balance."""
        return _json_result(get_balance(customer_name))

    def get_low_stock_tool(threshold: float = 10) -> str:
        """Find products whose stock is at or below the threshold."""
        return _json_result(get_low_stock(threshold))

    def get_reorder_suggestions_tool() -> str:
        """Suggest products that should be reordered."""
        return _json_result(get_reorder_suggestions())

    def daily_sales_summary_tool() -> str:
        """Get today's sales summary."""
        return _json_result(daily_sales_summary())

    def daily_close_report_tool() -> str:
        """Get today's complete business closing information."""
        return _json_result(daily_close_report())

    def business_report_tool() -> str:
        """Generate today's business analysis as a PowerPoint file."""
        nonlocal artifact_file

        result = create_business_report()

        if result.get("success"):
            artifact_file = result.get("file_path")

        return _json_result(result)

    def add_product_tool(
        name: str,
        category: str,
        stock: float,
        unit: str,
        cost_price: float,
        selling_price: float,
        mrp: float,
        gst_rate: float
    ) -> str:
        """Add a new product to inventory."""
        return _json_result(
            add_product(
                name,
                category,
                stock,
                unit,
                cost_price,
                selling_price,
                mrp,
                gst_rate
            )
        )

    def list_products_tool() -> str:
        """List all products in inventory."""
        return _json_result(list_products())

    def save_memory_tool(memory_key: str, memory_value: str) -> str:
        """Save a user preference or important shop detail permanently."""
        return _json_result(
            save_memory(user_id, memory_key, memory_value)
        )

    def get_memory_tool(memory_key: str) -> str:
        """Retrieve a specific saved memory."""
        return _json_result(
            get_memory(user_id, memory_key)
        )

    def get_all_memories_tool() -> str:
        """Retrieve all saved memories for the current user."""
        return _json_result(get_all_memories(user_id))

    tool_functions = [
        check_stock_tool,
        receive_stock_tool,
        calculate_item_tool,
        add_item_tool,
        remove_item_tool,
        update_quantity_tool,
        view_draft_tool,
        finalize_draft_bill_tool,
        add_credit_tool,
        record_payment_tool,
        get_balance_tool,
        get_low_stock_tool,
        get_reorder_suggestions_tool,
        daily_sales_summary_tool,
        daily_close_report_tool,
        business_report_tool,
        add_product_tool,
        list_products_tool,
        save_memory_tool,
        get_memory_tool,
        get_all_memories_tool
    ]

    function_map = {fn.__name__: fn for fn in tool_functions}

    def python_type_to_schema(annotation):
        if annotation is str:
            return {"type": "string"}
        if annotation is int:
            return {"type": "integer"}
        if annotation is float:
            return {"type": "number"}
        if annotation is bool:
            return {"type": "boolean"}
        return {"type": "string"}

    tools = []

    for fn in tool_functions:
        signature = inspect.signature(fn)
        properties = {}
        required = []

        for name, parameter in signature.parameters.items():
            properties[name] = python_type_to_schema(parameter.annotation)

            if parameter.default is inspect.Parameter.empty:
                required.append(name)

        tools.append({
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": inspect.getdoc(fn) or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        })

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]

    try:
        for _ in range(8):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            assistant_dict = {
                "role": "assistant",
                "content": assistant_message.content
            }

            if assistant_message.tool_calls:
                assistant_dict["tool_calls"] = []

                for tool_call in assistant_message.tool_calls:
                    assistant_dict["tool_calls"].append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })

            messages.append(assistant_dict)

            if not assistant_message.tool_calls:
                break

            for tool_call in assistant_message.tool_calls:
                name = tool_call.function.name

                if name not in function_map:
                    tool_result = {
                        "success": False,
                        "error": f"Unknown tool: {name}"
                    }
                else:
                    try:
                        arguments = json.loads(tool_call.function.arguments or "{}")
                        tool_result = function_map[name](**arguments)
                    except Exception as exc:
                        tool_result = {
                            "success": False,
                            "error": str(exc)
                        }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })

        result = {
            "text": assistant_message.content or "Done."
        }

        if artifact_file and os.path.exists(artifact_file):
            result["artifact_file"] = artifact_file

            if artifact_file.lower().endswith(".pdf"):
                result["invoice_file"] = artifact_file

            elif artifact_file.lower().endswith(".pptx"):
                result["report_file"] = artifact_file

        return result

    except Exception as exc:
        return {
            "text": f"AI service error: {exc}",
            "error": str(exc)
        }
