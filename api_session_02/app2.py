from flask import Flask, jsonify, request
app = Flask(__name__)

BOOKS = []
_next_id = 1

@app.get("/books/<int:bid>")
def get_book(bid):
    book = next(
        (book for book in BOOKS if book["id"] == bid),
        None
    )
    if not book:
        return jsonify({"error": "not found"}), 404
    response = jsonify(book)

    response.headers["Cache-Control"] = "max-age=60"
    return response

@app.put("/books/<int:bid>")
def update_book_put(bid):
    book = next(
        (book for book in BOOKS if book["id"] == bid),
        None    
    )
    if not book:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    author = data.get("author")
    if not title or not author:
        return jsonify({"error": "need title+author"}), 422
    book["title"] = title.strip()
    book["author"] = author.strip()
    return jsonify(book), 200

@app.patch("/books/<int:bid>")
def update_book_patch(bid):
    book = next(
        (book for book in BOOKS if book["id"] == bid),
        None    
    )
    if not book:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}

    if "price" in data:
        try:
            price = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({"error": "price must be positive"}), 422

        if price <= 0:
            return jsonify({"error": "price must be positive"}), 422
        book["price"] = price

    for key in ("title", "author", "isbn"):
        if key in data:
            book[key] = data[key]

    return jsonify(book), 200

@app.post("/books")
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    data = request.get_json(silent=True)
    if data is None:
        return jsonify(error="invalid JSON"), 400

    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    if not title or not author:
        return jsonify(error="title and author are required"), 422
    book = {"id": _next_id, "title": title, "author": author}
    BOOKS.append(book); _next_id += 1
    response = jsonify(book)
    response.status_code = 201
    response.headers["Location"] = f"/books/{book['id']}"
    return response

@app.delete("/books/<int:bid>")
def delete_book(bid):

    index = next(
        (
            i for i, book in enumerate(BOOKS)
            if book["id"] == bid
        ),
        None
    )

    if index is None:
        return jsonify({"error": "not found"}), 404

    BOOKS.pop(index)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)