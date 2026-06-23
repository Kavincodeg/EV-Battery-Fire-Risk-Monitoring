import datetime

def log_event(state, risk):
    """
    Log important battery events to CSV
    """
    with open("data/event_log.csv", "a") as f:
        f.write(
            f"{datetime.datetime.now()},"
            f"{state.temperature},"
            f"{state.voltage},"
            f"{state.current},"
            f"{state.capacity},"
            f"{risk}\n"
        )
