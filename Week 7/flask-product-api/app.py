
import connexion

from models import db

# Khởi tạo Connexion
app = connexion.FlaskApp(
    __name__,
    specification_dir="openapi/"
)

# Cấu hình Flask
app.app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///products.db"
)
app.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Khởi tạo database
db.init_app(app.app)

# Tạo bảng nếu chưa tồn tại
with app.app.app_context():
    from models.product import Product
    db.create_all()

# Đăng ký OpenAPI Specification
app.add_api(
    "products.yaml",
    validate_responses=True
)

if __name__ == "__main__":
    app.run(port=5000)
