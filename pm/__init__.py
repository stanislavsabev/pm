import logging
import os


def setup_logging() -> None:
    """Setup package logging."""
    fmt = "%(asctime)s %(levelname)-8s %(name)s [%(filename)s:%(lineno)d] %(message)s"
    lvl = os.environ.get("LOG_LEVEL", "WARNING")
    logging.basicConfig(level=lvl, format=fmt)
    logger = logging.getLogger("pm")
    logger.setLevel(lvl)
    git_logger = logging.getLogger("git.repo.base")
    git_logger.setLevel("DEBUG")


setup_logging()
