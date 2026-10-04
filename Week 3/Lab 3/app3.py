from flask import Flask, request, jsonify
import base64
import json

app = Flask(__name__)

orders = [
    {
        "id": 1,
        "customer_id": 101,
        "status": "paid",
        "total": 100000,
        "created_at": "2026-10-01T10:00:00"
    },
    {
        "id": 2,
        "customer_id": 102,
        "status": "pending",
        "total": 200000,
        "created_at": "2026-10-01T11:00:00"
    },
    {
        "id": 3,
        "customer_id": 101,
        "status": "paid",
        "total": 300000,
        "created_at": "2026-10-01T12:00:00"
    },
    {
        "id": 4,
        "customer_id": 103,
        "status": "cancelled",
        "total": 150000,
        "created_at": "2026-10-01T13:00:00"
    },
    {
        "id": 5,
        "customer_id": 102,
        "status": "paid",
        "total": 500000,
        "created_at": "2026-10-01T14:00:00"
    },
    {
        "id": 6,
        "customer_id": 101,
        "status": "pending",
        "total": 250000,
        "created_at": "2026-10-01T15:00:00"
    },
]

def encode_cursor(order_id):
    data = {
        "id": order_id
    }

    json_data = json.dumps(data)

    return base64.urlsafe_b64encode(
        json_data.encode()
    ).decode()

def decode_cursor(cursor):
    try:
        decoded = base64.urlsafe_b64decode(
            cursor.encode()
        ).decode()

        data = json.loads(decoded)

        if "id" not in data:
            raise ValueError()

        return data["id"]

    except Exception:
        raise ValueError("Invalid cursor")

@app.route("/orders", methods=["GET"])
def get_orders():

    # =========================
    # 1. Get query parameters
    # =========================

    cursor = request.args.get("cursor")

    status = request.args.get("status")

    customer_id = request.args.get("customer_id")

    sort = request.args.get("sort", "id")

    fields = request.args.get("fields")

    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({
            "error": "limit must be an integer"
        }), 400

    if limit <= 0:
        return jsonify({
            "error": "limit must be greater than 0"
        }), 400


    # =========================
    # 2. Filter
    # =========================

    result = orders.copy()

    if status:
        result = [
            order for order in result
            if order["status"] == status
        ]

    if customer_id:

        try:
            customer_id = int(customer_id)
        except ValueError:
            return jsonify({
                "error": "customer_id must be an integer"
            }), 400

        result = [
            order for order in result
            if order["customer_id"] == customer_id
        ]


    # =========================
    # 3. Sort
    # =========================

    allowed_sort_fields = [
        "id",
        "total",
        "created_at"
    ]

    descending = sort.startswith("-")

    sort_field = sort[1:] if descending else sort

    if sort_field not in allowed_sort_fields:
        return jsonify({
            "error": "Invalid sort field"
        }), 400

    result.sort(
        key=lambda order: order[sort_field],
        reverse=descending
    )


    # =========================
    # 4. Cursor
    # =========================

    if cursor:

        try:
            cursor_id = decode_cursor(cursor)

        except ValueError:
            return jsonify({
                "error": "Invalid cursor"
            }), 400

        # tìm vị trí của order
        index = next(
            (
                i
                for i, order in enumerate(result)
                if order["id"] == cursor_id
            ),
            None
        )

        if index is None:
            return jsonify({
                "error": "Invalid cursor"
            }), 400

        # lấy các record phía sau cursor
        result = result[index + 1:]


    # =========================
    # 5. Pagination
    # =========================

    has_more = len(result) > limit

    page = result[:limit]


    # =========================
    # 6. Next cursor
    # =========================

    next_cursor = None

    if has_more:

        last_order = page[-1]

        next_cursor = encode_cursor(
            last_order["id"]
        )


    # =========================
    # 7. Sparse fieldsets
    # =========================

    if fields:

        requested_fields = [
            field.strip()
            for field in fields.split(",")
        ]

        allowed_fields = {
            "id",
            "customer_id",
            "status",
            "total",
            "created_at"
        }

        invalid_fields = [
            field
            for field in requested_fields
            if field not in allowed_fields
        ]

        if invalid_fields:
            return jsonify({
                "error": "Invalid fields",
                "fields": invalid_fields
            }), 400

        page = [
            {
                field: order[field]
                for field in requested_fields
            }
            for order in page
        ]


    # =========================
    # 8. Response
    # =========================

    return jsonify({
        "data": page,
        "pagination": {
            "limit": limit,
            "next_cursor": next_cursor,
            "has_more": has_more
        }
    })

if __name__ == "__main__":
    app.run(debug=True)