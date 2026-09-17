from flask import Flask, jsonify, make_response, request

app = Flask(__name__)

BOOKS = []
_next_id = 1

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

    filtered_books = BOOKS

    author = request.args.get("author")

    if author:
        filtered_books = [
            book
            for book in filtered_books
            if author.lower() in book["author"].lower()
        ]

    q = request.args.get("q")

    if q:
        filtered_books = [
            book
            for book in filtered_books
            if q.lower() in book["title"].lower()
        ]


    total = len(filtered_books)

    start = (page - 1) * size
    end = start + size

    items = filtered_books[start:end]

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

    book = next(
        (book for book in BOOKS if book["id"] == bid),
        None
    )

    if book is None:
        return jsonify({
            "error": "not found"
        }), 404

    response = make_response(
        jsonify(book),
        200
    )

    response.headers["Cache-Control"] = "public, max-age=60"

    return response

@app.post("/books")
def create_book():

    global _next_id

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

    book = {
        "id": _next_id,
        "title": title,
        "author": author
    }

    BOOKS.append(book)

    _next_id += 1

    response = jsonify(book)

    response.status_code = 201

    response.headers["Location"] = f"/books/{book['id']}"

    return response

@app.put("/books/<int:bid>")
def update_book_put(bid):

    book = next(
        (book for book in BOOKS if book["id"] == bid),
        None
    )

    if book is None:
        return jsonify({
            "error": "not found"
        }), 404

    data = request.get_json(silent=True) or {}

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return jsonify({
            "error": "need title+author"
        }), 422

    book["title"] = title.strip()
    book["author"] = author.strip()

    return jsonify(book), 200

@app.patch("/books/<int:bid>")
def update_book_patch(bid):

    book = next(
        (book for book in BOOKS if book["id"] == bid),
        None
    )

    if book is None:
        return jsonify({
            "error": "not found"
        }), 404

    data = request.get_json(silent=True) or {}
    if "price" in data:

        try:
            price = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({
                "error": "price must be positive"
            }), 422

        if price <= 0:
            return jsonify({
                "error": "price must be positive"
            }), 422

        book["price"] = price

    for key in ("title", "author", "isbn"):

        if key in data:
            book[key] = data[key]

    return jsonify(book), 200

@app.delete("/books/<int:bid>")
def delete_book(bid):

    index = next(
        (
            i
            for i, book in enumerate(BOOKS)
            if book["id"] == bid
        ),
        None
    )

    if index is None:
        return jsonify({
            "error": "not found"
        }), 404

    BOOKS.pop(index)

    return "", 204


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )