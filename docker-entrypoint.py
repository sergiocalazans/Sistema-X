import os
import socket
import time


def wait_for_mysql() -> None:
    host = os.getenv("MYSQL_HOST")
    if not host:
        return

    port = int(os.getenv("MYSQL_PORT", "3306"))
    timeout = int(os.getenv("MYSQL_WAIT_TIMEOUT", "90"))
    deadline = time.monotonic() + timeout

    while True:
        try:
            with socket.create_connection((host, port), timeout=5):
                return
        except OSError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"MySQL is not reachable at {host}:{port}")
            time.sleep(2)


wait_for_mysql()

port = os.getenv("PORT", "5000")
os.execvp(
    "gunicorn",
    [
        "gunicorn",
        "run:app",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        "1",
        "--threads",
        "4",
        "--timeout",
        "120",
    ],
)
