import logging
import os

# https://peps.python.org/pep-0440/
# [N!]N(.N)*[{a|b|rc}N][.postN][.devN]
__version__ = "0.1.0"


def setup_logging() -> None:
    """Setup package logging."""
    fmt = "%(asctime)s %(levelname)-8s %(name)s [%(filename)s:%(lineno)d] %(message)s"
    lvl = os.environ.get("LOG_LEVEL", "WARNING")
    logging.basicConfig(level=lvl, format=fmt)
    logger = logging.getLogger("pm")
    logger.setLevel(lvl)
    logging.getLogger("git.repo.base").setLevel("WARNING")


setup_logging()
