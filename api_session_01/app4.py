from flask import Flask, jsonify, request
app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 3, "title": "1984", "author": "George Orwell"},
    {"id": 4, "title": "Pride and Prejudice", "author": "Jane Austen"}
]

@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = next((book for book in BOOKS if str(book["id"]) == book_id), None)
    if book is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200

@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    items = [book
             for book in BOOKS
             if q in book["title"].lower()
    ]
    items = items[:limit]
    return jsonify({"items": items}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)