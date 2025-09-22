from typing import Optional, List, Dict
from config import get_supabase

def _sb():
    return get_supabase()

def create_product(name: str, sku: str, price: float, stock: int = 0, category: str | None = None) -> Optional[Dict]:
    """
    Create a new product and return it.
    """
    payload = {"name": name, "sku": sku, "price": price, "stock": stock}
    if category is not None:
        payload["category"] = category

    # Insert product
    _sb().table("products").insert(payload).execute()

    # Fetch inserted row by unique SKU
    resp = _sb().table("products").select("*").eq("sku", sku).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_product_by_id(prod_id: int) -> Optional[Dict]:
    """
    Get product by ID.
    """
    resp = _sb().table("products").select("*").eq("id", prod_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_product_by_sku(sku: str) -> Optional[Dict]:
    """
    Get product by SKU.
    """
    resp = _sb().table("products").select("*").eq("sku", sku).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_product(prod_id: int, fields: Dict) -> Optional[Dict]:
    """
    Update a product and return the updated product.
    """
    _sb().table("products").update(fields).eq("id", prod_id).execute()
    resp = _sb().table("products").select("*").eq("id", prod_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_stock(prod_id: int, delta: int) -> Optional[Dict]:
    """
    Update stock by adding delta (can be negative).
    """
    # First get current stock
    current = get_product_by_id(prod_id)
    if not current:
        return None
    
    new_stock = max(0, current["stock"] + delta)  # Ensure stock doesn't go below 0
    return update_product(prod_id, {"stock": new_stock})

def delete_product(prod_id: int) -> Optional[Dict]:
    """
    Delete a product and return the deleted product.
    """
    # Fetch row before delete (so we can return it)
    resp_before = _sb().table("products").select("*").eq("id", prod_id).limit(1).execute()
    product = resp_before.data[0] if resp_before.data else None
    _sb().table("products").delete().eq("id", prod_id).execute()
    return product

def list_products(limit: int = 100, category: str | None = None) -> List[Dict]:
    """
    List products with optional category filtering.
    """
    q = _sb().table("products").select("*").order("id", desc=False).limit(limit)
    if category:
        q = q.eq("category", category)
    resp = q.execute()
    return resp.data or []
 
 