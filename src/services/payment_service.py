from typing import Dict, Optional
from datetime import datetime
from dao import payment_dao, order_dao

class PaymentError(Exception):
    """Custom exception for payment-related errors"""
    pass

def create_pending_payment(order_id: int, amount: float) -> Dict:
    """
    Create a pending payment record when an order is created.
    
    Args:
        order_id: ID of the order
        amount: Payment amount (total order amount)
        
    Returns:
        Dict: The created payment record
        
    Raises:
        PaymentError: If payment creation fails
    """
    try:
        payment = payment_dao.create_payment(order_id, amount, "PENDING")
        if not payment:
            raise PaymentError("Failed to create payment record")
        return payment
    except Exception as e:
        raise PaymentError(f"Payment creation failed: {str(e)}")

def process_payment(payment_id: int, payment_method: str) -> Dict:
    """
    Process a payment by marking it as PAID and updating the order status to COMPLETED.
    
    Args:
        payment_id: ID of the payment to process
        payment_method: Payment method (Cash/Card/UPI)
        
    Returns:
        Dict: The processed payment
        
    Raises:
        PaymentError: If payment processing fails
    """
    # Validate payment method
    valid_methods = ["Cash", "Card", "UPI"]
    if payment_method not in valid_methods:
        raise PaymentError(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
    
    # Get payment details
    payment = payment_dao.get_payment_by_id(payment_id)
    if not payment:
        raise PaymentError(f"Payment {payment_id} not found")
    
    current_status = payment.get("status")
    if current_status == "PAID":
        raise PaymentError("Payment is already processed")
    
    if current_status == "REFUNDED":
        raise PaymentError("Cannot process a refunded payment")
    
    try:
        # Process payment
        processed_payment = payment_dao.process_payment(payment_id, payment_method)
        if not processed_payment:
            raise PaymentError("Failed to process payment")
        
        # Update order status to COMPLETED
        order_id = payment["order_id"]
        updated_order = order_dao.update_order_status(order_id, "COMPLETED")
        if not updated_order:
            # If order update fails, revert payment status
            payment_dao.update_payment(payment_id, {"status": "PENDING", "payment_method": None})
            raise PaymentError("Failed to update order status")
        
        return processed_payment
        
    except Exception as e:
        raise PaymentError(f"Payment processing failed: {str(e)}")

def process_payment_by_order(order_id: int, payment_method: str) -> Dict:
    """
    Process payment by order ID (convenience method).
    
    Args:
        order_id: ID of the order
        payment_method: Payment method (Cash/Card/UPI)
        
    Returns:
        Dict: The processed payment
    """
    payment = payment_dao.get_payment_by_order_id(order_id)
    if not payment:
        raise PaymentError(f"No payment found for order {order_id}")
    
    return process_payment(payment["id"], payment_method)

def refund_payment(payment_id: int) -> Dict:
    """
    Refund a payment (typically called when order is cancelled).
    
    Args:
        payment_id: ID of the payment to refund
        
    Returns:
        Dict: The refunded payment
        
    Raises:
        PaymentError: If refund fails
    """
    payment = payment_dao.get_payment_by_id(payment_id)
    if not payment:
        raise PaymentError(f"Payment {payment_id} not found")
    
    current_status = payment.get("status")
    if current_status == "REFUNDED":
        raise PaymentError("Payment is already refunded")
    
    try:
        refunded_payment = payment_dao.refund_payment(payment_id)
        if not refunded_payment:
            raise PaymentError("Failed to refund payment")
        
        return refunded_payment
        
    except Exception as e:
        raise PaymentError(f"Payment refund failed: {str(e)}")

def refund_payment_by_order(order_id: int) -> Dict:
    """
    Refund payment by order ID (convenience method).
    
    Args:
        order_id: ID of the order
        
    Returns:
        Dict: The refunded payment
    """
    payment = payment_dao.get_payment_by_order_id(order_id)
    if not payment:
        raise PaymentError(f"No payment found for order {order_id}")
    
    return refund_payment(payment["id"])

def get_payment_details(payment_id: int) -> Dict:
    """
    Get payment details with order information.
    
    Args:
        payment_id: ID of the payment
        
    Returns:
        Dict: Payment with order details
        
    Raises:
        PaymentError: If payment not found
    """
    payment = payment_dao.get_payment_by_id(payment_id)
    if not payment:
        raise PaymentError(f"Payment {payment_id} not found")
    
    # Get order details
    order = order_dao.get_order_by_id(payment["order_id"])
    if order:
        payment["order"] = order
    
    return payment
