import logging

LOGGER = logging.getLogger(__name__)


def test_logger_differences():
    LOGGER.info("hihi")
    LOGGER.warning("hihi")
    LOGGER.error("hihi")
    LOGGER.debug("hihi")
