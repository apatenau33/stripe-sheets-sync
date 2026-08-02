import logging
import time

log = logging.getLogger("sync")


def setup_logging(logfile="sync.log"):
    """Log to both the console and a file the client can send you."""
    formatter = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = logging.FileHandler(logfile, encoding="utf-8")
    file_handler.setFormatter(formatter)

    log.setLevel(logging.INFO)
    log.handlers.clear()
    log.addHandler(console)
    log.addHandler(file_handler)


def with_retries(func, *, description, attempts=4, base_delay=2):
    """Run func(), retrying with exponential backoff if it raises."""
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except Exception as e:
            if attempt == attempts:
                log.error(f"{description} failed after {attempts} attempts: {e}")
                raise
            delay = base_delay ** attempt
            log.warning(
                f"{description} attempt {attempt} failed "
                f"({type(e).__name__}: {e}) - retrying in {delay}s"
            )
            time.sleep(delay)