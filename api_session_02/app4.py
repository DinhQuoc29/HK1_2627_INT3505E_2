from flask import Flask, jsonify, make_response, request
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL,
            isbn TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def book_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "price": row["price"],
        "isbn": row["isbn"]
    }

@app.get("/books")
def list_books():

    DEFAULT_SIZE = 20
    MAX_SIZE = 100

    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify({
            "error": "page and size must be integers"
        }), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    author = request.args.get("author")
    q = request.args.get("q")

    conn = get_db()

    conditions = []
    params = []

    if author:
        conditions.append("LOWER(author) LIKE LOWER(?)")
        params.append(f"%{author}%")

    if q:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{q}%")

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_sql = f"""
        SELECT COUNT(*)
        FROM books
        {where_clause}
    """

    total = conn.execute(
        count_sql,
        params
    ).fetchone()[0]

    start = (page - 1) * size

    sql = f"""
        SELECT id, title, author, price, isbn
        FROM books
        {where_clause}
        ORDER BY id
        LIMIT ? OFFSET ?
    """

    rows = conn.execute(
        sql,
        params + [size, start]
    ).fetchall()

    conn.close()

    items = [
        book_to_dict(row)
        for row in rows
    ]

    total_pages = (total + size - 1) // size

    def url(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {
            "href": url(page)
        },
        "first": {
            "href": url(1)
        },
        "last": {
            "href": url(max(1, total_pages))
        }
    }

    if page > 1:
        links["prev"] = {
            "href": url(page - 1)
        }

    if page < total_pages:
        links["next"] = {
            "href": url(page + 1)
        }

    body = {
        "data": items,

        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages
        },

        "_links": links
    }

    response = make_response(
        jsonify(body),
        200
    )

    response.headers["Cache-Control"] = "public, max-age=30"

    return response

@app.get("/books/<int:bid>")
def get_book(bid):

    conn = get_db()

    row = conn.execute(
        """
        SELECT id, title, author, price, isbn
        FROM books
        WHERE id = ?
        """,
        (bid,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify({
            "error": "not found"
        }), 404

    response = make_response(
        jsonify(book_to_dict(row)),
        200
    )

    response.headers["Cache-Control"] = "public, max-age=60"

    return response

@app.post("/books")
def create_book():

    if not request.is_json:
        return jsonify({
            "error": "expected JSON"
        }), 415

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "invalid JSON"
        }), 400

    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()

    if not title or not author:
        return jsonify({
            "error": "title and author are required"
        }), 422

    price = data.get("price")
    isbn = data.get("isbn")

    if price is not None:
        try:
            price = float(price)
        except (ValueError, TypeError):
            return jsonify({
                "error": "price must be positive"
            }), 422

        if price <= 0:
            return jsonify({
                "error": "price must be positive"
            }), 422

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO books (title, author, price, isbn)
        VALUES (?, ?, ?, ?)
        """,
        (title, author, price, isbn)
    )

    book_id = cursor.lastrowid

    conn.commit()

    row = conn.execute(
        """
        SELECT id, title, author, price, isbn
        FROM books
        WHERE id = ?
        """,
        (book_id,)
    ).fetchone()

    conn.close()

    book = book_to_dict(row)

    response = jsonify(book)

    response.status_code = 201

    response.headers["Location"] = f"/books/{book_id}"

    return response

@app.put("/books/<int:bid>")
def update_book_put(bid):

    if not request.is_json:
        return jsonify({
            "error": "expected JSON"
        }), 415

    data = request.get_json(silent=True) or {}

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return jsonify({
            "error": "need title+author"
        }), 422

    title = title.strip()
    author = author.strip()

    conn = get_db()

    row = conn.execute(
        """
        SELECT id
        FROM books
        WHERE id = ?
        """,
        (bid,)
    ).fetchone()

    if row is None:
        conn.close()

        return jsonify({
            "error": "not found"
        }), 404

    conn.execute(
        """
        UPDATE books
        SET title = ?, author = ?
        WHERE id = ?
        """,
        (title, author, bid)
    )

    conn.commit()

    row = conn.execute(
        """
        SELECT id, title, author, price, isbn
        FROM books
        WHERE id = ?
        """,
        (bid,)
    ).fetchone()

    conn.close()

    return jsonify(book_to_dict(row)), 200

@app.patch("/books/<int:bid>")
def update_book_patch(bid):

    if not request.is_json:
        return jsonify({
            "error": "expected JSON"
        }), 415

    data = request.get_json(silent=True) or {}

    conn = get_db()

    row = conn.execute(
        """
        SELECT id, title, author, price, isbn
        FROM books
        WHERE id = ?
        """,
        (bid,)
    ).fetchone()

    if row is None:
        conn.close()

        return jsonify({
            "error": "not found"
        }), 404

    if "price" in data:

        try:
            price = float(data["price"])
        except (ValueError, TypeError):
            conn.close()

            return jsonify({
                "error": "price must be positive"
            }), 422

        if price <= 0:
            conn.close()

            return jsonify({
                "error": "price must be positive"
            }), 422

        conn.execute(
            """
            UPDATE books
            SET price = ?
            WHERE id = ?
            """,
            (price, bid)
        )

    if "title" in data:
        conn.execute(
            """
            UPDATE books
            SET title = ?
            WHERE id = ?
            """,
            (data["title"], bid)
        )

    if "author" in data:
        conn.execute(
            """
            UPDATE books
            SET author = ?
            WHERE id = ?
            """,
            (data["author"], bid)
        )

    if "isbn" in data:
        conn.execute(
            """
            UPDATE books
            SET isbn = ?
            WHERE id = ?
            """,
            (data["isbn"], bid)
        )

    conn.commit()

    row = conn.execute(
        """
        SELECT id, title, author, price, isbn
        FROM books
        WHERE id = ?
        """,
        (bid,)
    ).fetchone()

    conn.close()

    return jsonify(book_to_dict(row)), 200

@app.delete("/books/<int:bid>")
def delete_book(bid):

    conn = get_db()

    row = conn.execute(
        """
        SELECT id
        FROM books
        WHERE id = ?
        """,
        (bid,)
    ).fetchone()

    if row is None:
        conn.close()

        return jsonify({
            "error": "not found"
        }), 404

    conn.execute(
        """
        DELETE FROM books
        WHERE id = ?
        """,
        (bid,)
    )

    conn.commit()
    conn.close()

    return "", 204

@app.get("/orders/<int:oid>")
def get_order(oid):

    conn = get_db()

    row = conn.execute(
        """
        SELECT id, title, author
        FROM orders
        WHERE id = ?
        """,
        (oid,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify({
            "error": "not found"
        }), 404

    order = {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"]
    }

    response = make_response(
        jsonify(order),
        200
    )

    response.headers["Cache-Control"] = "public, max-age=60"

    return response

if __name__ == "__main__":

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )