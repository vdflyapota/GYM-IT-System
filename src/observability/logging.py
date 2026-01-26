import logging
from pythonjsonlogger import jsonlogger

def configure_logging(app):
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
