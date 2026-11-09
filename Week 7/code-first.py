from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields, validate

app = Flask(__name__)

app.config["API_TITLE"] = "Product Service API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

PRODUCTS_DB = [
    {"id": 1, "sku": "IPHONE-15", "name": "iPhone 15", "price_cents": 20000000},
    {"id": 2, "sku": "MACBOOK-M3", "name": "MacBook Pro M3", "price_cents": 45000000},
]

class ProductInSchema(Schema):
    """Schema validate dữ liệu gửi lên khi tạo mới"""
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))

class ProductOutSchema(Schema):
    """Schema định dạng dữ liệu trả về cho client"""
    id = fields.Int(dump_only=True) 
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()

blp = Blueprint("products", __name__, url_prefix="/api/v1/products", description="Các thao tác với Product")

@blp.route("")
class ProductList(MethodView):
    
    @blp.response(200, ProductOutSchema(many=True))
    def get(self):
        """Lấy danh sách tất cả sản phẩm"""
        return PRODUCTS_DB

    @blp.arguments(ProductInSchema)          
    @blp.response(201, ProductOutSchema)    
    def post(self, product_data):
        """Tạo một sản phẩm mới"""
        new_id = len(PRODUCTS_DB) + 1
        new_product = {
            "id": new_id,
            **product_data
        }
        PRODUCTS_DB.append(new_product)
        return new_product

# 5. Đăng ký Blueprint vào API
api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)