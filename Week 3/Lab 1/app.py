from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Giả lập database in-memory
posts_db = [
    {
        "id": 1,
        "title": "REST API Design",
        "content": "Nguyen ly thiet ke RESTful API chuan...",
        "author_id": 101,
        "tags": ["api", "rest"]
    }
]
current_id = 1


@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    """Lấy danh sách posts có hỗ trợ lọc query params."""
    tag = request.args.get("tag")
    if tag:
        filtered = [p for p in posts_db if tag in p.get("tags", [])]
        return jsonify({"data": filtered, "total": len(filtered)}), 200

    return jsonify({"data": posts_db, "total": len(posts_db)}), 200


@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    """Tạo mới một bài viết."""
    global current_id
    payload = request.get_json(silent=True)
    if not payload or not payload.get("title") or not payload.get("content"):
        return jsonify({"error": "Bad Request", "message": "Title and content are required"}), 400

    current_id += 1
    new_post = {
        "id": current_id,
        "title": payload["title"],
        "content": payload["content"],
        "author_id": payload.get("author_id"),
        "tags": payload.get("tags", [])
    }
    posts_db.append(new_post)
    return jsonify({"message": "Post created successfully", "data": new_post}), 201


@app.route("/api/v1/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """Lấy chi tiết một bài viết theo ID."""
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Not Found", "message": f"Post {post_id} does not exist"}), 404
    return jsonify({"data": post}), 200


@app.route("/api/v1/posts/<int:post_id>", methods=["PATCH"])
def update_post(post_id):
    """Cập nhật một phần nội dung bài viết."""
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Not Found", "message": f"Post {post_id} does not exist"}), 404

    payload = request.get_json(silent=True) or {}
    post["title"] = payload.get("title", post["title"])
    post["content"] = payload.get("content", post["content"])
    post["tags"] = payload.get("tags", post["tags"])

    return jsonify({"message": "Post updated successfully", "data": post}), 200


@app.route("/api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Xóa một bài viết."""
    global posts_db
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Not Found", "message": f"Post {post_id} does not exist"}), 404

    posts_db = [p for p in posts_db if p["id"] != post_id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)