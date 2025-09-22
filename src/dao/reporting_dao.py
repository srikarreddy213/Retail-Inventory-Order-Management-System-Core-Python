from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import get_supabase

def _sb():
    return get_supabase()

def get_top_selling_products(limit: int = 5) -> List[Dict]:
    """
    Get top selling products by total quantity sold.
    
    Args:
        limit: Number of top products to return
        
    Returns:
        List[Dict]: List of products with total quantity sold
    """
    # This query joins order_items with products and sums quantities
    query = """
    SELECT 
        p.id,
        p.name,
        p.sku,
        p.price,
        p.category,
        COALESCE(SUM(oi.quantity), 0) as total_quantity_sold
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id
    WHERE o.status = 'COMPLETED' OR o.status IS NULL
    GROUP BY p.id, p.name, p.sku, p.price, p.category
    ORDER BY total_quantity_sold DESC
    LIMIT {}
    """.format(limit)
    
    resp = _sb().rpc('execute_sql', {'query': query}).execute()
    return resp.data or []

def get_total_revenue_last_month() -> Dict:
    """
    Get total revenue from completed orders in the last month.
    
    Returns:
        Dict: Total revenue and date range
    """
    # Calculate date range for last month
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    
    # Query for total revenue
    resp = _sb().table("orders").select("total_amount").eq("status", "COMPLETED").gte("created_at", first_day_last_month.isoformat()).lte("created_at", last_day_last_month.isoformat()).execute()
    
    total_revenue = sum(order.get("total_amount", 0) for order in resp.data or [])
    
    return {
        "total_revenue": total_revenue,
        "period": {
            "start_date": first_day_last_month.isoformat(),
            "end_date": last_day_last_month.isoformat()
        },
        "order_count": len(resp.data or [])
    }

def get_orders_per_customer() -> List[Dict]:
    """
    Get total orders placed by each customer.
    
    Returns:
        List[Dict]: List of customers with their order counts
    """
    # This query joins customers with orders and counts orders
    query = """
    SELECT 
        c.id,
        c.name,
        c.email,
        c.phone,
        c.city,
        COUNT(o.id) as total_orders,
        COALESCE(SUM(o.total_amount), 0) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email, c.phone, c.city
    ORDER BY total_orders DESC, total_spent DESC
    """
    
    resp = _sb().rpc('execute_sql', {'query': query}).execute()
    return resp.data or []

def get_customers_with_multiple_orders(min_orders: int = 2) -> List[Dict]:
    """
    Get customers who placed more than the specified number of orders.
    
    Args:
        min_orders: Minimum number of orders (default: 2)
        
    Returns:
        List[Dict]: List of customers with multiple orders
    """
    # This query filters customers by order count
    query = """
    SELECT 
        c.id,
        c.name,
        c.email,
        c.phone,
        c.city,
        COUNT(o.id) as total_orders,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        MAX(o.created_at) as last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email, c.phone, c.city
    HAVING COUNT(o.id) > {}
    ORDER BY total_orders DESC, total_spent DESC
    """.format(min_orders)
    
    resp = _sb().rpc('execute_sql', {'query': query}).execute()
    return resp.data or []

def get_sales_summary() -> Dict:
    """
    Get overall sales summary including total revenue, orders, and customers.
    
    Returns:
        Dict: Sales summary statistics
    """
    # Get total revenue from completed orders
    completed_orders_resp = _sb().table("orders").select("total_amount").eq("status", "COMPLETED").execute()
    total_revenue = sum(order.get("total_amount", 0) for order in completed_orders_resp.data or [])
    
    # Get total orders count
    orders_resp = _sb().table("orders").select("id").execute()
    total_orders = len(orders_resp.data or [])
    
    # Get completed orders count
    completed_orders_count = len(completed_orders_resp.data or [])
    
    # Get total customers
    customers_resp = _sb().table("customers").select("id").execute()
    total_customers = len(customers_resp.data or [])
    
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "completed_orders": completed_orders_count,
        "pending_orders": total_orders - completed_orders_count,
        "total_customers": total_customers,
        "average_order_value": total_revenue / completed_orders_count if completed_orders_count > 0 else 0
    }
