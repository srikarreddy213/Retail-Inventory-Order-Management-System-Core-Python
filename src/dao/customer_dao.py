from typing import Optional, Dict
from config import get_supabase

def _sb():
    return get_supabase()

def create_customer(name, email, phone, city):
    """
    Create a new customer and return it.
    """
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "city": city
    }
    
    # Insert customer
    _sb().table("customers").insert(payload).execute()
    
    # Fetch inserted row by unique email
    resp = _sb().table("customers").select("*").eq("email", email).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_customer_by_id(customer_id):
    """
    Get customer by ID.
    """
    resp = _sb().table("customers").select("*").eq("id", customer_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_customer_by_email(email):
    """
    Get customer by email.
    """
    resp = _sb().table("customers").select("*").eq("email", email).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_customer(customer_id, fields):
    """
    Update customer fields.
    """
    _sb().table("customers").update(fields).eq("id", customer_id).execute()
    resp = _sb().table("customers").select("*").eq("id", customer_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def delete_customer(customer_id):
    """
    Delete customer and return the deleted customer.
    """
    resp_before = _sb().table("customers").select("*").eq("id", customer_id).limit(1).execute()
    customer = resp_before.data[0] if resp_before.data else None
    _sb().table("customers").delete().eq("id", customer_id).execute()
    return customer

def list_customers(limit=100):
    """
    List all customers.
    """
    resp = _sb().table("customers").select("*").order("id", desc=False).limit(limit).execute()
    return resp.data or []