from typing import Optional, Dict, List
from config import get_supabase

def _sb():
    return get_supabase()

def create_payment(order_id: int, amount: float, status: str = "PENDING") -> Optional[Dict]:
    """
    Create a new payment record.
    
    Args:
        order_id: ID of the order this payment is for
        amount: Payment amount
        status: Payment status (PENDING, PAID, REFUNDED)
        
    Returns:
        Dict: The created payment record
    """
    payload = {
        "order_id": order_id,
        "amount": amount,
        "status": status,
        "payment_method": None
    }
    
    # Insert payment
    resp = _sb().table("payments").insert(payload).execute()
    return resp.data[0] if resp.data else None

def get_payment_by_id(payment_id: int) -> Optional[Dict]:
    """
    Get payment by ID.
    """
    resp = _sb().table("payments").select("*").eq("id", payment_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_payment_by_order_id(order_id: int) -> Optional[Dict]:
    """
    Get payment by order ID.
    """
    resp = _sb().table("payments").select("*").eq("order_id", order_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_payment(payment_id: int, fields: Dict) -> Optional[Dict]:
    """
    Update payment fields and return the updated payment.
    """
    _sb().table("payments").update(fields).eq("id", payment_id).execute()
    resp = _sb().table("payments").select("*").eq("id", payment_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def process_payment(payment_id: int, payment_method: str) -> Optional[Dict]:
    """
    Process a payment by updating status to PAID and setting payment method.
    """
    fields = {
        "status": "PAID",
        "payment_method": payment_method
    }
    return update_payment(payment_id, fields)

def refund_payment(payment_id: int) -> Optional[Dict]:
    """
    Mark payment as REFUNDED.
    """
    fields = {
        "status": "REFUNDED"
    }
    return update_payment(payment_id, fields)

def list_payments(limit: int = 100, status: str = None) -> List[Dict]:
    """
    List payments with optional status filtering.
    """
    q = _sb().table("payments").select("*").order("id", desc=False).limit(limit)
    if status:
        q = q.eq("status", status)
    resp = q.execute()
    return resp.data or []
