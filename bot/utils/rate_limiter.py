import time

MESSAGE_WINDOW_SECONDS = 10
MESSAGE_THRESHOLD = 12


def record_message(context_user_data: dict) -> bool:
    now = time.time()
    times: list = context_user_data.setdefault("_msg_times", [])
    times.append(now)

    cutoff = now - MESSAGE_WINDOW_SECONDS
    while times and times[0] < cutoff:
        times.pop(0)

    return len(times) >= MESSAGE_THRESHOLD
