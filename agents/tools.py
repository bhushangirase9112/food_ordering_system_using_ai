# agents/tools.py
from langchain.tools import tool
from config import MENU
from db.manager import db_manager
import json
from typing import List, Any

@tool
def get_menu() -> Any:
    """Return menu as JSON-friendly structure and as a formatted string."""
    menu_list = []
    text = "🍽️ Our Menu:\n"
    for key, data in MENU.items():
        menu_list.append({"id": key, "name": data["name"], "price": data["price"]})
        text += f"• {data['name']}: ${data['price']:.2f}\n"
    return {"menu": menu_list, "text": text}

@tool
def calculate_order_cost(items: List[dict]) -> Any:
    """
    items: [{"item": "chicken_sandwich", "quantity": 2}, ...]
    Returns structured breakdown and total.
    """
    total = 0.0
    breakdown = []
    for it in items:
        item_key = it.get("item", "").lower().replace(" ", "_")
        qty = int(it.get("quantity", 1))
        if item_key in MENU:
            unit = MENU[item_key]["price"]
            item_total = round(unit * qty, 2)
            total += item_total
            breakdown.append({
                "item": item_key,
                "name": MENU[item_key]["name"],
                "quantity": qty,
                "unit_price": unit,
                "total_price": item_total
            })
    total = round(total, 2)
    text = "💰 Cost Breakdown:\n"
    for b in breakdown:
        text += f"• {b['quantity']}x {b['name']}: ${b['total_price']:.2f}\n"
    text += f"\nTotal: ${total:.2f}"
    return {"breakdown": breakdown, "total": total, "text": text}

@tool
def create_order(user_id: str, items: List[dict]) -> Any:
    """Create order and return confirmation with ID."""
    order_items = []
    total_cost = 0.0
    for it in items:
        key = it.get("item", "").lower().replace(" ", "_")
        qty = int(it.get("quantity", 1))
        mods = it.get("modifications")
        if key in MENU:
            unit = MENU[key]["price"]
            item_total = round(unit * qty, 2)
            total_cost += item_total
            order_items.append({
                "item": key,
                "name": MENU[key]["name"],
                "quantity": qty,
                "unit_price": unit,
                "total_price": item_total,
                "modifications": mods
            })
    if not order_items:
        return {"error": "No valid items", "text": "❌ No valid items found. Please check the menu and try again."}
    rows = db_manager.execute_query(
        """INSERT INTO orders (user_id, items, total_cost, status)
           VALUES (%s, %s, %s, %s) RETURNING id, total_cost""",
        (user_id, json.dumps(order_items), total_cost, 'pending'),
        fetch=True
    )
    if not rows:
        return {"error": "db_insert_failed", "text": "❌ Failed to create order in the database."}
    order_id = rows[0]["id"]
    text = f"✅ Order #{order_id} created. Total: ${total_cost:.2f}. Status: pending."
    return {"order_id": order_id, "total_cost": total_cost, "items": order_items, "text": text}

@tool
def get_user_orders(user_id: str, limit: int = 10) -> Any:
    """Get all orders placed by a specific user. Returns a list of orders and a summary text."""
    rows = db_manager.execute_query(
        """SELECT id, items, total_cost, status, created_at
           FROM orders WHERE user_id = %s ORDER BY created_at DESC LIMIT %s""",
        (user_id, limit)
    )
    if not rows:
        return {"orders": [], "text": "📋 You don't have any orders yet."}
    for r in rows:
        if isinstance(r["items"], str):
            r["items"] = json.loads(r["items"])
    text = f"📋 You have {len(rows)} orders (showing up to {limit}):\n"
    for r in rows:
        text += f"- Order #{r['id']}: ${r['total_cost']:.2f} - {r['status'].upper()} ({r['created_at']})\n"
    return {"orders": rows, "text": text}

@tool
def get_order_details(order_id: int) -> Any:
    """Get detailed information about a specific order by order ID. Returns order details and a summary text."""
    rows = db_manager.execute_query(
        """SELECT id, user_id, items, total_cost, status, created_at, updated_at
           FROM orders WHERE id = %s""",
        (order_id,)
    )
    if not rows:
        return {"error": "not_found", "text": f"❌ Order #{order_id} not found."}
    r = rows[0]
    if isinstance(r["items"], str):
        r["items"] = json.loads(r["items"])
    text = f"📦 Order #{r['id']} — ${r['total_cost']:.2f} — {r['status'].upper()}\n"
    for it in r["items"]:
        mods = f" ({it.get('modifications')})" if it.get("modifications") else ""
        text += f"• {it['quantity']}x {it['name']}{mods} - ${it['total_price']:.2f}\n"
    return {"order": r, "text": text}

@tool
def cancel_order(order_id: int) -> Any:
    """Cancel an existing order by order ID. Returns confirmation or error text."""
    count = db_manager.execute_query(
        """UPDATE orders SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
           WHERE id = %s AND status = 'pending'""",
        (order_id,),
        fetch=False
    )
    if count == 0:
        return {"error": "cannot_cancel", "text": f"❌ Could not cancel order #{order_id}. It may not exist or is already processed."}
    return {"order_id": order_id, "text": f"✅ Order #{order_id} cancelled."}

@tool
def update_order_status(order_id: int, status: str) -> Any:
    """Update the status of an order. Status must be one of: pending, confirmed, preparing, ready, delivered, cancelled. Returns confirmation or error text."""
    valid_status = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
    if status not in valid_status:
        return {"error": "invalid_status", "text": f"❌ Invalid status. Valid: {', '.join(valid_status)}"}
    count = db_manager.execute_query(
        """UPDATE orders SET status = %s, updated_at = CURRENT_TIMESTAMP
           WHERE id = %s""",
        (status, order_id),
        fetch=False
    )
    if count == 0:
        return {"error": "not_found", "text": f"❌ Order #{order_id} not found."}
    return {"order_id": order_id, "text": f"✅ Order #{order_id} status updated to '{status}'."}

# List of all tools
all_tools = [
    get_menu,
    calculate_order_cost,
    create_order,
    get_user_orders,
    get_order_details,
    cancel_order,
    update_order_status,
]
