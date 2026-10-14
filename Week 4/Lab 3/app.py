
from flask import Flask, jsonify
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields
import yaml

app = Flask(__name__)

# 1. Schema Marshmallow
class TaskSchema(Schema):
    id = fields.UUID(dump_only=True)
    title = fields.Str(required=True)
    status = fields.Str(load_default="open")


# 2. Khởi tạo APISpec
spec = APISpec(
    title="Task API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)

# Đăng ký schema để có thể tham chiếu trong OpenAPI
spec.components.schema("Task", schema=TaskSchema)


# 3. API route, định nghĩa tài liệu bằng YAML docstring
@app.get("/tasks")
def list_tasks():
    """
    Lấy danh sách công việc.
    ---
    get:
      tags:
        - tasks
      summary: List all tasks
      responses:
        "200":
          description: Danh sách công việc
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Task"
    """
    return jsonify([]), 200


# Đọc YAML trong docstring và đăng ký route với APISpec

def register_route(path, view_func):
    docstring = view_func.__doc__ or ""
    yaml_text = docstring.split("---", 1)[1]
    operations = yaml.safe_load(yaml_text)

    # Tạo Flask application context
    with app.app_context():
        spec.path(
            path=path,
            operations=operations,
            view=view_func,
        )


register_route("/tasks", list_tasks)


# 4. Endpoint trả về OpenAPI JSON
@app.get("/openapi.json")
def openapi_json():
    return jsonify(spec.to_dict())


# 5. Swagger UI
@app.get("/docs")
def swagger_docs():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Task API - Swagger UI</title>
        <link rel="stylesheet"
          href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js">
        </script>
        <script>
            SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: "#swagger-ui"
            });
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5000)
