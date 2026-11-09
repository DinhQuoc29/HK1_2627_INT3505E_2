
from models.product import Product
from models import db


# API 1: Lấy danh sách sản phẩm
def list_products():
    rows = db.session.execute(
        db.select(Product)
    ).scalars().all()

    return [p.to_dict() for p in rows], 200


# API 2: Tạo sản phẩm mới
def create_product(body):
    product = Product(**body)

    db.session.add(product)
    db.session.commit()

    return product.to_dict(), 201


# API 3: Lấy sản phẩm theo ID
def get_product(id):
    product = db.get_or_404(Product, id)

    return product.to_dict(), 200
