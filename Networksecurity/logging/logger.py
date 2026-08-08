import logging
import os
from datetime import datetime


LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"


logs_path = os.path.join(os.getcwd(), "logs", LOG_FILE)


os.makedirs(os.path.dirname(logs_path), exist_ok=True)


LOG_FILE_PATH = logs_path


logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Create a logger object
logger = logging.getLogger(__name__)

print("Logger imported")
print("Log file:", LOG_FILE_PATH)
print("Handlers:", logger.handlers)
print("Has Handlers:", logger.hasHandlers())
logger.info("Logger is working!")