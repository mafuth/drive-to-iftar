import logging
import logging.handlers
import queue
import sys
from typing import Optional

# Global QueueListener instance
_listener: Optional[logging.handlers.QueueListener] = None

def setup_logging():
    """
    Sets up a non-blocking logger using QueueHandler and QueueListener.
    This should be called at application startup.
    """
    global _listener

    # Create a shared queue for log records
    log_queue = queue.Queue(-1)  # Infinite size

    # Create the QueueHandler (non-blocking)
    queue_handler = logging.handlers.QueueHandler(log_queue)

    # Configure root logger to output to the queue
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Remove existing handlers to avoid duplication if re-initialized
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    root.addHandler(queue_handler)

    # Create the actual handler that will write logs (runs in a separate thread)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Create and start the listener
    _listener = logging.handlers.QueueListener(log_queue, console_handler)
    _listener.start()

def shutdown_logging():
    """
    Stops the log listener.
    This should be called at application shutdown.
    """
    global _listener
    if _listener:
        _listener.stop()
        _listener = None

def get_logger(name: str):
    """
    Returns a logger instance with the given name.
    """
    return logging.getLogger(name)
