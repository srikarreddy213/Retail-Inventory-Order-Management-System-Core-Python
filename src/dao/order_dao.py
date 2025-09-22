from typing import Optional, Dict, List
from config import get_supabase

def _sb():
    return get_supabase()

def create_order(customer_id: int, items: List[Dict]) -> Optional[Dict]:
    """
    Create a new order with order items and return it.
    """
    # Calculate total amount
    total_amount = sum(item.get("price", 0) * item.get("quantity", 0) for item in items)
    
    order_payload = {
        "customer_id": customer_id,
        "total_amount": total_amount,
        "status": "PLACED"
    }
    
    # Insert order
    order_resp = _sb().table("orders").insert(order_payload).execute()
    order = order_resp.data[0] if order_resp.data else None
    
    if not order:
        return None
    
    # Insert order items
    order_items = []
    for item in items:
        order_item_payload = {
            "order_id": order["id"],
            "product_id": item["prod_id"],
            "quantity": item["quantity"],
            "price": item["price"]
        }
        item_resp = _sb().table("order_items").insert(order_item_payload).execute()
        if item_resp.data:
            order_items.append(item_resp.data[0])
    
    # Add order items to the order object
    order["order_items"] = order_items
    return order

def get_order_by_id(order_id: int) -> Optional[Dict]:
    """
    Get order by ID with full details including customer and order items.
    """
    # Get order details
    order_resp = _sb().table("orders").select("*").eq("id", order_id).limit(1).execute()
    order = order_resp.data[0] if order_resp.data else None
    
    if not order:
        return None
    
    # Get customer details
    customer_resp = _sb().table("customers").select("*").eq("id", order["customer_id"]).limit(1).execute()
    order["customer"] = customer_resp.data[0] if customer_resp.data else None
    
    # Get order items with product details
    items_resp = _sb().table("order_items").select("*, products(*)").eq("order_id", order_id).execute()
    order["order_items"] = items_resp.data or []
    
    return order

def update_order_status(order_id, status):
    """
    Update order status and return the updated order.
    """
    _sb().table("orders").update({"status": status}).eq("id", order_id).execute()
    resp = _sb().table("orders").select("*").eq("id", order_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_order(order_id, fields):
    """
    Update order fields and return the updated order.
    """
    _sb().table("orders").update(fields).eq("id", order_id).execute()
    resp = _sb().table("orders").select("*").eq("id", order_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def delete_order(order_id):
    """
    Delete order and return the deleted order.
    """
    resp_before = _sb().table("orders").select("*").eq("id", order_id).limit(1).execute()
    order = resp_before.data[0] if resp_before.data else None
    _sb().table("orders").delete().eq("id", order_id).execute()
    return order

def list_orders(limit=100, customer_id=None, status=None):
    """
    List orders with optional filtering.
    """
    q = _sb().table("orders").select("*").order("id", desc=False).limit(limit)
    if customer_id:
        q = q.eq("customer_id", customer_id)
    if status:
        q = q.eq("status", status)
    resp = q.execute()
    return resp.data or []

def get_orders_by_customer(customer_id: int, limit: int = 100) -> List[Dict]:
    """
    Get all orders for a specific customer with full details.
    """
    # Get orders for customer
    orders_resp = _sb().table("orders").select("*").eq("customer_id", customer_id).order("id", desc=False).limit(limit).execute()
    orders = orders_resp.data or []
    
    # Get customer details
    customer_resp = _sb().table("customers").select("*").eq("id", customer_id).limit(1).execute()
    customer = customer_resp.data[0] if customer_resp.data else None
    
    # Add customer details and order items to each order
    for order in orders:
        order["customer"] = customer
        
        # Get order items with product details
        items_resp = _sb().table("order_items").select("*, products(*)").eq("order_id", order["id"]).execute()
        order["order_items"] = items_resp.data or []
    
    return orders

def get_order_items_for_restoration(order_id: int) -> List[Dict]:
    """
    Get order items for stock restoration during cancellation.
    """
    items_resp = _sb().table("order_items").select("product_id, quantity").eq("order_id", order_id).execute()
    return items_resp.data or []