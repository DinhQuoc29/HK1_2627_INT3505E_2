from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 1
BOOKS = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925
    }
]

def find_book(book_id):
    return next (
        (book for book in BOOKS if book["id"] == book_id),
        None
    )

#LiST - GET /books
@app.route("/books", methods=["GET"])
def get_books():
    q = request.args.get("q", "").strip().lower()

    books = BOOKS
    if q:
        books = [
            book for book in BOOKS
            if q in book["title"].lower()
            or q in book["author"].lower()
        ]

    sort = request.args.get("sort")

    if sort:
        if sort not in ["title", "year"]:
            return jsonify({"error": "sort must be title or year"}), 400

        books = sorted(
            books,
            key=lambda book: book[sort]
        )

    limit = int(request.args.get("limit", 100))
    return jsonify(books[:limit]), 200

#DETAIL - GET /books/<int:id>
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200

#CREATE - POST /books
@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    author = body.get("author")
    year = body.get("year")

    if not title or not author or year is None:
        return jsonify({"error": "need title + author + year"}), 400

    if not isinstance(year, (int, float)) or isinstance(year, bool):
        return jsonify({"error": "year must be a number"}), 400

    if year < 1900:
        return jsonify({"error": "year must be >= 1900"}), 400
    
    _next += 1
    
    book = {
        "id": _next,
        "title": title,
        "author": author,
        "year": year
    }
    BOOKS.append(book)
    return jsonify(book), 201

#PUT /books/<id>
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": "not found"}), 404

    body = request.get_json(silent=True) or {}
    title = body.get("title")
    author = body.get("author")
    year = body.get("year")

    if not title or not author or year is None:
        return jsonify({"error": "need title + author + year"}), 400

    if not isinstance(year, (int, float)) or isinstance(year, bool):
        return jsonify({"error": "year must be a number"}), 400

    if year < 1900:
        return jsonify({"error": "year must be >= 1900"}), 400

    book.update({
        "title": title,
        "author": author,
        "year": year
    })
    return jsonify(book), 200


#DELETE /books/<id>
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": "not found"}), 404
    BOOKS.remove(book)
    return jsonify(""), 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)