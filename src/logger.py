import logging
import os
from datetime import datetime

LOG_FILE = F"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(os.getcwd(), "logs", LOG_FILE)
os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)


logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

if __name__ == '__main__':
    logging.info("Logging started.")