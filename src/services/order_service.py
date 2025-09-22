from typing import List, Dict
from dao import order_dao, product_dao, customer_dao
from services import payment_service

class OrderError(Exception):
    """Custom exception for order-related errors"""
    pass

def create_order(customer_id: int, items: List[Dict]) -> Dict:
    """
    Create a new order with comprehensive validation.
    
    Args:
        customer_id: ID of the customer placing the order
        items: List of items with prod_id and qty (e.g., [{"prod_id": 1, "qty": 2}])
    
    Returns:
        Dict: The created order with full details
        
    Raises:
        OrderError: If validation fails or order creation fails
    """
    # Validate customer exists
    customer = customer_dao.get_customer_by_id(customer_id)
    if not customer:
        raise OrderError(f"Customer {customer_id} not found")

    # Validate products and stock
    validated_items = []
    for item in items:
        prod_id = item.get("prod_id")
        qty = item.get("qty", 0)
        
        if not prod_id:
            raise OrderError("Product ID is required for each item")
        if qty <= 0:
            raise OrderError(f"Quantity must be positive for product {prod_id}")
            
        prod = product_dao.get_product_by_id(prod_id)
        if not prod:
            raise OrderError(f"Product {prod_id} not found")
        
        current_stock = prod.get("stock", 0)
        if current_stock < qty:
            raise OrderError(f"Insufficient stock for product {prod['name']} (ID: {prod_id}). Available: {current_stock}, Requested: {qty}")
        
        validated_items.append({
            "prod_id": prod["id"],
            "quantity": qty,
            "price": prod["price"]
        })

    try:
        # Deduct stock first (before creating order)
        for item in validated_items:
            product_dao.update_stock(item["prod_id"], -item["quantity"])

        # Create order
        order = order_dao.create_order(customer_id, validated_items)
        if not order:
            # If order creation failed, restore stock
            for item in validated_items:
                product_dao.update_stock(item["prod_id"], item["quantity"])
            raise OrderError("Failed to create order")
        
        # Create pending payment record
        try:
            payment = payment_service.create_pending_payment(order["id"], order["total_amount"])
            order["payment"] = payment
        except Exception as e:
            # If payment creation fails, we should still return the order
            # but log the error (in production, you might want to handle this differently)
            print(f"Warning: Failed to create payment record for order {order['id']}: {e}")
        
        return order
        
    except Exception as e:
        # If any error occurs after stock deduction, restore stock
        for item in validated_items:
            try:
                product_dao.update_stock(item["prod_id"], item["quantity"])
            except:
                pass  # Log this error in production
        raise OrderError(f"Order creation failed: {str(e)}")

def get_order_details(order_id: int) -> Dict:
    """
    Fetch full details of an order (order info + customer info + order items).
    
    Args:
        order_id: ID of the order to fetch
        
    Returns:
        Dict: Order with full details including customer and order items
        
    Raises:
        OrderError: If order not found
    """
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise OrderError(f"Order {order_id} not found")
    return order

def list_customer_orders(customer_id: int, limit: int = 100) -> List[Dict]:
    """
    List all orders of a customer.
    
    Args:
        customer_id: ID of the customer
        limit: Maximum number of orders to return
        
    Returns:
        List[Dict]: List of orders with full details
    """
    return order_dao.get_orders_by_customer(customer_id, limit)

def cancel_order(order_id: int) -> Dict:
    """
    Cancel an order (allowed only if status = PLACED).
    Restores product stock and updates order status to CANCELLED.
    
    Args:
        order_id: ID of the order to cancel
        
    Returns:
        Dict: The cancelled order
        
    Raises:
        OrderError: If order not found, already cancelled, or not in PLACED status
    """
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise OrderError(f"Order {order_id} not found")
    
    current_status = order.get("status")
    if current_status == "CANCELLED":
        raise OrderError("Order is already cancelled")
    
    if current_status != "PLACED":
        raise OrderError(f"Cannot cancel order with status '{current_status}'. Only PLACED orders can be cancelled.")

    try:
        # Get order items for stock restoration
        order_items = order_dao.get_order_items_for_restoration(order_id)
        
        # Restore stock
        for item in order_items:
            product_dao.update_stock(item["product_id"], item["quantity"])

        # Update order status to CANCELLED
        updated_order = order_dao.update_order_status(order_id, "CANCELLED")
        if not updated_order:
            # If status update failed, deduct stock again to maintain consistency
            for item in order_items:
                try:
                    product_dao.update_stock(item["product_id"], -item["quantity"])
                except:
                    pass
            raise OrderError("Failed to update order status")
        
        # Handle payment refund if payment exists
        try:
            refunded_payment = payment_service.refund_payment_by_order(order_id)
            updated_order["payment"] = refunded_payment
        except Exception as e:
            # Log warning but don't fail the cancellation
            print(f"Warning: Failed to refund payment for order {order_id}: {e}")
        
        return updated_order
        
    except Exception as e:
        # If any error occurs after stock restoration, deduct stock again
        order_items = order_dao.get_order_items_for_restoration(order_id)
        for item in order_items:
            try:
                product_dao.update_stock(item["product_id"], -item["quantity"])
            except:
                pass
        raise OrderError(f"Order cancellation failed: {str(e)}")

def mark_order_completed(order_id: int, payment_method: str = None) -> Dict:
    """
    Mark an order as COMPLETED after payment is successful.
    
    Args:
        order_id: ID of the order to mark as completed
        payment_method: Payment method (Cash/Card/UPI) - optional for backward compatibility
        
    Returns:
        Dict: The updated order
        
    Raises:
        OrderError: If order not found or already completed
    """
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise OrderError(f"Order {order_id} not found")
    
    current_status = order.get("status")
    if current_status == "COMPLETED":
        raise OrderError("Order is already completed")
    
    if current_status == "CANCELLED":
        raise OrderError("Cannot complete a cancelled order")
    
    # If payment method is provided, process the payment first
    if payment_method:
        try:
            processed_payment = payment_service.process_payment_by_order(order_id, payment_method)
            order["payment"] = processed_payment
        except Exception as e:
            raise OrderError(f"Payment processing failed: {e}")
    else:
        # For backward compatibility, just update order status
        updated_order = order_dao.update_order_status(order_id, "COMPLETED")
        if not updated_order:
            raise OrderError("Failed to update order status")
        return updated_order
    
    return order

def process_order_payment(order_id: int, payment_method: str) -> Dict:
    """
    Process payment for an order and mark it as completed.
    
    Args:
        order_id: ID of the order
        payment_method: Payment method (Cash/Card/UPI)
        
    Returns:
        Dict: The order with processed payment
        
    Raises:
        OrderError: If payment processing fails
    """
    try:
        # Process payment (this will also update order status to COMPLETED)
        processed_payment = payment_service.process_payment_by_order(order_id, payment_method)
        
        # Get updated order details
        order = order_dao.get_order_by_id(order_id)
        if order:
            order["payment"] = processed_payment
        
        return order
        
    except Exception as e:
        raise OrderError(f"Payment processing failed: {e}")