from db import init_db
from bot import run_bot


def start():
    init_db()
    run_bot()


if __name__ == "__main__":
    start()
