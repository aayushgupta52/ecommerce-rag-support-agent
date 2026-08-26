import json
from pathlib import Path

SAFE_FIELDS = [
    "order_id",
    "membership_tier",
    "placed_at",
    "status",
    "status_updated_at",
    "shipped_at",
    "delivered_at",
    "carrier",
    "tracking_number",
    "estimated_delivery",
    "customer_safe_message",
]


def load_orders(path: str | Path = "data/orders.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def lookup_order(order_id: str, orders_data: dict) -> dict | None:
    if not order_id or not order_id.strip():
        return None

    normalized = order_id.strip().upper()

    for order in orders_data.get("orders", []):
        if order.get("order_id", "").upper() == normalized:
            safe_result = {field: order.get(field) for field in SAFE_FIELDS}
            safe_result["items"] = [
                {
                    "name": item.get("name"),
                    "quantity": item.get("quantity"),
                    "final_sale": item.get("final_sale"),
                }
                for item in order.get("items", [])
            ]
            return safe_result

    return None

def build_status_guidance(order: dict) -> str:
    status = order.get("status")

    if status in ("cancelled", "returned"):
        return (
            f"This order is {status}. Do not reference estimated_delivery "
            f"or imply the order is still arriving, even if that field has a value."
        )
    if status == "shipped" and order.get("estimated_delivery") is None:
        return (
            "This order has shipped but no delivery estimate is available. "
            "State that clearly. Do not calculate or invent a date."
        )
    if status == "exception":
        return (
            "This order requires support review. Recommend a human handoff "
            "and do not speculate about resolution."
        )
    return ""


if __name__ == "__main__":
    orders_data = load_orders()
    print(f"Snapshot time: {orders_data.get('snapshot_at')}")
    print(f"Total orders in dataset: {len(orders_data.get('orders', []))}\n")

    test_ids = ["ORD-1001", "ord-1001 ", "ORD-9999", "", "   "]

    for oid in test_ids:
        print(f"Looking up: {oid!r}")
        result = lookup_order(oid, orders_data)
        if result is None:
            print("  -> Not found / invalid input\n")
            continue
        print(f"  -> Found: status={result['status']}, items={result['items']}")
        guidance = build_status_guidance(result)
        if guidance:
            print(f"  -> Guidance: {guidance}")
        print()