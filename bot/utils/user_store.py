import json
import os

STORE_PATH = "data/users.json"


def _load() -> set[int]:
    if not os.path.exists(STORE_PATH):
        return set()
    try:
        with open(STORE_PATH, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def _save(user_ids: set[int]) -> None:
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump(list(user_ids), f)


def register_user(chat_id: int) -> None:
    users = _load()
    if chat_id not in users:
        users.add(chat_id)
        _save(users)


def get_all_users() -> list[int]:
    return list(_load())


def user_count() -> int:
    return len(_load())
