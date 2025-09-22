from typing import List, Dict
from dao import reporting_dao

class ReportingError(Exception):
    """Custom exception for reporting-related errors"""
    pass

def get_top_selling_products(limit: int = 5) -> List[Dict]:
    """
    Get top 5 selling products by total quantity sold.
    
    Args:
        limit: Number of top products to return (default: 5)
        
    Returns:
        List[Dict]: List of top selling products with quantities
        
    Raises:
        ReportingError: If report generation fails
    """
    try:
        if limit <= 0:
            raise ReportingError("Limit must be a positive number")
        
        products = reporting_dao.get_top_selling_products(limit)
        
        # Format the results for better presentation
        formatted_products = []
        for product in products:
            formatted_products.append({
                "product_id": product.get("id"),
                "product_name": product.get("name"),
                "sku": product.get("sku"),
                "category": product.get("category"),
                "price": product.get("price"),
                "total_quantity_sold": product.get("total_quantity_sold", 0),
                "total_revenue": product.get("price", 0) * product.get("total_quantity_sold", 0)
            })
        
        return formatted_products
        
    except Exception as e:
        raise ReportingError(f"Failed to generate top selling products report: {str(e)}")

def get_total_revenue_last_month() -> Dict:
    """
    Get total revenue in the last month.
    
    Returns:
        Dict: Total revenue with period information
        
    Raises:
        ReportingError: If report generation fails
    """
    try:
        revenue_data = reporting_dao.get_total_revenue_last_month()
        
        return {
            "total_revenue": revenue_data.get("total_revenue", 0),
            "period": revenue_data.get("period"),
            "order_count": revenue_data.get("order_count", 0),
            "formatted_revenue": f"${revenue_data.get('total_revenue', 0):.2f}"
        }
        
    except Exception as e:
        raise ReportingError(f"Failed to generate revenue report: {str(e)}")

def get_orders_per_customer() -> List[Dict]:
    """
    Get total orders placed by each customer.
    
    Returns:
        List[Dict]: List of customers with their order counts
        
    Raises:
        ReportingError: If report generation fails
    """
    try:
        customers = reporting_dao.get_orders_per_customer()
        
        # Format the results for better presentation
        formatted_customers = []
        for customer in customers:
            formatted_customers.append({
                "customer_id": customer.get("id"),
                "customer_name": customer.get("name"),
                "email": customer.get("email"),
                "phone": customer.get("phone"),
                "city": customer.get("city"),
                "total_orders": customer.get("total_orders", 0),
                "total_spent": customer.get("total_spent", 0),
                "formatted_total_spent": f"${customer.get('total_spent', 0):.2f}"
            })
        
        return formatted_customers
        
    except Exception as e:
        raise ReportingError(f"Failed to generate orders per customer report: {str(e)}")

def get_customers_with_multiple_orders(min_orders: int = 2) -> List[Dict]:
    """
    Get customers who placed more than 2 orders.
    
    Args:
        min_orders: Minimum number of orders (default: 2)
        
    Returns:
        List[Dict]: List of customers with multiple orders
        
    Raises:
        ReportingError: If report generation fails
    """
    try:
        if min_orders < 1:
            raise ReportingError("Minimum orders must be at least 1")
        
        customers = reporting_dao.get_customers_with_multiple_orders(min_orders)
        
        # Format the results for better presentation
        formatted_customers = []
        for customer in customers:
            formatted_customers.append({
                "customer_id": customer.get("id"),
                "customer_name": customer.get("name"),
                "email": customer.get("email"),
                "phone": customer.get("phone"),
                "city": customer.get("city"),
                "total_orders": customer.get("total_orders", 0),
                "total_spent": customer.get("total_spent", 0),
                "last_order_date": customer.get("last_order_date"),
                "formatted_total_spent": f"${customer.get('total_spent', 0):.2f}"
            })
        
        return formatted_customers
        
    except Exception as e:
        raise ReportingError(f"Failed to generate multiple orders report: {str(e)}")

def get_sales_summary() -> Dict:
    """
    Get overall sales summary including key metrics.
    
    Returns:
        Dict: Sales summary with key metrics
        
    Raises:
        ReportingError: If report generation fails
    """
    try:
        summary = reporting_dao.get_sales_summary()
        
        return {
            "total_revenue": summary.get("total_revenue", 0),
            "total_orders": summary.get("total_orders", 0),
            "completed_orders": summary.get("completed_orders", 0),
            "pending_orders": summary.get("pending_orders", 0),
            "total_customers": summary.get("total_customers", 0),
            "average_order_value": summary.get("average_order_value", 0),
            "formatted_revenue": f"${summary.get('total_revenue', 0):.2f}",
            "formatted_avg_order_value": f"${summary.get('average_order_value', 0):.2f}",
            "completion_rate": (summary.get("completed_orders", 0) / summary.get("total_orders", 1)) * 100 if summary.get("total_orders", 0) > 0 else 0
        }
        
    except Exception as e:
        raise ReportingError(f"Failed to generate sales summary: {str(e)}")

def generate_all_reports() -> Dict:
    """
    Generate all reports in one call for dashboard purposes.
    
    Returns:
        Dict: All reports combined
        
    Raises:
        ReportingError: If any report generation fails
    """
    try:
        return {
            "sales_summary": get_sales_summary(),
            "top_selling_products": get_top_selling_products(5),
            "revenue_last_month": get_total_revenue_last_month(),
            "orders_per_customer": get_orders_per_customer(),
            "customers_multiple_orders": get_customers_with_multiple_orders(2)
        }
        
    except Exception as e:
        raise ReportingError(f"Failed to generate all reports: {str(e)}")
