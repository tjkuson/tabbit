"""Configuration for the root logger."""

import atexit
import datetime as dt
import functools
import json
import logging
import logging.config
import logging.handlers
import sys
from typing import Final
from typing import final
from typing import override

from tabbit.config.settings import settings
from tabbit.exceptions import TabbitLoggerError

# https://docs.python.org/3/library/logging.html#logrecord-attributes
LOG_RECORD_BUILTIN_ATTRS: Final = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",  # https://docs.python.org/3/library/logging.html#logging.Formatter.format
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


@final
class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter."""

    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.fmt_keys: dict[str, str] = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        additional_fields = {
            "timestamp": dt.datetime.fromtimestamp(
                record.created,
                tz=dt.UTC,
            ).isoformat(),
        }
        msg = {
            key: msg_val
            if (msg_val := additional_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }

        # Inject extras.
        msg.update(
            {
                key: val
                for key, val in record.__dict__.items()
                if key not in LOG_RECORD_BUILTIN_ATTRS
            }
        )

        return json.dumps(msg, default=str)


_logging_config: Final = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "json": {
            "()": JSONFormatter,
            "fmt_keys": {
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "function": "funcName",
                "line": "lineno",
                "thread_name": "threadName",
            },
        },
    },
    "handlers": {
        "stderr": {
            "class": logging.StreamHandler,
            "level": logging.getLevelName(logging.WARNING),
            "formatter": "default",
            "stream": sys.stderr,
        },
        "file_jsonl": {
            "class": logging.handlers.RotatingFileHandler,
            "level": logging.getLevelName(logging.DEBUG),
            "formatter": "json",
            "filename": settings.log_filename,
            "maxBytes": 10000,
            "backupCount": 3,
        },
        "queue_handler": {
            "class": logging.handlers.QueueHandler,
            "handlers": ["stderr", "file_jsonl"],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "root": {
            "level": logging.getLevelName(logging.DEBUG),
            "handlers": ["queue_handler"],
        }
    },
}


@functools.cache
def setup_logging() -> None:
    """Setup and configure application-level logging.

    Create a log file at the configured path if one does not exist
    already.

    Process log handlers on a separate thread for performance and close
    gracefully upon normal interpreter termination.

    Logging is only setup once; subsequent calls to this function return
    immediately.

    Raises:
        TabbitLoggerError: If the queue handler could not be
            initialized.

    Note:
        Call this function early in the application lifecycle, ideally
        during startup.
    """
    if not settings.log_filename.exists():
        settings.log_filename.touch()

    logging.config.dictConfig(_logging_config)

    queue_handler = logging.getHandlerByName("queue_handler")
    if (
        not isinstance(queue_handler, logging.handlers.QueueHandler)
        or queue_handler.listener is None
    ):
        raise TabbitLoggerError("Failed to initialize logging queue handler.")
    queue_handler.listener.start()
    _ = atexit.register(queue_handler.listener.stop)
