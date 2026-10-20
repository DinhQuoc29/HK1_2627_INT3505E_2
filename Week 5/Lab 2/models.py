from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()

# Bảng trung gian cho quan hệ N:M giữa Book và Author.
book_authors = db.Table(
    "book_authors",
    db.Column("book_id", db.Integer, db.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    db.Column("author_id", db.Integer, db.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True, index=True)
    price_vnd = db.Column(db.Integer, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    category = db.relationship("Category", back_populates="books")
    authors = db.relationship("Author", secondary=book_authors, back_populates="books")
    reviews = db.relationship("Review", back_populates="book", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("price_vnd >= 0", name="ck_book_price_nonnegative"),
        CheckConstraint("stock >= 0", name="ck_book_stock_nonnegative"),
    )

    def to_dict(self, include_relations=True):
        data = {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category_id": self.category_id,
        }
        if include_relations:
            data["category"] = self.category.to_dict() if self.category else None
            data["authors"] = [a.to_dict() for a in self.authors]
        return data


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    bio = db.Column(db.Text, nullable=True)

    books = db.relationship("Book", secondary=book_authors, back_populates="authors")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "bio": self.bio}


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)

    books = db.relationship("Book", back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    display_name = db.Column(db.String(120), nullable=False)

    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "email": self.email, "display_name": self.display_name}


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    book = db.relationship("Book", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_1_5"),
        UniqueConstraint("book_id", "user_id", name="uq_review_book_user"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "content": self.content,
            "book_id": self.book_id,
            "user_id": self.user_id,
        }
