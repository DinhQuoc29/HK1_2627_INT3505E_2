from flask import Blueprint, jsonify, request
from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError
from models import db, Book, Category, Author

books_bp = Blueprint("books", __name__)

SORT_FIELDS = {
    "id": Book.id,
    "title": Book.title,
    "price_vnd": Book.price_vnd,
    "stock": Book.stock,
}


def error(message, status=400):
    return jsonify({"error": message}), status


def parse_int_arg(name, default, minimum=None, maximum=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"Query parameter '{name}' phải là số nguyên.")
    if minimum is not None and value < minimum:
        raise ValueError(f"'{name}' phải >= {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"'{name}' phải <= {maximum}.")
    return value


def apply_sort(query, sort_value):
    """sort=price_vnd,-title: '-' nghĩa là giảm dần; hỗ trợ nhiều khóa."""
    terms = [term.strip() for term in (sort_value or "id").split(",") if term.strip()]
    if not terms:
        terms = ["id"]
    for term in terms:
        descending = term.startswith("-")
        field_name = term[1:] if term[:1] in ("-", "+") else term
        if field_name not in SORT_FIELDS:
            raise ValueError(
                f"Trường sort không hợp lệ: '{field_name}'. "
                f"Các trường hỗ trợ: {', '.join(SORT_FIELDS)}."
            )
        column = SORT_FIELDS[field_name]
        query = query.order_by(desc(column) if descending else asc(column))
    # Thêm id làm khóa phụ để thứ tự ổn định khi phân trang.
    if not any(t.lstrip("+-") == "id" for t in terms):
        query = query.order_by(asc(Book.id))
    return query


@books_bp.get("")
def list_books():
    """GET /api/v1/books?strategy=offset&page=1&per_page=10&genre=fiction&sort=-price_vnd,title
       GET /api/v1/books?strategy=cursor&limit=10&cursor=12
    """
    try:
        strategy = request.args.get("strategy", "offset").lower()
        genre = request.args.get("genre")
        sort_value = request.args.get("sort", "id")
        query = Book.query.join(Category, isouter=True)

        if genre:
            # genre có thể là slug hoặc tên category, so sánh không phân biệt hoa thường.
            query = query.filter(
                db.or_(Category.slug.ilike(genre), Category.name.ilike(genre))
            )

        query = apply_sort(query, sort_value)

        if strategy == "offset":
            page = parse_int_arg("page", 1, minimum=1)
            per_page = parse_int_arg("per_page", 10, minimum=1, maximum=100)
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            return jsonify({
                "items": [book.to_dict() for book in items],
                "pagination": {
                    "strategy": "offset",
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page,
                    "has_next": page * per_page < total,
                    "has_prev": page > 1,
                },
            })

        if strategy == "cursor":
            limit = parse_int_arg("limit", 10, minimum=1, maximum=100)
            # Cursor đơn giản: id của bản ghi cuối cùng đã nhận.
            # Để giữ đúng ý nghĩa cursor, chiến lược này yêu cầu sort theo id.
            if sort_value not in ("id", "+id", "id asc", "id,"):
                return error("strategy=cursor hiện yêu cầu sort=id; dùng offset nếu cần sort nhiều khóa.")
            cursor_raw = request.args.get("cursor")
            if cursor_raw:
                try:
                    cursor_id = int(cursor_raw)
                except ValueError:
                    return error("cursor phải là id dạng số nguyên.")
                query = query.filter(Book.id > cursor_id)
            items = query.order_by(Book.id.asc()).limit(limit + 1).all()
            has_next = len(items) > limit
            items = items[:limit]
            next_cursor = items[-1].id if items and has_next else None
            return jsonify({
                "items": [book.to_dict() for book in items],
                "pagination": {
                    "strategy": "cursor",
                    "limit": limit,
                    "next_cursor": next_cursor,
                    "has_next": has_next,
                },
            })

        return error("strategy phải là 'offset' hoặc 'cursor'.")
    except ValueError as exc:
        return error(str(exc))


@books_bp.get("/<int:book_id>")
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return error("Không tìm thấy sách.", 404)
    return jsonify(book.to_dict())


@books_bp.post("")
def create_book():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Body phải là JSON object.")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return error("title là bắt buộc và không được để trống.")

    try:
        price_vnd = int(data.get("price_vnd", 0))
        stock = int(data.get("stock", 0))
        if price_vnd < 0 or stock < 0:
            return error("price_vnd và stock phải >= 0.")

        category_id = data.get("category_id")
        category = db.session.get(Category, category_id) if category_id is not None else None
        if category_id is not None and category is None:
            return error("category_id không tồn tại.")

        author_ids = data.get("author_ids", [])
        if not isinstance(author_ids, list):
            return error("author_ids phải là một mảng.")
        authors = []
        if author_ids:
            authors = Author.query.filter(Author.id.in_(author_ids)).all()
            if len(authors) != len(set(author_ids)):
                return error("Một hoặc nhiều author_ids không tồn tại.")

        book = Book(
            title=title.strip(),
            isbn=data.get("isbn"),
            price_vnd=price_vnd,
            stock=stock,
            category=category,
            authors=authors,
        )
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except (TypeError, ValueError):
        db.session.rollback()
        return error("price_vnd và stock phải là số nguyên hợp lệ.")
    except IntegrityError:
        db.session.rollback()
        return error("ISBN đã tồn tại hoặc dữ liệu vi phạm ràng buộc.", 409)


@books_bp.patch("/<int:book_id>")
@books_bp.put("/<int:book_id>")
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return error("Không tìm thấy sách.", 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Body phải là JSON object.")

    try:
        if "title" in data:
            if not isinstance(data["title"], str) or not data["title"].strip():
                return error("title không được để trống.")
            book.title = data["title"].strip()
        if "isbn" in data:
            book.isbn = data["isbn"]
        for field in ("price_vnd", "stock"):
            if field in data:
                value = int(data[field])
                if value < 0:
                    return error(f"{field} phải >= 0.")
                setattr(book, field, value)
        if "category_id" in data:
            category_id = data["category_id"]
            category = db.session.get(Category, category_id) if category_id is not None else None
            if category_id is not None and category is None:
                return error("category_id không tồn tại.")
            book.category = category
        if "author_ids" in data:
            author_ids = data["author_ids"]
            if not isinstance(author_ids, list):
                return error("author_ids phải là một mảng.")
            authors = Author.query.filter(Author.id.in_(author_ids)).all() if author_ids else []
            if len(authors) != len(set(author_ids)):
                return error("Một hoặc nhiều author_ids không tồn tại.")
            book.authors = authors

        db.session.commit()
        return jsonify(book.to_dict())
    except (TypeError, ValueError):
        db.session.rollback()
        return error("price_vnd và stock phải là số nguyên hợp lệ.")
    except IntegrityError:
        db.session.rollback()
        return error("ISBN đã tồn tại hoặc dữ liệu vi phạm ràng buộc.", 409)


@books_bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return error("Không tìm thấy sách.", 404)
    db.session.delete(book)
    db.session.commit()
    return "", 204
