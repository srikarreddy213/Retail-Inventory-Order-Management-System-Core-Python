import argparse
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import product_service, order_service, payment_service, reporting_service
from dao import product_dao, customer_dao
 
def cmd_product_add(args):
    try:
        p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
        print("Created product:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_product_list(args):
    ps = product_dao.list_products(limit=100)
    print(json.dumps(ps, indent=2, default=str))
 
def cmd_customer_add(args):
    try:
        c = customer_dao.create_customer(args.name, args.email, args.phone, args.city)
        print("Created customer:")
        print(json.dumps(c, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_order_create(args):
    # items provided as prod_id:qty strings
    items = []
    for item in args.item:
        try:
            pid, qty = item.split(":")
            items.append({"prod_id": int(pid), "qty": int(qty)})
        except Exception:
            print("Invalid item format:", item)
            return
    try:
        ord = order_service.create_order(args.customer, items)
        print("Order created:")
        print(json.dumps(ord, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_order_show(args):
    try:
        o = order_service.get_order_details(args.order)
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def cmd_order_cancel(args):
    try:
        o = order_service.cancel_order(args.order)
        print("Order cancelled (updated):")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_list_customer(args):
    try:
        orders = order_service.list_customer_orders(args.customer, args.limit)
        print(f"Orders for customer {args.customer}:")
        print(json.dumps(orders, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_complete(args):
    try:
        o = order_service.mark_order_completed(args.order)
        print("Order marked as completed:")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_pay(args):
    try:
        o = order_service.process_order_payment(args.order, args.method)
        print("Payment processed and order completed:")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_payment_process(args):
    try:
        p = payment_service.process_payment_by_order(args.order, args.method)
        print("Payment processed:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_payment_refund(args):
    try:
        p = payment_service.refund_payment_by_order(args.order)
        print("Payment refunded:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_payment_show(args):
    try:
        p = payment_service.get_payment_details(args.payment)
        print("Payment details:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_top_products(args):
    try:
        products = reporting_service.get_top_selling_products(args.limit)
        print(f"Top {args.limit} selling products:")
        print(json.dumps(products, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_revenue(args):
    try:
        revenue = reporting_service.get_total_revenue_last_month()
        print("Revenue report for last month:")
        print(json.dumps(revenue, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_customer_orders(args):
    try:
        customers = reporting_service.get_orders_per_customer()
        print("Orders per customer:")
        print(json.dumps(customers, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_multiple_orders(args):
    try:
        customers = reporting_service.get_customers_with_multiple_orders(args.min_orders)
        print(f"Customers with more than {args.min_orders} orders:")
        print(json.dumps(customers, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_summary(args):
    try:
        summary = reporting_service.get_sales_summary()
        print("Sales summary:")
        print(json.dumps(summary, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_report_all(args):
    try:
        all_reports = reporting_service.generate_all_reports()
        print("All reports:")
        print(json.dumps(all_reports, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
 
def build_parser():
    parser = argparse.ArgumentParser(prog="retail-cli")
    sub = parser.add_subparsers(dest="cmd")
 
    # product add/list
    p_prod = sub.add_parser("product", help="product commands")
    pprod_sub = p_prod.add_subparsers(dest="action")
    addp = pprod_sub.add_parser("add")
    addp.add_argument("--name", required=True)
    addp.add_argument("--sku", required=True)
    addp.add_argument("--price", type=float, required=True)
    addp.add_argument("--stock", type=int, default=0)
    addp.add_argument("--category", default=None)
    addp.set_defaults(func=cmd_product_add)
 
    listp = pprod_sub.add_parser("list")
    listp.set_defaults(func=cmd_product_list)
 
    # customer add
    pcust = sub.add_parser("customer")
    pcust_sub = pcust.add_subparsers(dest="action")
    addc = pcust_sub.add_parser("add")
    addc.add_argument("--name", required=True)
    addc.add_argument("--email", required=True)
    addc.add_argument("--phone", required=True)
    addc.add_argument("--city", default=None)
    addc.set_defaults(func=cmd_customer_add)
 
    # order
    porder = sub.add_parser("order")
    porder_sub = porder.add_subparsers(dest="action")
 
    createo = porder_sub.add_parser("create")
    createo.add_argument("--customer", type=int, required=True)
    createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
    createo.set_defaults(func=cmd_order_create)
 
    showo = porder_sub.add_parser("show")
    showo.add_argument("--order", type=int, required=True)
    showo.set_defaults(func=cmd_order_show)
 
    cano = porder_sub.add_parser("cancel")
    cano.add_argument("--order", type=int, required=True)
    cano.set_defaults(func=cmd_order_cancel)

    listo = porder_sub.add_parser("list")
    listo.add_argument("--customer", type=int, required=True)
    listo.add_argument("--limit", type=int, default=100)
    listo.set_defaults(func=cmd_order_list_customer)

    completo = porder_sub.add_parser("complete")
    completo.add_argument("--order", type=int, required=True)
    completo.set_defaults(func=cmd_order_complete)

    payo = porder_sub.add_parser("pay")
    payo.add_argument("--order", type=int, required=True)
    payo.add_argument("--method", required=True, choices=["Cash", "Card", "UPI"])
    payo.set_defaults(func=cmd_order_pay)

    # payment commands
    ppay = sub.add_parser("payment")
    ppay_sub = ppay.add_subparsers(dest="action")

    processp = ppay_sub.add_parser("process")
    processp.add_argument("--order", type=int, required=True)
    processp.add_argument("--method", required=True, choices=["Cash", "Card", "UPI"])
    processp.set_defaults(func=cmd_payment_process)

    refundp = ppay_sub.add_parser("refund")
    refundp.add_argument("--order", type=int, required=True)
    refundp.set_defaults(func=cmd_payment_refund)

    showp = ppay_sub.add_parser("show")
    showp.add_argument("--payment", type=int, required=True)
    showp.set_defaults(func=cmd_payment_show)

    # report commands
    preport = sub.add_parser("report")
    preport_sub = preport.add_subparsers(dest="action")

    topp = preport_sub.add_parser("top-products")
    topp.add_argument("--limit", type=int, default=5)
    topp.set_defaults(func=cmd_report_top_products)

    revenue = preport_sub.add_parser("revenue")
    revenue.set_defaults(func=cmd_report_revenue)

    customer_orders = preport_sub.add_parser("customer-orders")
    customer_orders.set_defaults(func=cmd_report_customer_orders)

    multiple = preport_sub.add_parser("multiple-orders")
    multiple.add_argument("--min-orders", type=int, default=2)
    multiple.set_defaults(func=cmd_report_multiple_orders)

    summary = preport_sub.add_parser("summary")
    summary.set_defaults(func=cmd_report_summary)

    all_reports = preport_sub.add_parser("all")
    all_reports.set_defaults(func=cmd_report_all)

    return parser
 
def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)
 
if __name__ == "__main__":
    main()
 