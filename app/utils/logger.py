import logging
import queue
import json
from logging.handlers import QueueHandler, QueueListener

class JsonFormatter(logging.Formatter):
    RESERVED_FIELDS = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
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
    }

    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in self.RESERVED_FIELDS and not key.startswith("_"):
                log_record[key] = value

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)



log_queue = queue.Queue()

queue_handler = QueueHandler(log_queue)

console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())


console_handler.setLevel(logging.DEBUG)


listener = QueueListener(log_queue, console_handler)
listener.start()



def get_logger(name: str = "app"):
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(queue_handler)
        logger.propagate = False

    return logger
