import logging
from flask import Flask, Response, json, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProblemError(Exception):
    """Exception đại diện cho lỗi theo chuẩn Problem Details (RFC 7807/9457)."""

    def __init__(
        self,
        status: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        instance: str | None = None,
    ):
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.type = error_type
        self.instance = instance


def create_problem_response(status: int, title: str, detail: str, error_type: str = "about:blank", instance: str | None = None) -> Response:
    """Hàm helper đóng gói body chuẩn application/problem+json."""
    payload = {
        "type": error_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance or request.path,
    }
    return Response(
        response=json.dumps(payload),
        status=status,
        mimetype="application/problem+json",
    )


@app.errorhandler(ProblemError)
def handle_problem_error(err: ProblemError):
    """Bắt các lỗi chủ động raise ProblemError từ mã nguồn."""
    return create_problem_response(
        status=err.status,
        title=err.title,
        detail=err.detail,
        error_type=err.type,
        instance=err.instance,
    )


@app.errorhandler(HTTPException)
def handle_http_exception(err: HTTPException):
    """Fallback cho các lỗi HTTP mặc định của Werkzeug/Flask (404, 405, 400...)."""
    return create_problem_response(
        status=err.code or 500,
        title=err.name,
        detail=err.description or "An HTTP error occurred.",
        error_type="about:blank",
        instance=request.path,
    )


@app.errorhandler(Exception)
def handle_unexpected_exception(err: Exception):
    """Bắt các exception chưa lường trước (Unhandled Exceptions): log chi tiết server-side, trả về 500 trung tính."""
    logger.exception("Unhandled server exception occurred: %s", err)
    return create_problem_response(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred on the server. Please contact support.",
        error_type="about:blank",
        instance=request.path,
    )

@app.route("/resources/<int:resource_id>", methods=["GET"])
def get_resource(resource_id: int):
    database = {1: {"id": 1, "name": "Resource Item 1"}}

    if resource_id not in database:
        raise ProblemError(
            status=404,
            title="Resource Not Found",
            detail=f"Resource with ID '{resource_id}' does not exist.",
            error_type="https://example.com/errors/resource-not-found",
        )

    return {"data": database[resource_id]}, 200


@app.route("/crash", methods=["GET"])
def trigger_unhandled_crash():
    _ = 1 / 0
    return {"message": "Success"}


if __name__ == "__main__":
    app.run(debug=False, port=5000)