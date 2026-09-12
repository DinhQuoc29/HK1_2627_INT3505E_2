from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 1
BOOKS = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
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
    limit = int(request.args.get("limit", 100))
    return jsonify(BOOKS[:limit]), 200

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
    title, author = body.get("title"), body.get("author")

    if not title or not author:
        return jsonify({"error": "need title+author"}), 400
    _next += 1
    book = {
        "id": _next,
        "title": title,
        "author": author
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
    title, author = body.get("title"), body.get("author")

    if not title or not author:
        return jsonify({"error": "need title+author"}), 400

    book.update({
        "title": title,
        "author": author
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