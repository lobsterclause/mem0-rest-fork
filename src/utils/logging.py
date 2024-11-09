"""Logging utilities for memory system."""
import logging
import sys

# Configure standard logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Create logger instance
logger = logging.getLogger(__name__)

__all__ = ["logger"]
