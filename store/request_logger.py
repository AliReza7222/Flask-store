import logging
import time
from logging.handlers import RotatingFileHandler

from flask import g, request

request_logger = logging.getLogger("request_logger")
request_logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "logs/request.log",
    maxBytes=1 * 1024 * 1024,
    backupCount=3,
)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
request_logger.addHandler(handler)


def request_logging(app):
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        if request.path.startswith("/api/"):
            request_logger.info(
                f"START request: {request.method} {request.path} | IP: {request.remote_addr} | "  # noqa: E501, G004
                f"Params: {request.args} | Body: {request.get_data(as_text=True)}",
            )

    @app.after_request
    def log_response_info(response):
        duration = time.time() - g.start_time
        if request.path.startswith("/api/"):
            request_logger.info(
                f"END request: {request.method} {request.path} | IP: {request.remote_addr}  | "  # noqa: E501, G004
                f" Status: {response.status_code} | Duration: {duration:.4f}s ",
            )
        return response
