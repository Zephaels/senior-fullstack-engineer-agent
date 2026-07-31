MAX_ATTEMPTS = 3


def should_retry(attempt: int) -> bool:
    return 0 <= attempt < MAX_ATTEMPTS
